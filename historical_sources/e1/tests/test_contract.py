"""E1 regression and rejection tests (fixtures are synthetic, not factual evidence)."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate import SemanticValidator, ValidationError
import yaml

@pytest.fixture(scope='module')
def validator():
    return SemanticValidator(ROOT)

@pytest.fixture
def pouring():
    return json.loads((ROOT / 'examples/pouring_hypothesis.json').read_text())

@pytest.fixture
def profile():
    return yaml.safe_load((ROOT / 'profiles/pouring.yaml').read_text())

def test_pouring_sample(validator, pouring, profile):
    result = validator.validate_batch(pouring, profile)
    assert result['status'] == 'PASS'
    assert any('SYNTHETIC' in s for s in result['warnings'])

def test_grasping_sample(validator):
    p = yaml.safe_load((ROOT / 'profiles/grasping-smoke.yaml').read_text())
    g = json.loads((ROOT / 'examples/grasping_hypothesis.json').read_text())
    assert validator.validate_batch(g, p)['status'] == 'PASS'

@pytest.mark.parametrize('new_field', ['robot_id','scene_id','world_state','execution_id'])
def test_reject_world_model_fields(validator, pouring, profile, new_field):
    pouring['candidates'][0][new_field] = 'concrete-state'
    with pytest.raises(ValidationError, match='JSON Schema'):
        validator.validate_batch(pouring, profile)

def test_reject_missing_epistemic_status(validator, pouring, profile):
    del pouring['candidates'][0]['epistemic_status']
    with pytest.raises(ValidationError, match='JSON Schema'):
        validator.validate_batch(pouring, profile)

def test_reject_bad_quote(validator, pouring, profile):
    pouring['candidates'][0]['source_support'][0]['exact_quote'] = 'The paper proves that any container always pours perfectly.'
    with pytest.raises(ValidationError, match='exact_quote'):
        validator.validate_batch(pouring, profile)

def test_reject_bad_offsets(validator, pouring, profile):
    pouring['candidates'][0]['source_support'][0]['start_char'] = 2
    with pytest.raises(ValidationError, match='offsets'):
        validator.validate_batch(pouring, profile)

def test_reject_nonexistent_class(validator, pouring, profile):
    pouring['candidates'][0]['components'][0]['ontology_class'] = 'paf:NonExistentHypothesis'
    with pytest.raises(ValidationError, match='not declared'):
        validator.validate_batch(pouring, profile)

def test_reject_wrong_property_range(validator, pouring, profile):
    pouring['candidates'][0]['structural_links'][0]['object_component'] = 'effect'
    with pytest.raises(ValidationError, match='range'):
        validator.validate_batch(pouring, profile)

def test_reject_missing_condition_link(validator, pouring, profile):
    pouring['candidates'][0]['structural_links'] = [x for x in pouring['candidates'][0]['structural_links'] if x['predicate_curie'] != 'makf:hasApplicabilityCondition']
    with pytest.raises(ValidationError, match='hasApplicabilityCondition'):
        validator.validate_batch(pouring, profile)

def test_reject_unhedged_generated_hypothesis(validator, pouring, profile):
    c = pouring['candidates'][0]
    c['derivation_mode'] = 'llm_proposal'
    c['evidence_status'] = 'not_assessed'
    c['modality'] = 'necessary'
    with pytest.raises(ValidationError, match='cannot be labeled necessary'):
        validator.validate_batch(pouring, profile)

def test_reject_llm_proposal_labeled_source_proven(validator, pouring, profile):
    c = pouring['candidates'][0]
    c['derivation_mode'] = 'llm_proposal'
    with pytest.raises(ValidationError, match='generated/inferred'):
        validator.validate_batch(pouring, profile)

def test_reject_unsupported_ontology_grounding(validator, pouring, profile):
    c = pouring['candidates'][0]['components'][0]
    c['grounding_status'] = 'needs_mapping'
    c['ontology_class'] = None
    with pytest.raises(ValidationError, match='JSON Schema'):
        validator.validate_batch(pouring, profile)

def test_valid_unmapped_additional_component(validator, pouring, profile):
    pouring['candidates'][0]['components'].append({
        'component_id':'not-yet-mapped','component_kind':'generic_description',
        'description':'A notion not represented by current vocabularies',
        'grounding_status':'needs_mapping',
        'grounding_note':'Requires controlled ontology extension review'
    })
    result = validator.validate_batch(pouring, profile)
    assert result['status'] == 'PASS'
    assert any('pending ontology grounding' in w for w in result['warnings'])

def test_reject_duplicate_component_ids(validator, pouring, profile):
    pouring['candidates'][0]['components'].append(deepcopy(pouring['candidates'][0]['components'][0]))
    with pytest.raises(ValidationError, match='duplicate component_id'):
        validator.validate_batch(pouring, profile)

def test_reject_wrong_profile(validator, pouring):
    gp = yaml.safe_load((ROOT / 'profiles/grasping-smoke.yaml').read_text())
    with pytest.raises(ValidationError, match='profile_id'):
        validator.validate_batch(pouring, gp)

def test_reject_corrob_claim_with_single_document(validator, pouring, profile):
    pouring['candidates'][0]['evidence_status'] = 'corroborated'
    with pytest.raises(ValidationError, match='two independently'):
        validator.validate_batch(pouring, profile)

def test_reject_unknown_predicate(validator, pouring, profile):
    pouring['candidates'][0]['structural_links'][0]['predicate_curie'] = 'makf:entailsPhysicalOutflow'
    with pytest.raises(ValidationError, match='not declared'):
        validator.validate_batch(pouring, profile)

def test_all_profile_focus_terms_exist(validator):
    for n in ('pouring.yaml', 'grasping-smoke.yaml'):
        validator.validate_profile(yaml.safe_load((ROOT / 'profiles' / n).read_text()))

def test_json_schema_generated_from_linkml(validator):
    committed = json.loads((ROOT / 'schema/makf_extraction.schema.json').read_text())
    assert committed == validator.json_schema


def test_reject_mismatched_action_frame_profile(validator, profile):
    profile['ontology_action_class'] = 'aicor:Grasping'
    with pytest.raises(ValidationError, match='hasActionCategory'):
        validator.validate_profile(profile)
