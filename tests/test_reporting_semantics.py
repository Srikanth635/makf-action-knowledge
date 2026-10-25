"""E1 0.2 source-reporting categories preserve evidence and reject false attribution."""
from copy import deepcopy
from importlib.util import find_spec
import json
from pathlib import Path

import pytest
from rdflib import Dataset, Literal, URIRef
import yaml
from makf_knowledge.paths import profile_path
from makf_knowledge.publication import PUB, export_batch, read_json, validate_dataset
from makf_knowledge.validation import SemanticValidator, ValidationError

PATH = Path(__file__).resolve().parents[1] / 'docs/experiments/corpus_expansion_001/semantic-v02-proposals.json'

@pytest.fixture(scope='module')
def validator():
    return SemanticValidator()

@pytest.fixture
def batch():
    return read_json(PATH)

@pytest.mark.parametrize('index', [0, 1, 2])
def test_source_reporting_categories_and_wrong_status(validator, batch, index):
    batch['candidates'] = [batch['candidates'][index]]
    profile = yaml.safe_load(profile_path().read_text())
    assert validator.validate_batch(batch, profile)['status'] == 'PASS'
    batch['candidates'][0]['epistemic_status'] = 'proposed_strategy'
    with pytest.raises(ValidationError, match='requires source derivation'):
        validator.validate_batch(batch, profile)

@pytest.mark.parametrize('index', [0, 1, 2])
def test_generated_ideas_cannot_be_source_reports(validator, batch, index):
    c = batch['candidates'][index]
    batch['candidates'] = [c]
    c.update(derivation_mode='llm_proposal', evidence_status='not_assessed', modality='possible')
    for support in c['source_support']:
        support['support_role'] = 'context_only'
    with pytest.raises(ValidationError, match='requires source derivation'):
        validator.validate_batch(batch, yaml.safe_load(profile_path().read_text()))

@pytest.mark.skipif(find_spec('pyshacl') is None, reason='Optional RDF extra')
def test_pending_reports_roundtrip_and_rdf_rejects_status_escalation(batch):
    result = export_batch(batch, base_iri='https://example.org/semantic-v02/')
    ds = Dataset().parse(data=dict(result.artifacts)['dataset.trig'], format='trig')
    manifest = json.loads(result.manifest_json)
    cg = ds.graph(URIRef(manifest['candidates_graph']))
    assert set(cg.objects(None, PUB.reviewState)) == {Literal('pending')}
    assert set(cg.objects(None, PUB.knowledgeKind)) == {Literal('benchmark_definition'),Literal('task_objective'),Literal('reported_observation')}
    claim = cg.value(predicate=PUB.knowledgeKind, object=Literal('reported_observation'))
    cg.set((claim, PUB.epistemicStatus, Literal('conditional_principle')))
    with pytest.raises(ValidationError, match='SHACL'):
        validate_dataset(ds, manifest)
