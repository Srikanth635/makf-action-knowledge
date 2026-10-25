"""Offline scalar evidence validation. Source attribution is not physical truth."""
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import re

import jsonschema

from .paths import resource_path
from .validation import ValidationError

# Deliberately bounded conversion registry: no guessed scales or fluid-property units.
UNITS = {'s': ('time', Decimal('1')), 'ms': ('time', Decimal('0.001')),
         'count': ('count', Decimal('1')), '1': ('fraction', Decimal('1')),
         '%': ('fraction', Decimal('0.01'))}
UNIT_LABELS = {'s': {'s', 'second', 'seconds'}, 'ms': {'ms', 'millisecond', 'milliseconds'},
               'count': {'count', 'counts', 'particle', 'particles', 'substep', 'substeps'},
               '1': {'dimensionless', 'fraction', 'ratio'}, '%': {'%', 'percent', 'percentage'}}
DIMENSIONS = {'time_step': 'time', 'substep_duration': 'time', 'duration': 'time',
              'observed_particle_count': 'count', 'total_particle_count': 'count',
              'substep_count': 'count', 'success_fraction': 'fraction',
              'volume_fraction': 'fraction', 'mass_fraction': 'fraction'}


def _decimal(text: str) -> Decimal:
    try:
        value = Decimal(text)
        if not value.is_finite() or (value and abs(value.adjusted()) > 300):
            raise ValueError()
        return value
    except (InvalidOperation, ValueError):
        raise ValidationError('Quantity must be a bounded finite decimal') from None


def _index(records: list[dict], key: str) -> dict:
    result = {r[key]: r for r in records}
    if len(result) != len(records):
        raise ValidationError(f'Duplicate {key}')
    return result


