"""Offline tests of review boundaries and the four-call maximum workflow."""
from copy import deepcopy
import json
from pathlib import Path
import socket

import pytest

from makf_knowledge import ExtractionRequest, SourceDocument, SourcePassage, FixtureProvider, extract
from makf_knowledge.quality import CHECKS, review_quality, review_and_revise, select_reviewed

ROOT = Path(__file__).resolve().parents[1] / 'docs/experiments/e23_pouring'


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail('No network in quality tests')
    monkeypatch.setattr(socket.socket, 'connect', fail)


@pytest.fixture
def sample():
    batch = json.loads((ROOT / 'review-proposed.json').read_text())
    batch.pop('extraction_run')
    d = batch['documents'][0]
    request = ExtractionRequest(batch['batch_id'], (SourceDocument(
        d['document_id'], d['title'], d['synthetic_demo'],
        tuple(SourcePassage(**p) for p in d['passages']), uri=d.get('uri')),))
    result = extract(request, FixtureProvider(json.dumps(batch)))
    assert result.report['status'] == 'provisional'
    return request, batch, result


def assessments(batch, passed):
    return {'assessments': [{'candidate_id': c['candidate_id'],
        **{key: passed for key in CHECKS},
        'rationale': 'All supplied evidence covers the claim.' if passed else 'Missing outcome evidence; narrow the claim.'}
        for c in batch['candidates']]}


class Sequence:
    wire_format = 'e1'
    audit = {'engine': 'offline_fixture', 'live': False}
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []
    def generate(self, prompt):
        self.calls.append(deepcopy(prompt))
        return self.responses.pop(0)


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'unknown', 'blank', 'malformed', 'string_boolean'])
def test_review_fails_closed(sample, fault):
    _, batch, result = sample
    data = assessments(batch, True)
    if fault == 'missing': data['assessments'].pop()
    if fault == 'duplicate': data['assessments'][1] = deepcopy(data['assessments'][0])
    if fault == 'unknown': data['assessments'][0]['candidate_id'] = 'other'
    if fault == 'blank': data['assessments'][0]['rationale'] = ' '
    if fault == 'string_boolean': data['assessments'][0]['evidence_complete'] = 'true'
    raw = '{bad' if fault == 'malformed' else json.dumps(data)
    review = review_quality(result, FixtureProvider(raw))
    assert review.report['status'] == 'review_error'
    assert review.raw_response == raw


@pytest.mark.parametrize('check', CHECKS)
def test_each_quality_failure_blocks_selection(sample, tmp_path, check):
    request, batch, initial = sample
    data = assessments(batch, True)
    data['assessments'][0][check] = False
    initial.save(tmp_path / 'run')
    provider = Sequence()
    summary = review_and_revise(request, initial, provider, FixtureProvider(json.dumps(data)), tmp_path / 'run')
    assert summary['status'] == 'changes_required'
    assert summary['selected_run'] is None
    assert not provider.calls


@pytest.mark.parametrize('second_passes', [True, False])
def test_one_revision_preserves_original_and_is_reviewed(sample, tmp_path, second_passes):
    request, batch, initial = sample
    initial.save(tmp_path / 'run')
    original_bytes = (tmp_path / 'run/candidates.json').read_bytes()
    provider = Sequence(json.dumps(batch))
    reviewer = Sequence(json.dumps(assessments(batch, False)), json.dumps(assessments(batch, second_passes)))
    summary = review_and_revise(request, initial, provider, reviewer, tmp_path / 'run', revise_once=True)
    assert len(provider.calls) == 1 and len(reviewer.calls) == 2
    assert summary['selected_run'] == ('revision' if second_passes else None)
    assert summary['human_review_required']
    assert (tmp_path / 'run/candidates.json').read_bytes() == original_bytes
    feedback = json.loads(provider.calls[0].messages[-1].content)
    assert feedback['previous_candidates'] == batch['candidates']
    assert feedback['review_findings'][0]['evidence_complete'] is False
    with pytest.raises(ValueError):
        review_and_revise(request, initial, provider, reviewer, tmp_path / 'run', revise_once=True)
    assert len(provider.calls) == 1


def test_invalid_revision_cannot_fall_back_to_rejected_batch(sample, tmp_path):
    request, batch, initial = sample
    initial.save(tmp_path / 'run')
    provider = Sequence('{}')
    reviewer = Sequence(json.dumps(assessments(batch, False)))
    summary = review_and_revise(request, initial, provider, reviewer, tmp_path / 'run', revise_once=True)
    assert summary['status'] == 'quarantined' and summary['selected_run'] is None
    assert len(reviewer.calls) == 1


