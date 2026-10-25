"""Offline checks of the draft fixture, not a production publication gate."""
import json
from importlib.metadata import version

from pyshacl import validate
from rdflib import Dataset, Graph, Literal, RDF, URIRef

from build_example import HERE, PUB, ROOT, build, expand


def main():
    dataset = Dataset().parse(HERE / 'worked-example.trig', format='trig')
    manifest = json.loads((HERE / 'manifest.json').read_text())
    expected_graphs = {URIRef(manifest[k]) for k in ('sources_graph', 'candidates_graph')}
    assert {g for _, _, _, g in dataset.quads()} == expected_graphs
    rebuilt, rebuilt_manifest = build()
    repeated, _ = build()
    assert manifest == rebuilt_manifest
    assert set(dataset.quads()) == set(rebuilt.quads()) == set(repeated.quads())
    graph = Graph()
    for graph_id in expected_graphs:
        for triple in dataset.graph(graph_id):
            graph.add(triple)
    shapes = Graph().parse(HERE / 'shapes.ttl')
    conforms, report_graph, report_text = validate(
        graph, shacl_graph=shapes, inference='none', meta_shacl=True,
        do_owl_imports=False,
    )
    assert conforms, report_text

    batch = json.loads((ROOT / 'docs/experiments/e23_pouring/quality-selected.json').read_text())
    candidate = batch['candidates'][0]
    claim = graph.value(predicate=RDF.type, object=PUB.Claim, any=False)
    evidence = graph.value(claim, PUB.evidence, any=False)
    review = graph.value(claim, PUB.review, any=False)
    passage = graph.value(evidence, PUB.passage)
    grounded = graph.value(predicate=PUB.groundingStatus, object=Literal('grounded'), any=False)
    unmapped = graph.value(predicate=PUB.groundingStatus, object=Literal('needs_mapping'), any=False)
    assert str(graph.value(claim, PUB.statement)) == candidate['statement']
    quote = candidate['source_support'][0]['exact_quote']
    assert str(graph.value(evidence, PUB.exactQuote)) == quote
    assert str(graph.value(passage, PUB.text)) == batch['documents'][0]['passages'][0]['text']
    assert graph.value(unmapped, PUB.groundedClass) is None
    assert graph.value(claim, PUB.actionClass) == expand(candidate['action_class'])
    assert graph.value(claim, PUB.frameClass) == expand(candidate['frame_class'])
    for prop in (PUB.actionClass, PUB.frameClass, PUB.groundedClass):
        for subject, target in graph.subject_objects(prop):
            assert (subject, RDF.type, target) not in graph

    query = (HERE / 'queries.rq').read_text()
    bindings = {'candidateGraph': URIRef(manifest['candidates_graph']),
                'sourcesGraph': URIRef(manifest['sources_graph'])}
    rows = list(dataset.query(query, initBindings=bindings))
    assert len(rows) == 1
    assert str(rows[0].statement) == candidate['statement']
    assert str(rows[0].mappingGap) == candidate['components'][1]['description']
    assert str(rows[0].quote) == quote
    approved = list(dataset.query(query.replace('model_selected_provisional', 'human_approved'),
                                  initBindings=bindings))
    assert not approved

    results = []

    def case(name, mutate, expected=False):
        altered = Graph()
        for triple in graph:
            altered.add(triple)
        mutate(altered)
        ok, _, details = validate(altered, shacl_graph=shapes, inference='none', do_owl_imports=False)
        assert ok == expected, f'{name}: expected conforms={expected}\n{details}'
        results.append({'case': name, 'expected_conforms': expected, 'actual_conforms': bool(ok)})

    def offsets(g, start, end):
        g.set((evidence, PUB.startChar, Literal(start)))
        g.set((evidence, PUB.endChar, Literal(end)))

    # The fixture quote is the full passage; exercise end-exclusive offsets too.
    case('valid paired offsets', lambda g: offsets(g, 0, len(quote)), True)
    case('missing evidence', lambda g: g.remove((claim, PUB.evidence, None)))
    case('missing quote', lambda g: g.remove((evidence, PUB.exactQuote, None)))
    case('fabricated quote', lambda g: g.set((evidence, PUB.exactQuote, Literal('Invented test quotation.'))))
    case('missing grounded class', lambda g: g.remove((grounded, PUB.groundedClass, None)))
    case('unmapped component has class', lambda g: g.add((unmapped, PUB.groundedClass, expand('makf:GeneralizedStrategy'))))
    case('missing mapping explanation', lambda g: g.remove((unmapped, PUB.groundingNote, None)))
    case('unknown modality', lambda g: g.set((claim, PUB.modality, Literal('certain'))))
    case('empty statement', lambda g: g.set((claim, PUB.statement, Literal(''))))
    case('unpaired offset', lambda g: g.set((evidence, PUB.startChar, Literal(0))))
    case('incorrect offsets', lambda g: offsets(g, 1, len(quote)))
    case('out of bounds offsets', lambda g: offsets(g, 0, len(quote) + 1))
    case('model review relabelled human approval', lambda g: g.set((review, PUB.reviewState, Literal('human_approved'))))
    case('missing review', lambda g: g.remove((claim, PUB.review, None)))
    case('generated claim attributed to source', lambda g: g.set((claim, PUB.derivationMode, Literal('llm_proposal'))))
    case('source claim with context-only evidence', lambda g: g.set((evidence, PUB.supportRole, Literal('context_only'))))

    def wrong_document(g):
        original = g.value(evidence, PUB.document)
        other = URIRef('urn:test:other-document')
        for p, o in list(g.predicate_objects(original)):
            g.add((other, p, o))
        g.set((evidence, PUB.document, other))

    case('evidence and passage document mismatch', wrong_document)

    def external_endpoint(g):
        external, link = URIRef('urn:test:external-component'), URIRef('urn:test:link')
        for p, o in list(g.predicate_objects(grounded)):
            g.add((external, p, o))
        g.add((claim, PUB.structuralLink, link))
        g.add((link, RDF.type, PUB.StructuralLink))
        g.add((link, PUB.subjectComponent, grounded))
        g.add((link, PUB.objectComponent, external))
        g.add((link, PUB.predicate, expand('makf:concernsStrategy')))

    case('structural endpoint outside claim', external_endpoint)

    def wrong_review_target(g):
        other = URIRef('urn:test:other-claim')
        for p, o in list(g.predicate_objects(claim)):
            g.add((other, p, o))
        g.set((review, PUB.assesses, other))

    case('review targets another claim', wrong_review_target)
    report_graph.serialize(destination=HERE / 'validation-report.ttl', format='turtle')
    summary = {
        'scope': 'Draft worked fixture only; no OWL inference or scientific acceptance.',
        'pyshacl_version': version('pyshacl'), 'rdflib_version': version('rdflib'),
        'baseline_conforms': bool(conforms), 'quad_count': len(list(dataset.quads())),
        'deterministic_rebuild': True, 'fixture_fidelity_checks': 'passed',
        'query_rows_provisional': len(rows), 'query_rows_human_approved': len(approved),
        'mutation_checks': results,
    }
    (HERE / 'validation-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(f'PASS: baseline + {len(results)} mutation checks; '
          f'{len(rows)} provisional / {len(approved)} human-approved query rows; deterministic rebuild.')


if __name__ == '__main__':
    main()