def validate_quantitative(data: dict) -> dict:
    """Return derived issues/eligibility without changing any reported evidence.

    Missing units and source conflicts are valid archival states. Structurally
    malformed evidence and unsupported derivations fail validation. Comparison
    readiness describes prerequisites, not compatibility with arbitrary studies.
    Execution is deliberately unsupported in this archival contract version.
    """
    schema = json.loads(resource_path('quantitative', 'schema.json').read_text())
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(data))
    if errors:
        raise ValidationError('Quantitative schema: ' + '/'.join(map(str, errors[0].absolute_path))
                              + f' ({errors[0].validator})')
    artifacts = _index(data['artifacts'], 'artifact_id')
    quantities = _index(data['quantities'], 'quantity_id')
    _index(data['conversions'], 'conversion_id')
    _index(data['timing_checks'], 'check_id')
    _index(data['issues'], 'issue_id')
    for artifact in artifacts.values():
        if hashlib.sha256(artifact['text'].encode('utf-8')).hexdigest() != artifact['sha256']:
            raise ValidationError('Artifact hash does not match preserved text')

    def anchors(items):
        for anchor in items:
            artifact = artifacts.get(anchor['artifact_id'])
            if artifact is None or anchor['exact_quote'] not in artifact['text']:
                raise ValidationError('Unknown artifact or non-verbatim evidence quote')
        return '\n'.join(a['exact_quote'] for a in items)

    context = data['study']['context']
    anchors(context['evidence'])
    simulator = data['study']['simulator']
    if (simulator['version_status'] == 'reported') != ('version' in simulator):
        raise ValidationError('Simulator version presence must match version_status')
    issues, readiness, values = [], {}, {}

    def issue(code, ids, message):
        issues.append({'code': code, 'quantity_ids': ids, 'message': message})

    for qid, q in quantities.items():
        quote = anchors(q['evidence'])
        value = _decimal(q['reported_value_text'])
        # Preserve exact source spelling (2e-3 remains 2e-3, not a silent 0.002).
        if not re.search(r'(?<![\w.+-])' + re.escape(q['reported_value_text']) + r'(?![\w.])', quote):
            raise ValidationError('Reported numeric spelling is absent from cited evidence')
        kind, unit = q['quantity_kind'], q['unit']
        status, symbol = unit['status'], unit.get('symbol')
        if status in {'unreported', 'unresolved'}:
            if 'symbol' in unit or 'reported_text' in unit:
                raise ValidationError('Unknown units cannot include an invented unit symbol')
        elif status == 'dimensionless':
            if symbol != '1' or not unit.get('reported_text') or unit['reported_text'] not in quote:
                raise ValidationError('Dimensionless status requires explicit source support and symbol 1')
        elif not symbol or not unit.get('reported_text') or unit['reported_text'] not in quote:
            raise ValidationError('Explicit/simulation units require cited reported unit text')
        if symbol in UNIT_LABELS and unit.get('reported_text', '').strip().casefold() not in UNIT_LABELS[symbol]:
            raise ValidationError('Canonical unit symbol disagrees with reported unit label')
        dimension = DIMENSIONS.get(kind)
        if symbol in UNITS and dimension != UNITS[symbol][0]:
            raise ValidationError('Quantity kind and unit dimensions disagree')
        known = status in {'explicit', 'dimensionless'} and symbol in UNITS and dimension is not None
        if dimension == 'count' and (value < 0 or value != value.to_integral_value()):
            raise ValidationError('Counts must be nonnegative integers')
        if kind == 'substep_count' and value <= 0:
            raise ValidationError('Substep count must be positive')
        if dimension == 'time' and value <= 0:
            raise ValidationError('Time durations must be positive')
        if kind == 'reported_density_parameter' and value <= 0:
            raise ValidationError('Reported density parameter must be positive')
        if dimension == 'fraction':
            if 'denominator' not in q or 'metric_definition' not in q:
                raise ValidationError('Fraction metrics require definition and denominator')
            limit = Decimal(100) if symbol == '%' else Decimal(1)
            if known and not Decimal(0) <= value <= limit:
                raise ValidationError('Fraction/percentage is outside its physical range')
        if q['role'] == 'result' and 'metric_definition' not in q:
            raise ValidationError('Results require a metric definition')
        values[qid] = value
        readiness[qid] = {'storage_eligible': True, 'unit_conversion_eligible': known,
                          'comparison_ready': known and context['status'] == 'complete',
                          'execution_eligible': False}
        if not known:
            issue('units_unresolved', [qid], 'No validated physical-unit conversion is available.')

    for supplied in data['issues']:
        if any(q not in quantities for q in supplied['quantity_ids']):
            raise ValidationError('Issue references unknown quantity')
        anchors(supplied['evidence'])
        issue(supplied['code'], supplied['quantity_ids'], supplied['message'])

    calculations = []
    with localcontext() as ctx:
        ctx.prec = 400
        for check in data['timing_checks']:
            ids = [check[k] for k in ('step_id', 'count_id', 'substep_id')]
            if any(q not in quantities for q in ids):
                raise ValidationError('Timing check references unknown quantity')
            if [quantities[q]['quantity_kind'] for q in ids] != ['time_step', 'substep_count', 'substep_duration']:
                raise ValidationError('Timing check requires step, substep count and substep duration')
            if not all(readiness[q]['unit_conversion_eligible'] for q in ids):
                issue('timing_unresolved', ids, 'Timing check needs known compatible units.')
                continue
            step, count, substep = [values[q] * UNITS[quantities[q]['unit']['symbol']][1] for q in ids]
            calculated = count * substep
            calculations.append({'check_id': check['check_id'], 'method': 'count_times_substep_v1',
                'input_ids': ids, 'reported_step_seconds': str(step),
                'calculated_step_seconds': str(calculated), 'consistent': step == calculated})
            if step != calculated:
                issue('timing_conflict', ids, 'Reported step differs from count times substep; no value was corrected.')

        conversions = []
        for conversion in data['conversions']:
            qid = conversion['input_id']
            if qid not in quantities or not readiness[qid]['unit_conversion_eligible']:
                raise ValidationError('Conversion requires a known-unit input quantity')
            source, target = quantities[qid]['unit']['symbol'], conversion['target_unit']
            if target not in UNITS or UNITS[source][0] != UNITS[target][0]:
                raise ValidationError('Unsupported or dimensionally incompatible conversion')
            computed = values[qid] * UNITS[source][1] / UNITS[target][1]
            if computed != _decimal(conversion['derived_value_text']):
                raise ValidationError('Derived conversion value is incorrect')
            conversions.append({**conversion, 'computed_value': str(computed), 'source_unit': source})

    if context['status'] != 'complete':
        issue('context_incomplete', list(quantities), 'Study context is incomplete for controlled comparison.')
    for item in issues:
        for qid in item['quantity_ids']:
            readiness[qid]['comparison_ready'] = False
    return {'status': 'PASS', 'schema_version': '0.1', 'study_id': data['study']['study_id'],
            'quantity_count': len(quantities), 'annex_record_count': len({q['annex_record_id'] for q in quantities.values()}),
            'storage_eligible': True, 'comparison_ready': all(r['comparison_ready'] for r in readiness.values()),
            'execution_eligible': False, 'execution_reason': 'Archival scalar contract; no executable configuration validation.',
            'quantities': readiness, 'issues': issues, 'calculations': calculations, 'conversions': conversions,
            'scope': 'Structural/numeric evidence checks; not source entailment, scientific approval or simulator reproduction.'}
