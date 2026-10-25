"""Minimal end-to-end runner: transport, strict parsing, validation and quarantine.

Semantic acceptance is mechanical and provisional, never scientific verification.
Raw output is retained. No repair loop, ontology write, or partial acceptance occurs.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import jsonschema

from .extraction import ExtractionProvider, ExtractionRequest, build_extraction_prompt
from .guidance import load_profile
from .paths import RESOURCE_ROOT, profile_path
from .providers import OPENAI_WIRE_FORMAT, ProviderError, evidence_catalog, openai_response_schema
from .validation import SemanticValidator, ValidationError


def _parse_json(text: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError('Non-finite JSON number')

    return json.loads(text, object_pairs_hook=unique, parse_constant=reject_constant)


def _remove_optional_nulls(value, schema, definitions):
    """Normalize only documented nullable optional transport fields, never values."""
    if '$ref' in schema:
        schema = definitions[schema['$ref'].rsplit('/', 1)[-1]]
    if isinstance(value, list):
        return [_remove_optional_nulls(v, schema['items'], definitions) for v in value]
    if isinstance(value, dict):
        return {key: _remove_optional_nulls(v, schema['properties'][key], definitions)
                for key, v in value.items()
                if v is not None or key in schema.get('required', [])}
    return value


def _check_schema(data, schema, label):
    errors = list(jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()).iter_errors(data))
    if errors:
        # Report locations and constraint names, never source values or excerpts.
        # For the batch/abstention union, prefer errors from the intended branch.
        if 'oneOf' in schema and isinstance(data, dict):
            branch = schema['oneOf'][1 if data.get('abstained') is True else 0]
            errors = list(jsonschema.Draft202012Validator(
                {'$defs': schema['$defs'], **branch},
                format_checker=jsonschema.FormatChecker()).iter_errors(data)) or errors
        details = '; '.join(
            f'{"/".join(map(str, e.absolute_path)) or "<root>"} ({e.validator})'
            for e in errors[:8])
        raise ValidationError(f'{label} validation failed: {details}')


@dataclass
class ExtractionResult:
    report: dict
    prompt: dict
    raw_response: str | None = None
    batch: dict | None = None
    transport_request: dict | None = None

    def save(self, directory: str | Path) -> None:
        """Write a new private run directory; refuse to overwrite previous results."""
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=False, mode=0o700)

        def write(name, value):
            path = target / name
            with path.open('x', encoding='utf-8') as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write('\n')

        write('prompt.json', self.prompt)
        write('report.json', self.report)
        if self.transport_request is not None:
            write('transport-request.json', self.transport_request)
        if self.raw_response is not None:
            name = 'quarantined-response.txt' if self.report['status'] == 'quarantined' else 'response.txt'
            (target / name).write_bytes(self.raw_response.encode('utf-8'))
        if self.batch is not None:
            write('candidates.json', self.batch)


def extract(request: ExtractionRequest, provider: ExtractionProvider, *, root=RESOURCE_ROOT) -> ExtractionResult:
    """Execute one explicitly selected provider and retain a complete local audit.

    Request errors raise before any provider call. Failed generations are reported
    as provider_error/refused; invalid output is quarantined; accepted batches are
    provisional. The caller decides where to persist the resulting artifacts.
    """
    prompt = build_extraction_prompt(request, root=root)
    # Preserve the trusted contract even if an adapter mutates its input object.
    artifact = prompt.to_dict()
    report = {'status': 'pending', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'prompt_version': prompt.prompt_version, 'source_sha256': prompt.source_sha256,
              'prompt_sha256': hashlib.sha256(json.dumps(artifact, sort_keys=True,
                  ensure_ascii=False).encode('utf-8')).hexdigest(),
              'scope': 'Mechanical validation only; scientific support and generalization need review.'}
    result = ExtractionResult(report=report, prompt=artifact)
    try:
        result.raw_response = provider.generate(deepcopy(prompt))
    except ProviderError as exc:
        report.update(status='refused' if exc.code == 'refused' else 'provider_error', error_code=exc.code)
        report['provider'] = deepcopy(getattr(provider, 'audit', {'engine': type(provider).__name__}))
        result.transport_request = deepcopy(getattr(provider, 'request_payload', None))
        return result
    report['provider'] = deepcopy(getattr(provider, 'audit', {'engine': type(provider).__name__}))
    result.transport_request = deepcopy(getattr(provider, 'request_payload', None))
    try:
        if not isinstance(result.raw_response, str):
            result.raw_response = None
            raise ValidationError('Provider response must be text')
        report['response_sha256'] = hashlib.sha256(result.raw_response.encode('utf-8')).hexdigest()
        data = _parse_json(result.raw_response)
        wire_format = getattr(provider, 'wire_format', 'e1')
        if wire_format == OPENAI_WIRE_FORMAT:
            _check_schema(data, openai_response_schema(prompt), 'Transport schema')
            data = data['result']
            if 'abstained' not in data:
                catalog = evidence_catalog(prompt)
                for candidate in data['candidates']:
                    for support in candidate['source_support']:
                        support['exact_quote'] = catalog[support.pop('quote_id')]
                data = _remove_optional_nulls(data, {'$ref': '#/$defs/ExtractionBatch'},
                                              prompt.response_schema['$defs'])
        elif wire_format != 'e1':
            raise ValidationError('Unknown provider wire format')
        _check_schema(data, prompt.response_schema, 'Request-bound E1 schema')
        if data.get('abstained') is True:
            if not data['reason'].strip():
                raise ValidationError('Abstention reason must be nonempty')
            report.update(status='abstained', reason=data['reason'])
            return result
        if 'extraction_run' in data:
            raise ValidationError('Provider must not author extraction_run audit metadata')
        validator = SemanticValidator(root)
        path = (Path(root) / 'profiles' / profile_path(request.profile).name
                if request.profile in ('pouring', 'grasping') else Path(request.profile))
        profile = load_profile(path, validator)
        validation = validator.validate_batch(data, profile)
        context = json.loads(prompt.messages[1].content)['ontology_context']
        classes = {entry['curie'] for entries in context['perspectives'].values() for entry in entries}
        classes.update(entry['curie'] for entry in context['shared_description_classes'])
        properties = {entry['curie'] for entry in context['allowed_properties']}
        for candidate in data['candidates']:
            if candidate['evidence_status'] == 'corroborated':
                raise ValidationError('Extraction alone cannot establish corroboration')
            if candidate['derivation_mode'] in {'llm_inference', 'llm_proposal'}:
                if (candidate['evidence_status'] != 'not_assessed' or
                        any(s['support_role'] != 'context_only' for s in candidate['source_support'])):
                    raise ValidationError('Generated ideas require unassessed context-only support')
            if any(c.get('ontology_class') not in classes for c in candidate['components']
                   if c['grounding_status'] == 'grounded'):
                raise ValidationError('Grounded class was not offered in the prompt context')
            if any(link['predicate_curie'] not in properties for link in candidate.get('structural_links', [])):
                raise ValidationError('Structural property was not offered in the prompt context')
            for support in candidate['source_support']:
                if not support['exact_quote'].strip():
                    raise ValidationError('Evidence quote must contain non-whitespace text')
                if 'end_char' in support:
                    document = next(d for d in data['documents'] if d['document_id'] == support['document_id'])
                    passage = next(p for p in document['passages'] if p['passage_id'] == support['passage_id'])
                    if support['end_char'] > len(passage['text']):
                        raise ValidationError('Evidence offsets extend beyond the passage')
        audit = {'engine': report['provider']['engine'], 'prompt_version': prompt.prompt_version,
                 'recorded_at': report['recorded_at']}
        if report['provider'].get('model_name'):
            audit['model_name'] = report['provider']['model_name']
        data['extraction_run'] = audit
        result.batch = data
        report.update(status='provisional', validation=validation, candidate_count=len(data['candidates']),
                      perspectives=sorted({p for c in data['candidates'] for p in c['perspectives']}),
                      human_review_required=True)
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        report.update(status='quarantined', error_code='invalid_output',
                      error=str(exc) if isinstance(exc, ValidationError) else 'Invalid JSON or response structure')
    return result
