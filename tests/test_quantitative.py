"""Archival quantities, unit conversion and adversarial numerical/provenance checks."""
from copy import deepcopy
import hashlib
import json

import pytest
from makf_knowledge.cli import run
from makf_knowledge.paths import resource_path
from makf_knowledge.quantitative import validate_quantitative
from makf_knowledge.validation import ValidationError

@pytest.fixture
def data():
    return json.loads(resource_path('quantitative','fluidlab.json').read_text())


def test_all_four_annex_records_store_without_erasing_conflicts(data):
    before=deepcopy(data)
    report=validate_quantitative(data)
    assert data==before
    assert report['storage_eligible'] and report['quantity_count']==10 and report['annex_record_count']==4
    assert not report['comparison_ready'] and not report['execution_eligible']
    assert sum(i['code']=='units_unresolved' for i in report['issues'])==6
    assert {'timing_conflict','material_model_ambiguity','context_incomplete'} <= {i['code'] for i in report['issues']}
    assert report['calculations'][0]['reported_step_seconds']=='0.002'
    assert report['calculations'][0]['calculated_step_seconds']=='0.0010'
    assert data['quantities'][0]['quantity_kind']=='observed_particle_count'
    assert next(q for q in data['quantities'] if q['quantity_id']=='step')['reported_value_text']=='2e-3'


def test_correct_conversion_retains_original_reported_value(data):
    data['conversions']=[dict(conversion_id='step-to-ms',input_id='step',target_unit='ms',derived_value_text='2',method='unit_conversion_v1')]
    report=validate_quantitative(data)
    assert report['conversions'][0]['computed_value']=='2'
    assert next(q for q in data['quantities'] if q['quantity_id']=='step')['reported_value_text']=='2e-3'
    # A numerically valid conversion does not repair the inconsistent configuration.
    assert not report['comparison_ready'] and not report['execution_eligible']


@pytest.mark.parametrize('fault',['hash','quote','artifact','number','nan','huge','unknown_field','id','unit_invention','unit_dimension','unit_quote','count_fraction','negative_time','unknown_issue','unknown_timing','wrong_timing_kind','conversion_unknown_units','conversion_wrong_value','conversion_dimensions','version'])
def test_reject_corrupt_evidence_and_unsupported_calculations(data,fault):
    q=data['quantities'][0]
    if fault=='hash':data['artifacts'][0]['sha256']='0'*64
    elif fault=='quote':q['evidence'][0]['exact_quote']='Fabricated evidence.'
    elif fault=='artifact':q['evidence'][0]['artifact_id']='missing'
    elif fault=='number':q['reported_value_text']='555'
    elif fault=='nan':q['reported_value_text']='NaN'
    elif fault=='huge':q['reported_value_text']='1e999'
    elif fault=='unknown_field':q['execution_eligible']=True
    elif fault=='id':data['quantities'].append(deepcopy(q))
    elif fault=='unit_invention':data['quantities'][1]['unit']={'status':'unreported','symbol':'kg/m3'}
    elif fault=='unit_dimension':q['unit']['symbol']='s'
    elif fault=='unit_quote':q['unit']['reported_text']='kilograms per cubic metre'
    elif fault=='unknown_issue':data['issues'][0]['quantity_ids']=['missing']
    elif fault=='unknown_timing':data['timing_checks'][0]['step_id']='missing'
    elif fault=='wrong_timing_kind':data['timing_checks'][0]['count_id']=q['quantity_id']
    elif fault=='version':data['study']['simulator']['version']='invented'
    elif fault.startswith('conversion_'):
        c=dict(conversion_id='test',input_id='step',target_unit='ms',derived_value_text='2000',method='unit_conversion_v1')
        if fault=='conversion_unknown_units':c.update(input_id='light-density_rho',target_unit='kg/m3')
        if fault=='conversion_dimensions':c.update(target_unit='count')
        data['conversions']=[c]
    else:
        # Supply synthetic numeric text so arithmetic validation, not quote matching, rejects it.
        value='0.5' if fault=='count_fraction' else '-1'
        target=q if fault=='count_fraction' else next(x for x in data['quantities'] if x['quantity_id']=='step')
        artifact=dict(artifact_id='synthetic-invalid',text=value+' particles seconds',locator='Invented negative test, not published evidence')
        artifact['sha256']=hashlib.sha256(artifact['text'].encode()).hexdigest()
        data['artifacts'].append(artifact)
        data['study']['synthetic_demo']=True
        target['reported_value_text']=value
        target['evidence']=[dict(artifact_id=artifact['artifact_id'],exact_quote=artifact['text'])]
    with pytest.raises(ValidationError):validate_quantitative(data)


