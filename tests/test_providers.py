"""Offline provider/pipeline tests. Fixture output is never live extraction evidence."""
from copy import deepcopy
import json
import socket
import sys
import ssl
from types import SimpleNamespace

import jsonschema
import pytest

from makf_knowledge import (
    ExtractionRequest, FixtureProvider, OpenAIProvider, ProviderError,
    SourceDocument, SourcePassage, build_extraction_prompt, extract,
)
from makf_knowledge.cli import run
from makf_knowledge.paths import example_path
from makf_knowledge.providers import openai_response_schema


@pytest.fixture(autouse=True)
def prohibit_network(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail('Default tests must never call a live service')
    monkeypatch.setattr(socket.socket, 'connect', fail)
    monkeypatch.setattr(socket, 'create_connection', fail)


@pytest.fixture
def example():
    batch = json.loads(example_path('pouring').read_text())
    batch.pop('extraction_run')
    for component in batch['candidates'][0]['components']:
        if component['component_kind'] == 'hypothesis':
            component['ontology_class'] = 'paf:PouringCausalHypothesis'
        elif component['component_kind'] == 'predicted_effect':
            component['ontology_class'] = 'makf:PredictedEffectPattern'
    doc = batch['documents'][0]
    document = SourceDocument(doc['document_id'], doc['title'], doc['synthetic_demo'],
                              tuple(SourcePassage(**p) for p in doc['passages']))
    return ExtractionRequest(batch['batch_id'], (document,)), batch


def completion(content, *, finish='stop', refusal=None):
    return SimpleNamespace(model='test-model-snapshot', id='test-response', _request_id='test-request',
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=200, total_tokens=300),
        choices=[SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content=content, refusal=refusal))])


class Client:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls = response, error, []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


def nullable_wire(value, schema, definitions):
    if '$ref' in schema:
        schema = definitions[schema['$ref'].rsplit('/', 1)[-1]]
    if isinstance(value, list):
        return [nullable_wire(v, schema['items'], definitions) for v in value]
    if isinstance(value, dict):
        return {key: nullable_wire(value[key], field, definitions) if key in value else None
                for key, field in schema['properties'].items()}
    return value


def wire_batch(batch, prompt):
    return {'result': nullable_wire(batch, {'$ref': '#/$defs/ExtractionBatch'}, prompt.response_schema['$defs'])}


def test_strict_schema_has_required_nullable_optionals_without_changing_e1(example):
    request, batch = example
    prompt = build_extraction_prompt(request)
    original = deepcopy(prompt.response_schema)
    wire_schema = openai_response_schema(prompt)
    jsonschema.Draft202012Validator.check_schema(wire_schema)
    check = jsonschema.Draft202012Validator(wire_schema)
    check.validate(wire_batch(batch, prompt))
    check.validate({'result': {'abstained': True, 'reason': 'No supported claim'}})
    assert prompt.response_schema == original

    def check_nodes(node):
        if not isinstance(node, dict):
            return
        if node.get('type') == 'object':
            assert set(node['required']) == set(node['properties'])
            assert node['additionalProperties'] is False
        assert not ({'oneOf', 'const', 'minLength', 'minItems', 'format'} & node.keys())
        for child in node.values():
            if isinstance(child, dict):
                check_nodes(child)
            elif isinstance(child, list):
                for item in child:
                    check_nodes(item)
    check_nodes(wire_schema)


def test_openai_wire_request_and_end_to_end_validation(example, tmp_path):
    request, batch = example
    prompt = build_extraction_prompt(request)
    raw = json.dumps(wire_batch(batch, prompt))
    client = Client(completion(raw))
    provider = OpenAIProvider('explicit-model', client=client, max_output_tokens=2048)
    result = extract(request, provider)
    assert len(client.calls) == 1
    sent = client.calls[0]
    assert sent['model'] == 'explicit-model'
    assert sent['store'] is False
    assert sent['max_completion_tokens'] == 2048
    assert sent['response_format']['json_schema']['strict'] is True
    assert sent['messages'][1]['content'] == prompt.messages[1].content
    assert 'TRANSPORT FORMAT' in sent['messages'][0]['content']
    assert result.report['status'] == 'provisional'
    assert result.report['provider']['model_name'] == 'test-model-snapshot'
    assert result.report['provider']['usage']['total_tokens'] == 300
    assert result.batch['documents'] == batch['documents']
    assert result.batch['candidates'] == batch['candidates']
    assert result.batch['extraction_run']['engine'] == 'openai'
    assert result.raw_response == raw
    target = tmp_path / 'run'
    result.save(target)
    assert (target / 'response.txt').read_text() == raw
    assert json.loads((target / 'transport-request.json').read_text()) == sent
    assert json.loads((target / 'report.json').read_text())['human_review_required'] is True
    with pytest.raises(FileExistsError):
        result.save(target)


