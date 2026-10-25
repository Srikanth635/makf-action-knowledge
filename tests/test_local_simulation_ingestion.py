"""Local experiment ingestion must preserve scope and reject incomplete/bad results."""
from copy import deepcopy
from importlib.util import find_spec, spec_from_file_location, module_from_spec
import json
from pathlib import Path
import pytest
from makf_knowledge.validation import ValidationError

ROOT=Path(__file__).resolve().parents[1]
EXPERIMENT=ROOT/'docs/experiments/fluidlab_validation_001'
pytestmark=pytest.mark.skipif(find_spec('pyshacl') is None,reason='Optional rdf extra')


def loader(tmp_path):
    spec=spec_from_file_location('local_ingestion',EXPERIMENT/'ingest_results.py')
    module=module_from_spec(spec);spec.loader.exec_module(module)
    module.HERE=tmp_path
    return module


def test_real_results_remain_local_pending_and_in_native_units(tmp_path):
    module=loader(tmp_path)
    report=module.ingest(EXPERIMENT/'validation-report.json',tmp_path/'rdf')
    data=json.loads((tmp_path/'local-evidence.json').read_text())
    assert data['study']['evidence_origin']=='local_simulation'
    assert data['study']['review_state']=='pending'
    assert data['study']['synthetic_demo'] is False
    assert report['quantity_count']==6 and not report['comparison_ready'] and not report['execution_eligible']
    assert sum(q['unit']['status']=='simulation_units' for q in data['quantities'])==2
    assert all('not a fluid-transfer' in q['metric_definition'] for q in data['quantities'] if q['quantity_kind']=='mass_fraction')
    assert json.loads((tmp_path/'rdf/manifest.json').read_text())['shacl_conforms']


@pytest.mark.parametrize('fault',['incomplete','missing_steps','nonfinite_mass'])
def test_no_evidence_bundle_for_incomplete_or_invalid_run(tmp_path,fault):
    raw=json.loads((EXPERIMENT/'validation-report.json').read_text())
    if fault=='incomplete':raw['status']='ERROR'
    elif fault=='missing_steps':raw['rollouts'][0]['records'].pop()
    elif fault=='nonfinite_mass':raw['rollouts'][0]['final']['active_mass']=float('nan')
    path=tmp_path/'input.json';path.write_text(json.dumps(raw))
    module=loader(tmp_path)
    with pytest.raises((ValueError,ValidationError)):
        module.ingest(path,tmp_path/'rdf')
    assert not (tmp_path/'rdf').exists()