def test_missing_units_are_not_dimensionless(data):
    q=data['quantities'][1]
    q['unit']={'status':'dimensionless','symbol':'1'}
    with pytest.raises(ValidationError):validate_quantitative(data)


def test_seconds_cannot_be_silently_relabelled_milliseconds(data):
    next(q for q in data['quantities'] if q['quantity_id']=='step')['unit']['symbol']='ms'
    with pytest.raises(ValidationError,match='unit label'):validate_quantitative(data)


def test_known_units_do_not_establish_cross_study_compatibility(data):
    data['issues']=[]
    data['timing_checks']=[]
    data['study']['context']['status']='complete'
    data['quantities']=[deepcopy(data['quantities'][0])]
    report=validate_quantitative(data)
    assert report['comparison_ready']
    assert not report['execution_eligible']


def test_cli_exposes_storage_and_execution_separately(capsys):
    assert run(['validate-quantitative','fluidlab'])==0
    result=json.loads(capsys.readouterr().out)
    assert result['storage_eligible'] and not result['execution_eligible']


def test_percentage_conversion_and_denominator_are_explicit(data):
    artifact=dict(artifact_id='synthetic-metric',text='Success was 75 percent of the 100 trials.',locator='Invented unit test, not scientific evidence')
    artifact['sha256']=hashlib.sha256(artifact['text'].encode()).hexdigest()
    data['artifacts'].append(artifact)
    data['study']['synthetic_demo']=True
    q=dict(quantity_id='success',annex_record_id='synthetic',quantity_kind='success_fraction',role='result',subject='Synthetic success metric',reported_value_text='75',unit=dict(status='explicit',symbol='%',reported_text='percent'),evidence=[dict(artifact_id=artifact['artifact_id'],exact_quote=artifact['text'])],metric_definition='Successful trials divided by all trials.',denominator='100 trials')
    data['quantities'].append(q)
    data['conversions']=[dict(conversion_id='percentage-to-fraction',input_id='success',target_unit='1',derived_value_text='0.75',method='unit_conversion_v1')]
    assert validate_quantitative(data)['conversions'][0]['computed_value']=='0.75'
    del q['denominator']
    with pytest.raises(ValidationError,match='denominator'):validate_quantitative(data)


def test_unknown_origin_is_not_misrepresented_as_simulation(data):
    data['study']['evidence_origin']='physical_experiment'
    with pytest.raises(ValidationError,match='schema'):validate_quantitative(data)


def test_source_number_cannot_silently_change_sign(data):
    artifact=dict(artifact_id='signed-test',text='-500 particles',locator='Invented sign regression')
    artifact['sha256']=hashlib.sha256(artifact['text'].encode()).hexdigest()
    data['artifacts'].append(artifact)
    data['study']['synthetic_demo']=True
    data['quantities'][0]['evidence']=[dict(artifact_id=artifact['artifact_id'],exact_quote=artifact['text'])]
    with pytest.raises(ValidationError,match='numeric spelling'):validate_quantitative(data)


def test_percentage_range_does_not_round_away_small_excess(data):
    value='100.00000000000000000000000000001'
    artifact=dict(artifact_id='precise-percentage',text=value+' percent of trials succeeded.',locator='Invented precision regression')
    artifact['sha256']=hashlib.sha256(artifact['text'].encode()).hexdigest()
    data['artifacts'].append(artifact)
    data['study']['synthetic_demo']=True
    data['quantities']=[dict(quantity_id='precise',annex_record_id='synthetic',quantity_kind='success_fraction',role='result',subject='Synthetic test',reported_value_text=value,unit=dict(status='explicit',symbol='%',reported_text='percent'),evidence=[dict(artifact_id=artifact['artifact_id'],exact_quote=artifact['text'])],metric_definition='Successful trials divided by trials.',denominator='all trials')]
    data['issues']=[]
    data['timing_checks']=[]
    with pytest.raises(ValidationError,match='physical range'):validate_quantitative(data)
