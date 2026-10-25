"""Offline assembly of independently validated paper snapshots; no claim merging."""
import argparse
import hashlib
import json
from pathlib import Path

from rdflib import Dataset, RDF, URIRef
from makf_knowledge.publication import PUB, export_batch, read_json, validate_dataset

HERE = Path(__file__).resolve().parent
BASE = 'https://example.org/makf/data/'


def assemble(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    prior = HERE.parent / 'e23_pouring'
    sources = [('pourit', read_json(prior / 'quality-selected.json'),
        read_json(prior / 'quality-evaluation.json')['selection'], read_json(prior / 'quality-reviewed.json'),
        'published_research')]
    outcomes = read_json(HERE / 'experiment-results.json')['sources']
    withheld_sources = []
    for outcome in outcomes:
        key = outcome['source']
        if not outcome['selected_candidate_count']:
            withheld_sources.append({'source_key': key, 'status': outcome['status'],
                'reason': 'No candidates passed the bounded advisory review; source and simulation annex retained for curation.'})
            continue
        sources.append((key, read_json(HERE / (key + '-selected.json')),
            read_json(HERE / (key + '-selection.json')), read_json(HERE / (key + '-reviewed.json')),
            'published_simulation'))
    dataset = Dataset()
    dataset.bind('pub', PUB)
    entries = []
    seen_graphs = set()
    for key, batch, selection, reviewed, origin in sources:
        result = export_batch(batch, base_iri=BASE, selection=selection, reviewed_batch=reviewed)
        result.save(output / 'bundles' / key)
        manifest = json.loads(result.manifest_json)
        graph = Dataset().parse(data=dict(result.artifacts)['dataset.trig'], format='trig')
        validate_dataset(graph, manifest)
        graph_ids = {manifest['sources_graph'], manifest['candidates_graph']}
        if seen_graphs & graph_ids:
            raise ValueError('Overlapping snapshot graphs require explicit reconciliation')
        seen_graphs.update(graph_ids)
        for s, p, o, g in graph.quads():
            dataset.graph(g).add((s, p, o))
        entries.append({'source_key':key, 'evidence_origin':origin,
            'bundle': 'bundles/' + key, 'sources_graph':manifest['sources_graph'],
            'candidates_graph':manifest['candidates_graph'], 'review_state':manifest['review_state'],
            'candidate_count':manifest['candidate_count'], 'quad_count':manifest['quad_count']})
    dataset.serialize(destination=output / 'collection.trig', format='trig')
    values = '\n'.join(f'(<{e["candidates_graph"]}> <{e["sources_graph"]}> "{e["evidence_origin"]}")' for e in entries)
    query = '''PREFIX pub: <https://example.org/makf/publication/0.1#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT DISTINCT ?claim ?sourceTitle ?origin ?statement ?reviewState ?supportRole ?mappingGap WHERE {
 VALUES (?candidateGraph ?sourceGraph ?origin) {
''' + values + '''
 }
 GRAPH ?candidateGraph {
  ?claim a pub:Claim; pub:statement ?statement; pub:review ?review; pub:evidence ?anchor.
  ?review pub:reviewState ?reviewState.
  FILTER(?reviewState = "model_selected_provisional")
  ?anchor pub:document ?document; pub:supportRole ?supportRole.
  OPTIONAL { ?claim pub:hasComponent ?c. ?c pub:groundingStatus "needs_mapping"; pub:description ?mappingGap. }
 }
 GRAPH ?sourceGraph { ?document dct:title ?sourceTitle; pub:syntheticDemo false. }
}
ORDER BY ?sourceTitle ?claim
'''
    (output / 'claims.rq').write_text(query)
    rows = [{str(k):str(v) for k,v in row.asdict().items()} for row in dataset.query(query)]
    (output / 'query-results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False)+'\n')
    count = len({s for s,p,o,g in dataset.quads() if p == RDF.type and o == PUB.Claim})
    if count != sum(e['candidate_count'] for e in entries):
        raise ValueError('Collection changed claim identity/count')
    if set(str(g) for _,_,_,g in dataset.quads()) != seen_graphs:
        raise ValueError('Collection contains unexpected graphs')
    manifest = {'schema_version':'research-collection-0.1', 'source_count':len(entries),
        'claim_count':count, 'quad_count':len(list(dataset.quads())), 'snapshots':entries,
        'withheld_sources':withheld_sources,
        'review_policy':'Only explicit model-selected provisional subsets; no human approval or empirical truth inferred.',
        'simulation_scope':'Published reports only; no simulations executed or raw trajectories ingested.',
        'numeric_annex':'docs/experiments/corpus_expansion_001/simulation-evidence.json; retained separately pending units/schema review.',
        'files_sha256':{name:hashlib.sha256((output/name).read_bytes()).hexdigest()
                        for name in ('collection.trig','claims.rq','query-results.json')}}
    marker = output / '.manifest.tmp'
    marker.write_text(json.dumps(manifest,indent=2)+'\n')
    marker.replace(output / 'manifest.json')
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    args=parser.parse_args()
    manifest=assemble(args.out_dir)
    print(json.dumps({k:manifest[k] for k in ('source_count','claim_count','quad_count')},indent=2))