@pytest.mark.parametrize('action', ['pouring', 'grasping'])
def test_fixture_transport_reuses_profiles(action):
    batch = json.loads(example_path(action).read_text())
    batch.pop('extraction_run')
    for component in batch['candidates'][0]['components']:
        if component['component_kind'] == 'predicted_effect':
            component['ontology_class'] = 'makf:PredictedEffectPattern'
        if action == 'pouring' and component['component_kind'] == 'hypothesis':
            component['ontology_class'] = 'paf:PouringCausalHypothesis'
    doc = batch['documents'][0]
    request = ExtractionRequest(batch['batch_id'], (SourceDocument(
        doc['document_id'], doc['title'], True, tuple(SourcePassage(**p) for p in doc['passages'])),), action)
    result = extract(request, FixtureProvider(json.dumps(batch)))
    assert result.report['status'] == 'provisional'
    assert result.report['provider']['live'] is False
    assert result.batch['extraction_run']['engine'] == 'offline_fixture'


@pytest.mark.parametrize('raw', ['{"candidates":', '{} trailing', '{"x":1,"x":2}', '{"x": NaN}'])
def test_invalid_json_quarantined_verbatim(example, raw, tmp_path):
    result = extract(example[0], FixtureProvider(raw))
    assert result.report['status'] == 'quarantined'
    assert result.batch is None
    result.save(tmp_path / 'run')
    assert (tmp_path / 'run/quarantined-response.txt').read_text() == raw
    assert not (tmp_path / 'run/candidates.json').exists()


@pytest.mark.parametrize('attack', [
    'changed_source', 'changed_synthetic', 'missing_epistemic', 'world_instance',
    'invented_quote', 'offset_overrun', 'unoffered_class', 'invented_property',
    'generated_attribution', 'necessary_hypothesis', 'fake_audit', 'wrong_profile',
])
def test_adversarial_outputs_quarantined(example, attack):
    request, batch = example
    candidate = batch['candidates'][0]
    if attack == 'changed_source':
        batch['documents'][0]['passages'][0]['text'] = 'Fabricated evidence.'
    elif attack == 'changed_synthetic':
        batch['documents'][0]['synthetic_demo'] = False
    elif attack == 'missing_epistemic':
        candidate.pop('epistemic_status')
    elif attack == 'world_instance':
        candidate['robot_id'] = 'robot-1'
    elif attack == 'invented_quote':
        candidate['source_support'][0]['exact_quote'] = 'This does not occur in the source.'
    elif attack == 'offset_overrun':
        candidate['source_support'][0]['end_char'] = 100000
    elif attack == 'unoffered_class':
        candidate['components'][0]['ontology_class'] = 'paf:OrientationInducedEffluxHypothesis'
    elif attack == 'invented_property':
        candidate['structural_links'][0]['predicate_curie'] = 'makf:ProvenPhysicalCause'
    elif attack == 'generated_attribution':
        candidate.update(derivation_mode='llm_proposal', evidence_status='not_assessed')
    elif attack == 'necessary_hypothesis':
        candidate['modality'] = 'necessary'
    elif attack == 'fake_audit':
        batch['extraction_run'] = {'engine': 'invented-peer-review'}
    elif attack == 'wrong_profile':
        batch['profile_id'] = 'wrong-profile'
    result = extract(request, FixtureProvider(json.dumps(batch)))
    assert result.report['status'] == 'quarantined'
    assert result.batch is None


def test_generated_hypothesis_can_remain_unassessed_with_context_only_support(example):
    request, batch = example
    candidate = batch['candidates'][0]
    candidate.update(derivation_mode='llm_proposal', evidence_status='not_assessed', modality='speculative')
    candidate['source_support'][0]['support_role'] = 'context_only'
    result = extract(request, FixtureProvider(json.dumps(batch)))
    assert result.report['status'] == 'provisional'
    assert result.batch['candidates'][0]['evidence_status'] == 'not_assessed'


@pytest.mark.parametrize('openai', [False, True])
def test_abstention_is_not_an_extracted_batch(example, openai):
    response = {'abstained': True, 'reason': 'No relevant claim.'}
    provider = (OpenAIProvider('test', client=Client(completion(json.dumps({'result': response}))))
                if openai else FixtureProvider(json.dumps(response)))
    result = extract(example[0], provider)
    assert result.report['status'] == 'abstained'
    assert result.batch is None


