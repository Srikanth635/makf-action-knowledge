"""Opt-in model IO and deterministic fixture transport. No IO occurs on import."""
from copy import deepcopy
from dataclasses import asdict
import os
import hashlib
import json
import ssl
from typing import Any

from .extraction import ExtractionPrompt

OPENAI_WIRE_FORMAT = 'openai-strict-v1'


class ProviderError(RuntimeError):
    """Sanitized transport failure; never includes credentials or response bodies."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def openai_response_schema(prompt: ExtractionPrompt) -> dict:
    """Adapt E1 to OpenAI strict output: object root, required nullable optionals.

    Length/format constraints and document const are checked locally against the
    original schema. No constraint is removed from the canonical E1 contract.
    """
    def adapt(node):
        if not isinstance(node, dict):
            return node
        result = {k: deepcopy(v) for k, v in node.items()
                  if k not in {'$schema', '$id', 'title', 'minLength', 'minItems', 'format', 'const'}}
        if 'const' in node and not isinstance(node['const'], (dict, list)):
            result['enum'] = [node['const']]
            if 'type' not in result:
                result['type'] = 'boolean' if isinstance(node['const'], bool) else 'string'
        if 'oneOf' in result:
            result['anyOf'] = result.pop('oneOf')
        for key in ('anyOf', 'allOf'):
            if key in result:
                result[key] = [adapt(item) for item in result[key]]
        if '$defs' in result:
            result['$defs'] = {k: adapt(v) for k, v in result['$defs'].items()}
        if 'items' in result:
            result['items'] = adapt(result['items'])
        if 'properties' in result:
            required = node.get('required', [])
            result['properties'] = {
                key: adapt(value) if key in required else {'anyOf': [adapt(value), {'type': 'null'}]}
                for key, value in node['properties'].items()
            }
            result['required'] = list(result['properties'])
            result['additionalProperties'] = False
        return result

    schema = adapt(prompt.response_schema)
    return {'type': 'object', '$defs': schema.pop('$defs'),
            'properties': {'result': schema}, 'required': ['result'], 'additionalProperties': False}


class FixtureProvider:
    """Return explicitly supplied offline text; never presented as model extraction."""

    wire_format = 'e1'

    def __init__(self, response: str):
        self.response = response
        self.audit = {'engine': 'offline_fixture', 'live': False}

    def generate(self, prompt: ExtractionPrompt) -> str:
        return self.response


class OpenAIProvider:
    """Single bounded Chat Completions request to the official OpenAI endpoint.

    SDK import and credentials are needed only when this adapter is instantiated.
    A client can be injected for offline transport tests. No automatic repair or
    retry calls are made; the raw model JSON is returned for separate validation.
    """

    wire_format = OPENAI_WIRE_FORMAT

    def __init__(self, model: str, *, api_key_env: str = 'MAKF_OPENAI_API_KEY',
                 max_output_tokens: int = 6000, timeout: float = 60.0, client: Any = None):
        if not isinstance(model, str) or not model.strip():
            raise ValueError('An explicit OpenAI model is required')
        if type(max_output_tokens) is not int or not 1 <= max_output_tokens <= 16000:
            raise ValueError('max_output_tokens must be between 1 and 16000')
        if not 0 < timeout <= 300:
            raise ValueError('timeout must be between 0 and 300 seconds')
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.audit = {'engine': 'openai', 'requested_model': model, 'live': True}
        self.request_payload = None
        self._owns_client = client is None
        if client is None:
            key = os.environ.get(api_key_env)
            if not key and api_key_env == 'MAKF_OPENAI_API_KEY':
                key = os.environ.get('OPENAI_API_KEY')
            if not key:
                raise ProviderError('missing_credential', f'Set {api_key_env} securely before using OpenAI')
            try:
                from openai import OpenAI, DefaultHttpxClient
            except ImportError:
                raise ProviderError('missing_dependency', 'Install makf-action-knowledge[openai]') from None
            client = OpenAI(api_key=key, base_url='https://api.openai.com/v1',
                            max_retries=0, timeout=timeout,
                            http_client=DefaultHttpxClient(verify=ssl.create_default_context()))
        self.client = client

    def generate(self, prompt: ExtractionPrompt) -> str:
        self.audit = {'engine': 'openai', 'requested_model': self.model, 'live': True}
        messages = [asdict(message) for message in prompt.messages]
        messages[0]['content'] += (
            '\nTRANSPORT FORMAT\nWrap the E1 batch or abstention in {"result": ...}. '
            'For optional fields required by the transport schema, use null when absent. '
            'Set extraction_run=null; audit metadata is recorded by the caller. '
            'Extract at most three candidates for this bounded pilot. Cover distinct '
            'perspectives only when justified by the passage; do not force coverage.'
        )
        self.request_payload = dict(model=self.model, messages=messages, store=False,
            max_completion_tokens=self.max_output_tokens,
            response_format={'type': 'json_schema', 'json_schema': {
                'name': 'makf_extraction', 'strict': True, 'schema': openai_response_schema(prompt)}})
        self.audit['wire_request_sha256'] = hashlib.sha256(json.dumps(
            self.request_payload, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        try:
            response = self.client.chat.completions.create(**self.request_payload)
        except Exception as exc:
            status = getattr(exc, 'status_code', None)
            if isinstance(status, int):
                self.audit['http_status'] = status
            code = 'api_error' if status is not None else 'connection_error'
            raise ProviderError(code, f'OpenAI request failed ({code}' +
                                (f', HTTP {status}' if status is not None else '') + ')') from None
        self.audit.update(model_name=response.model, response_id=response.id,
                          request_id=getattr(response, '_request_id', None))
        usage = getattr(response, 'usage', None)
        if usage is not None:
            self.audit['usage'] = {key: getattr(usage, key, None)
                                   for key in ('prompt_tokens', 'completion_tokens', 'total_tokens')}
        if len(response.choices) != 1:
            raise ProviderError('invalid_response', 'OpenAI returned an unexpected choice count')
        choice = response.choices[0]
        self.audit['finish_reason'] = choice.finish_reason
        if getattr(choice.message, 'refusal', None):
            raise ProviderError('refused', 'OpenAI refused the extraction request')
        if choice.finish_reason != 'stop':
            raise ProviderError('incomplete', 'OpenAI output was incomplete or filtered')
        if not isinstance(choice.message.content, str) or not choice.message.content.strip():
            raise ProviderError('empty_response', 'OpenAI returned no extraction text')
        return choice.message.content

    def close(self) -> None:
        if self._owns_client:
            self.client.close()