def test_review_error_does_not_trigger_revision(sample, tmp_path):
    request, _, initial = sample
    initial.save(tmp_path / 'run')
    provider = Sequence()
    summary = review_and_revise(request, initial, provider, Sequence('{}'), tmp_path / 'run', revise_once=True)
    assert summary['status'] == 'review_error' and summary['selected_run'] is None
    assert not provider.calls


@pytest.mark.parametrize('rename', [False, True])
def test_revision_omissions_are_explicit_and_renames_rejected(sample, tmp_path, rename):
    request, batch, initial = sample
    initial.save(tmp_path / 'run')
    revised = deepcopy(batch)
    omitted = revised['candidates'].pop()['candidate_id']
    if rename:
        revised['candidates'][0]['candidate_id'] = 'new-unrequested-id'
    reviewer = Sequence(json.dumps(assessments(batch, False)), json.dumps(assessments(revised, True)))
    summary = review_and_revise(request, initial, Sequence(json.dumps(revised)), reviewer,
                                tmp_path / 'run', revise_once=True)
    if rename:
        assert summary['status'] == 'quarantined' and summary['selected_run'] is None
        assert len(reviewer.calls) == 1
    else:
        assert summary['selected_run'] == 'revision'
        assert summary['omitted_candidate_ids'] == [omitted]


def test_cli_review_workflow_is_bounded_and_closes_clients(sample, tmp_path, monkeypatch):
    from makf_knowledge import cli
    _, batch, _ = sample
    clients = []
    class Extractor(Sequence):
        def __init__(self, *args, **kwargs):
            super().__init__(json.dumps(batch), json.dumps(batch))
            self.closed = False
            clients.append(self)
        def close(self): self.closed = True
    class Reviewer(Extractor):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.responses = [json.dumps(assessments(batch, False)), json.dumps(assessments(batch, True))]
    monkeypatch.setattr(cli, 'OpenAIProvider', Extractor)
    monkeypatch.setattr(cli, 'OpenAIReviewer', Reviewer)
    d = batch['documents'][0]
    p = d['passages'][0]
    text_file = tmp_path / 'source.txt'
    text_file.write_text(p['text'])
    args = ['extract', '--provider', 'openai', '--model', 'fake-model', '--review-model', 'fake-review',
            '--revise-once', '--text-file', str(text_file), '--source-id', d['document_id'],
            '--source-title', d['title'], '--source-uri', d['uri'], '--locator', p['locator'],
            '--passage-id', p['passage_id'], '--batch-id', batch['batch_id'], '--out-dir', str(tmp_path / 'run')]
    assert cli.run(args) == 0
    assert [len(c.calls) for c in clients] == [2, 2]
    assert all(c.closed for c in clients)
    assert json.loads((tmp_path / 'run/workflow.json').read_text())['selected_run'] == 'revision'


def test_explicit_subset_keeps_only_unchanged_passing_candidates(sample, tmp_path):
    request, batch, initial = sample
    initial.save(tmp_path / 'run')
    data = assessments(batch, True)
    data['assessments'][1]['mapping_supported'] = False
    data['assessments'][2]['scope_supported'] = False
    summary = review_and_revise(request, initial, Sequence(), Sequence(json.dumps(data)),
                                tmp_path / 'run', select_passed=True)
    assert summary['status'] == 'model_reviewed_subset'
    assert summary['selected_candidate_ids'] == [batch['candidates'][0]['candidate_id']]
    selected = json.loads((tmp_path / 'run/selection/candidates.json').read_text())
    assert selected['candidates'] == initial.batch['candidates'][:1]
    assert selected['documents'] == initial.batch['documents']
    assert len(json.loads((tmp_path / 'run/candidates.json').read_text())['candidates']) == 3


def test_selection_rejects_review_of_different_batch_and_empty_acceptance(sample, tmp_path):
    _, batch, initial = sample
    review = review_quality(initial, FixtureProvider(json.dumps(assessments(batch, False))))
    selected = select_reviewed(initial, review, tmp_path / 'none')
    assert selected['selected_candidate_ids'] == []
    assert not (tmp_path / 'none/candidates.json').exists()
    initial.batch['candidates'][0]['statement'] += ' Fabricated update.'
    with pytest.raises(ValueError):
        select_reviewed(initial, review, tmp_path / 'mismatch')
