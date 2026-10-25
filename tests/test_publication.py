"""Provisional RDF export, content-bound review, graph isolation and failure paths."""
from copy import deepcopy
import hashlib
from importlib.util import find_spec
import json
from pathlib import Path
import sys

import pytest
from rdflib import Dataset, Graph, Literal, RDF, URIRef

from makf_knowledge.cli import run
from makf_knowledge.paths import example_path, resource_path
from makf_knowledge.publication import PUB, export_batch, read_json, validate_dataset
from makf_knowledge.validation import ValidationError

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://example.org/makf/data/'
HAS_SHACL = find_spec('pyshacl') is not None
rdf = pytest.mark.skipif(not HAS_SHACL, reason='Install the optional rdf extra to exercise SHACL export')


def sample(action='pouring'):
    return read_json(example_path(action))


def unpack(result):
    return Dataset().parse(data=dict(result.artifacts)['dataset.trig'], format='trig'), json.loads(result.manifest_json)


def selection_for(batch):
    return {'status': 'model_reviewed_subset',
            'selected_candidate_ids': [c['candidate_id'] for c in batch['candidates']],
            'withheld_candidate_ids': [],
            'reviewed_batch_sha256': hashlib.sha256(json.dumps(batch, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
            'review_response_sha256': 'a' * 64, 'human_review_required': True,
            'scope': 'Synthetic test decision; not scientific evidence.'}


@rdf
@pytest.mark.parametrize('action', ['pouring', 'grasping'])
def test_hypotheses_export_with_evidence_and_no_domain_assertions(action):
    batch = sample(action)
    before = deepcopy(batch)
    ds, manifest = unpack(export_batch(batch, base_iri=BASE, profile=action))
    assert batch == before
    cg = ds.graph(URIRef(manifest['candidates_graph']))
    sg = ds.graph(URIRef(manifest['sources_graph']))
    assert set(cg.objects(None, PUB.reviewState)) == {Literal('pending')}
    assert set(sg.objects(None, PUB.syntheticDemo)) == {Literal(True)}
    assert len(list(cg.subjects(RDF.type, PUB.StructuralLink))) == sum(len(c['structural_links']) for c in batch['candidates'])
    for claim in cg.subjects(RDF.type, PUB.Claim):
        assert (claim, RDF.type, cg.value(claim, PUB.actionClass)) not in cg
    for component, cls in cg.subject_objects(PUB.groundedClass):
        assert (component, RDF.type, cls) not in cg
    for anchor in cg.subjects(RDF.type, PUB.EvidenceAnchor):
        assert str(cg.value(anchor, PUB.exactQuote)) in str(sg.value(cg.value(anchor, PUB.passage), PUB.text))
    assert manifest['shacl_conforms'] is True


@rdf
def test_real_selected_candidate_matches_worked_contract():
    directory = ROOT / 'docs/experiments/e23_pouring'
    batch = read_json(directory / 'quality-selected.json')
    selection = read_json(directory / 'quality-evaluation.json')['selection']
    reviewed = read_json(directory / 'quality-reviewed.json')
    ds, manifest = unpack(export_batch(batch, base_iri=BASE, selection=selection, reviewed_batch=reviewed))
    golden = Dataset().parse(ROOT / 'docs/design/publication-v0.1/worked-example.trig', format='trig')
    # Only the portable bundle-relative assessment location replaces the illustration path.
    triples = lambda d: {q for q in d.quads() if q[1] != PUB.artifactPath}
    assert triples(ds) == triples(golden)
    assert manifest['review_state'] == 'model_selected_provisional'
    query = (ROOT / 'docs/design/publication-v0.1/queries.rq').read_text()
    bindings = {'candidateGraph': URIRef(manifest['candidates_graph']), 'sourcesGraph': URIRef(manifest['sources_graph'])}
    rows = list(ds.query(query, initBindings=bindings))
    assert len(rows) == 1 and rows[0].mappingGap
    assert not list(ds.query(query.replace('model_selected_provisional', 'human_approved'), initBindings=bindings))


@rdf
def test_idempotence_namespace_and_review_changes():
    batch = sample('grasping')
    args = dict(base_iri=BASE, profile='grasping')
    a, ma = unpack(export_batch(batch, **args))
    b, mb = unpack(export_batch(batch, **args))
    assert set(a.quads()) == set(b.quads())
    assert ma['candidates_graph'] == mb['candidates_graph']
    c, mc = unpack(export_batch(batch, selection=selection_for(batch), reviewed_batch=batch, **args))
    assert ma['candidates_graph'] != mc['candidates_graph']
    # Query named graphs explicitly; Dataset's default graph is intentionally empty.
    claims = lambda d: {s for s, p, o, _ in d.quads() if p == RDF.type and o == PUB.Claim}
    assert claims(a) == claims(c)
    d, _ = unpack(export_batch(batch, base_iri='https://data.example.test/project', profile='grasping'))
    assert all(str(s).startswith('https://data.example.test/project/') for s in claims(d))
    changed = deepcopy(batch)
    changed['candidates'][0]['statement'] += ' (Qualified description.)'
    e, _ = unpack(export_batch(changed, **args))
    assert claims(e).isdisjoint(claims(a))


@rdf
def test_generated_hypothesis_keeps_context_only_evidence():
    batch = sample('grasping')
    del batch['extraction_run']
    c = batch['candidates'][0]
    c.update(derivation_mode='llm_proposal', evidence_status='not_assessed')
    c['source_support'][0]['support_role'] = 'context_only'
    ds, manifest = unpack(export_batch(batch, base_iri=BASE, profile='grasping'))
    cg = ds.graph(URIRef(manifest['candidates_graph']))
    assert set(cg.objects(None, PUB.supportRole)) == {Literal('context_only')}
    assert not list(cg.subjects(RDF.type, PUB.ExtractionRun))


@rdf
def test_multiple_sources_keep_separate_evidence_and_corroboration_warning():
    batch = sample('grasping')
    other = deepcopy(batch['documents'][0])
    other.update(document_id='second-synthetic-source', title='Second synthetic example, not independent evidence')
    batch['documents'].append(other)
    c = batch['candidates'][0]
    support = deepcopy(c['source_support'][0])
    support['document_id'] = other['document_id']
    c['source_support'].append(support)
    c['evidence_status'] = 'corroborated'
    result = export_batch(batch, base_iri=BASE, profile='grasping')
    ds, manifest = unpack(result)
    cg = ds.graph(URIRef(manifest['candidates_graph']))
    assert len(list(cg.subjects(RDF.type, PUB.EvidenceAnchor))) == 2
    warnings = json.loads(dict(result.artifacts)['validation.json'])['e1']['warnings']
    assert any('independent corroboration is not proven' in warning for warning in warnings)


@rdf
def test_unicode_crlf_offsets_and_timestamp_roundtrip():
    batch = sample('grasping')
    text = 'préface\r\n🫗 exact quotation\r\nfin'
    quote = '🫗 exact quotation'
    batch['documents'][0]['passages'][0]['text'] = text
    support = batch['candidates'][0]['source_support'][0]
    support.update(exact_quote=quote, start_char=text.index(quote), end_char=text.index(quote) + len(quote))
    batch['extraction_run']['recorded_at'] = '2026-10-24T00:00:00Z'
    result = export_batch(batch, profile='grasping', base_iri=BASE)
    ds, manifest = unpack(result)
    assert text in {str(v) for v in ds.graph(URIRef(manifest['sources_graph'])).objects(None, PUB.text)}
    assert json.loads(dict(result.artifacts)['candidates.json']) == batch


@pytest.mark.parametrize('mutation', ['claim', 'source', 'run', 'digest', 'overlap', 'missing', 'human', 'duplicate'])
def test_selection_is_bound_to_exact_unchanged_content(mutation):
    batch = sample('grasping')
    original = deepcopy(batch)
    selection = selection_for(original)
    if mutation == 'claim':
        batch['candidates'][0]['statement'] += ' Changed.'
    elif mutation == 'source':
        batch['documents'][0]['title'] += ' Changed.'
    elif mutation == 'run':
        batch['extraction_run']['engine'] = 'different'
    elif mutation == 'digest':
        selection['reviewed_batch_sha256'] = '0' * 64
    elif mutation == 'overlap':
        selection['withheld_candidate_ids'] = selection['selected_candidate_ids'][:]
    elif mutation == 'missing':
        original = None
    elif mutation == 'human':
        selection['status'] = 'human_approved'
    elif mutation == 'duplicate':
        selection['selected_candidate_ids'] *= 2
    with pytest.raises(ValidationError):
        export_batch(batch, base_iri=BASE, profile='grasping', selection=selection, reviewed_batch=original)


@pytest.mark.parametrize('change', ['quote', 'class', 'hypothesis_link', 'duplicate_id', 'domain', 'generated'])
def test_e1_semantics_are_required_before_export(change):
    batch = sample('grasping')
    c = batch['candidates'][0]
    if change == 'quote':
        c['source_support'][0]['exact_quote'] = 'Invented quote.'
    elif change == 'class':
        c['components'][0]['ontology_class'] = 'makf:Nonexistent'
    elif change == 'hypothesis_link':
        c['structural_links'] = []
    elif change == 'duplicate_id':
        batch['candidates'].append(deepcopy(c))
    elif change == 'domain':
        c['structural_links'][0]['subject_component'] = 'condition'
    elif change == 'generated':
        c['derivation_mode'] = 'llm_proposal'
    with pytest.raises(ValidationError):
        export_batch(batch, base_iri=BASE, profile='grasping')


@rdf
@pytest.mark.parametrize('change', ['quote', 'link', 'review', 'backlink', 'extra_graph', 'default_graph', 'wrong_graph', 'generated', 'whitespace', 'offset'])
def test_rdf_validation_rejects_corrupted_snapshots(change):
    ds, manifest = unpack(export_batch(sample('grasping'), base_iri=BASE, profile='grasping'))
    cg, sg = [ds.graph(URIRef(manifest[k])) for k in ('candidates_graph', 'sources_graph')]
    claim = cg.value(predicate=RDF.type, object=PUB.Claim)
    evidence = cg.value(claim, PUB.evidence)
    if change == 'quote':
        cg.set((evidence, PUB.exactQuote, Literal('Invented quote.')))
    elif change == 'link':
        link = next(cg.subjects(PUB.predicate, URIRef('https://w3id.org/aicor/makf#predictsPossibleEffect')))
        cg.remove((claim, PUB.structuralLink, link))
    elif change == 'review':
        cg.set((cg.value(claim, PUB.review), PUB.reviewState, Literal('human_approved')))
    elif change == 'backlink':
        sg.remove((None, PUB.passage, None))
    elif change in {'extra_graph', 'default_graph'}:
        target = ds.graph(URIRef('urn:unrelated')) if change == 'extra_graph' else ds.default_graph
        target.add((URIRef('urn:subject'), RDF.type, PUB.Claim))
    elif change == 'wrong_graph':
        triple = (claim, PUB.statement, cg.value(claim, PUB.statement))
        cg.remove(triple)
        sg.add(triple)
    elif change == 'generated':
        cg.set((claim, PUB.derivationMode, Literal('llm_proposal')))
    elif change == 'whitespace':
        cg.set((claim, PUB.statement, Literal(' \n\t')))
    elif change == 'offset':
        cg.set((evidence, PUB.startChar, Literal(0)))
        cg.set((evidence, PUB.endChar, Literal(100000)))
    with pytest.raises(ValidationError):
        validate_dataset(ds, manifest)


@rdf
def test_bundle_hashes_and_no_overwrite(tmp_path):
    result = export_batch(sample('grasping'), base_iri=BASE, profile='grasping')
    out = tmp_path / 'bundle'
    result.save(out)
    manifest = read_json(out / 'manifest.json')
    for name, digest in manifest['files_sha256'].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    with pytest.raises(FileExistsError):
        result.save(out)
    assert before == {p.name: p.read_bytes() for p in out.iterdir()}


@rdf
def test_write_failure_leaves_no_complete_bundle(tmp_path, monkeypatch):
    result = export_batch(sample('grasping'), base_iri=BASE, profile='grasping')
    original = Path.write_bytes
    def fail(path, data):
        if path.name == 'assessment.json':
            raise OSError('Simulated disk failure')
        return original(path, data)
    monkeypatch.setattr(Path, 'write_bytes', fail)
    with pytest.raises(OSError, match='disk failure'):
        result.save(tmp_path / 'bundle')
    assert not (tmp_path / 'bundle').exists()


@rdf
def test_cli_export_and_invalid_input_leave_no_output(tmp_path, capsys):
    args = ['export-rdf', 'grasping', '--profile', 'grasping', '--base-iri', BASE, '--out-dir', str(tmp_path / 'ok')]
    assert run(args) == 0
    assert json.loads(capsys.readouterr().out)['review_state'] == 'pending'
    assert run(args) == 1
    assert 'preserved' in capsys.readouterr().err
    batch = sample('grasping')
    batch['candidates'][0]['source_support'][0]['exact_quote'] = 'Invented.'
    bad = tmp_path / 'bad.json'
    bad.write_text(json.dumps(batch))
    args[1], args[-1] = str(bad), str(tmp_path / 'bad-out')
    assert run(args) == 1
    assert not (tmp_path / 'bad-out').exists()


def test_missing_optional_dependency_is_actionable(monkeypatch):
    monkeypatch.setitem(sys.modules, 'pyshacl', None)
    with pytest.raises(ValidationError, match='optional dependency'):
        export_batch(sample('grasping'), base_iri=BASE, profile='grasping')


@pytest.mark.parametrize('value', ['relative', 'file:///tmp/x', 'https://example.test/#x',
                                  'https://user:secret@example.test/', 'https://example.test/a b'])
def test_invalid_namespaces(value):
    with pytest.raises(ValidationError, match='Data base'):
        export_batch(sample(), base_iri=value)


def test_strict_json_rejects_duplicate_keys(tmp_path):
    path = tmp_path / 'duplicate.json'
    path.write_text('{"status":"pending","status":"human_approved"}')
    with pytest.raises(ValueError, match='Duplicate'):
        read_json(path)


@rdf
def test_packaged_shapes_are_valid_shacl():
    from pyshacl import validate
    shapes = Graph().parse(resource_path('publication', 'shapes.ttl'))
    assert validate(Graph(), shacl_graph=shapes, meta_shacl=True, do_owl_imports=False)[0]