@pytest.mark.parametrize('response,expected', [
    (completion('{}', refusal='Refusal content'), 'refused'),
    (completion('{', finish='length'), 'incomplete'),
    (completion(None, finish='content_filter'), 'incomplete'),
    (completion(''), 'empty_response'),
])
def test_refusal_and_incomplete_output_not_accepted(example, response, expected):
    client = Client(response)
    result = extract(example[0], OpenAIProvider('test', client=client))
    assert result.report['error_code'] == expected
    assert result.report['status'] in {'refused', 'provider_error'}
    assert result.batch is None
    assert len(client.calls) == 1


def test_transport_error_is_sanitized_and_not_retried(example):
    error = RuntimeError('secret-key-and-private-source-must-not-leak')
    error.status_code = 401
    client = Client(error=error)
    result = extract(example[0], OpenAIProvider('test', client=client))
    assert result.report['status'] == 'provider_error'
    assert result.report['provider']['http_status'] == 401
    assert 'secret-key' not in json.dumps(result.report)
    assert len(client.calls) == 1


def test_missing_credential_has_no_fallback_network(monkeypatch):
    monkeypatch.delenv('MAKF_OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(ProviderError, match='securely'):
        OpenAIProvider('explicit-model')


def test_client_uses_official_endpoint_verified_tls_and_no_retries(monkeypatch):
    captured = {}
    def client(**kwargs):
        captured.update(kwargs)
        return Client()
    monkeypatch.setitem(sys.modules, 'openai', SimpleNamespace(
        OpenAI=client, DefaultHttpxClient=lambda **kwargs: kwargs))
    monkeypatch.setenv('MAKF_OPENAI_API_KEY', 'test-only-sentinel')
    monkeypatch.setenv('OPENAI_BASE_URL', 'https://untrusted.invalid')
    provider = OpenAIProvider('explicit-model', timeout=15)
    assert captured['base_url'] == 'https://api.openai.com/v1'
    assert captured['max_retries'] == 0
    assert captured['timeout'] == 15
    assert captured['api_key'] == 'test-only-sentinel'
    context = captured['http_client']['verify']
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    assert 'test-only-sentinel' not in repr(provider.audit)


def test_optional_sdk_not_needed_for_package_import():
    import subprocess
    code = '''
import sys
sys.modules['openai'] = None
import makf_knowledge
assert makf_knowledge.FixtureProvider('{}').audit['live'] is False
'''
    subprocess.run([sys.executable, '-c', code], check=True)


def test_real_sdk_serialization_with_offline_http_transport(example):
    openai = pytest.importorskip('openai', reason='Optional SDK integration test; install .[openai]')
    httpx = pytest.importorskip('httpx')
    request, batch = example
    prompt = build_extraction_prompt(request)
    raw = json.dumps(wire_batch(batch, prompt))
    calls = []
    def handler(http_request):
        calls.append(json.loads(http_request.content))
        assert str(http_request.url) == 'https://api.openai.com/v1/chat/completions'
        return httpx.Response(200, json={
            'id': 'test-offline-response', 'object': 'chat.completion', 'created': 0,
            'model': 'test-offline-model',
            'choices': [{'index': 0, 'finish_reason': 'stop',
                         'message': {'role': 'assistant', 'content': raw, 'refusal': None}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
        }, headers={'x-request-id': 'test-offline-request'})
    with openai.OpenAI(api_key='test-only-sentinel', base_url='https://api.openai.com/v1',
                       http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
        result = extract(request, OpenAIProvider('explicit-model', client=client))
    assert result.report['status'] == 'provisional'
    assert result.report['provider']['request_id'] == 'test-offline-request'
    assert len(calls) == 1


def test_fixture_cli_artifacts_and_failure_exit(example, tmp_path, capsys):
    request, batch = example
    source = tmp_path / 'source.txt'
    source.write_text(request.documents[0].passages[0].text)
    fixture = tmp_path / 'fixture.json'
    fixture.write_text(json.dumps(batch))
    args = ['extract', '--provider', 'fixture', '--fixture-file', str(fixture),
            '--text-file', str(source), '--source-id', request.documents[0].document_id,
            '--source-title', request.documents[0].title, '--synthetic-demo',
            '--passage-id', request.documents[0].passages[0].passage_id, '--batch-id', request.batch_id]
    assert run(args + ['--out-dir', str(tmp_path / 'good')]) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'provisional'
    assert run(args + ['--out-dir', str(tmp_path / 'good')]) == 1
    assert 'existing runs' in capsys.readouterr().err
    fixture.write_text('bad JSON')
    assert run(args + ['--out-dir', str(tmp_path / 'bad')]) == 1
    assert json.loads(capsys.readouterr().out)['status'] == 'quarantined'
