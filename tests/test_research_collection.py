"""Offline integrity of the research expansion and conservative multi-source assembly."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from rdflib import Dataset, RDF
from makf_knowledge.publication import PUB, read_json

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / 'docs/experiments/corpus_expansion_001'


def test_research_excerpts_preserve_hashes_and_document_identity():
    catalog = json.loads((EXPERIMENT / 'source-catalog.json').read_text())
    assert len({r['document_id'] for r in catalog}) == 2
    # Research simulations are real published sources, not invented demo passages.
    for record in catalog:
        key = 'softgym' if 'softgym' in record['document_id'] else 'fluidlab'
        document = read_json(EXPERIMENT / (key + '-source.json'))
        assert document['document_id'] == record['document_id']
        assert document['synthetic_demo'] is False
        assert record['simulation_reproduced'] is False
        passages = {p['passage_id']:p for p in document['passages']}
        for evidence in record['passages']:
            raw = (EXPERIMENT / evidence['file']).read_bytes()
            assert raw.decode('utf-8') == passages[evidence['passage_id']]['text']
            assert hashlib.sha256(raw).hexdigest() == evidence['sha256']


def test_simulation_annex_keeps_unresolved_units_and_source_inconsistencies():
    annex = read_json(EXPERIMENT / 'simulation-evidence.json')
    for evidence in annex['evidence']:
        raw = (EXPERIMENT / evidence['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == evidence['sha256']
        assert raw.decode('utf-8') == evidence['exact_text']
    by_id = {r['record_id']:r for r in annex['records']}
    table = (EXPERIMENT / 'fluidlab-tables-3-4.txt').read_text()
    for material in ('light', 'heavy'):
        record = by_id[f'fluidlab-{material}-liquid-parameters']
        line = next(line for line in table.splitlines() if record['material_label'] in line)
        mu, lam, rho = map(float, line.split()[-3:])
        assert record['source_values'] == {'mu':mu, 'lambda':lam, 'density_rho':rho}
        assert 'not specified' in record['unit_status']
    timing = by_id['fluidlab-runtime-timing']
    assert timing['reported_step_seconds'] != timing['reported_substeps_per_step'] * timing['reported_substep_seconds']
    assert timing['status'] == 'needs_source_resolution'


@pytest.mark.skipif(importlib.util.find_spec('pyshacl') is None, reason='Requires optional rdf extra')
def test_collection_preserves_prior_claims_and_excludes_withheld_sources(tmp_path):
    spec = importlib.util.spec_from_file_location('research_assembly', EXPERIMENT / 'assemble_collection.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = tmp_path / 'collection'
    manifest = module.assemble(out)
    assert manifest['claim_count'] == 2
    assert manifest['source_count'] == 2
    assert [s['source_key'] for s in manifest['withheld_sources']] == ['fluidlab']
    combined = Dataset().parse(out / 'collection.trig', format='trig')
    prior = Dataset().parse(ROOT / 'docs/design/publication-v0.1/worked-example.trig', format='trig')
    substantive = lambda d: {q for q in d.quads() if q[1] != PUB.artifactPath}
    assert substantive(prior) <= substantive(combined)
    for entry in manifest['snapshots']:
        graph = Dataset().parse(out / entry['bundle'] / 'dataset.trig', format='trig')
        assert set(graph.quads()) <= set(combined.quads())
    assert not any('fluidlab' in str(o) for _,p,o,_ in combined.quads() if p == PUB.documentId)
    query = (out / 'claims.rq').read_text()
    rows = list(combined.query(query))
    assert {str(row.origin) for row in rows} == {'published_research','published_simulation'}
    assert len({row.claim for row in rows}) == 2
    assert not list(combined.query(query.replace('model_selected_provisional','human_approved')))
    for name, expected in manifest['files_sha256'].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
    original = (out / 'collection.trig').read_bytes()
    with pytest.raises(FileExistsError):
        module.assemble(out)
    assert (out / 'collection.trig').read_bytes() == original
