"""Coverage of explicit review annotations; never scientific entailment tests."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from makf_knowledge.review import evidence_coverage
from makf_knowledge.validation import validate_file
from makf_knowledge.paths import profile_path

ROOT = Path(__file__).resolve().parents[1] / 'docs/experiments/e23_pouring'


def read(name):
    return json.loads((ROOT / name).read_text())


def test_pourit_review_preserves_source_and_exposes_missing_evidence():
    original, revised = read('review-original-008.json'), read('review-proposed.json')
    annotations = read('review-annotations.json')
    source = (ROOT / 'source.txt').read_bytes()
    assert hashlib.sha256(source).hexdigest() == annotations['source_sha256']
    assert original['documents'] == revised['documents']
    assert original['extraction_run']['engine'] == 'openai'
    assert revised['extraction_run']['engine'] == 'agent_authored_review_revision'
    assert annotations['human_approved'] is False
    for old, new, annotation in zip(original['candidates'], revised['candidates'], annotations['reviews']):
        requirements = annotation['required_evidence']
        assert old['candidate_id'] == annotation['original_candidate_id']
        assert new['candidate_id'] == annotation['revised_candidate_id']
        assert evidence_coverage(old, original['documents'], requirements)['status'] == 'FAIL'
        assert evidence_coverage(new, revised['documents'], requirements)['status'] == 'PASS'
    assert validate_file(ROOT / 'review-proposed.json', profile_path('pouring'))['status'] == 'PASS'


@pytest.fixture
def example():
    text = 'Under these conditions,\nfeedback may reduce error.'
    documents = [{'document_id': 'd', 'passages': [{'passage_id': 'p', 'text': text}]}]
    support = dict(document_id='d', passage_id='p', exact_quote=text, support_role='asserts_claim')
    return documents, {'source_support': [support]}, [deepcopy(support)]


@pytest.mark.parametrize('fault', ['context', 'partial', 'wrong_document', 'normalized', 'wrong_offsets'])
def test_bad_citations_cannot_satisfy_review_coverage(example, fault):
    documents, candidate, requirements = example
    support = candidate['source_support'][0]
    if fault == 'context':
        support['support_role'] = 'context_only'
    elif fault == 'partial':
        support['exact_quote'] = 'feedback may reduce error.'
    elif fault == 'wrong_document':
        support['document_id'] = 'other'
    elif fault == 'normalized':
        support['exact_quote'] = support['exact_quote'].replace('\n', ' ')
    else:
        support.update(start_char=1, end_char=2)
    assert evidence_coverage(candidate, documents, requirements)['status'] == 'FAIL'


def test_adjacent_source_lines_jointly_cover_requirement(example):
    documents, candidate, requirements = example
    support = candidate['source_support'][0]
    candidate['source_support'] = [{**support, 'exact_quote': line}
                                   for line in support['exact_quote'].splitlines()]
    assert evidence_coverage(candidate, documents, requirements)['status'] == 'PASS'


def test_repeated_quote_requires_offsets():
    documents = [{'document_id': 'd', 'passages': [{'passage_id': 'p', 'text': 'cue cue'}]}]
    support = dict(document_id='d', passage_id='p', exact_quote='cue', support_role='asserts_claim')
    required = [{**support, 'start_char': 4, 'end_char': 7}]
    assert evidence_coverage({'source_support': [support]}, documents, required)['status'] == 'FAIL'
    assert evidence_coverage({'source_support': required}, documents, required)['status'] == 'PASS'


def test_missing_or_invalid_annotations_fail(example):
    documents, candidate, requirements = example
    with pytest.raises(ValueError):
        evidence_coverage(candidate, documents, [])
    requirements[0]['exact_quote'] = 'Fabricated review evidence'
    with pytest.raises(ValueError):
        evidence_coverage(candidate, documents, requirements)
