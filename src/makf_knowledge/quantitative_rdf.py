"""Provisional scalar evidence snapshots, with lossless JSON and derived issues."""
from copy import deepcopy
import hashlib
from importlib.metadata import version
import json

from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef, XSD

from .paths import resource_path
from .publication import PublicationResult, _base_iri, canonical_json, digest
from .quantitative import _decimal, validate_quantitative
from .validation import ValidationError

Q = Namespace('https://example.org/makf/quantitative/0.1#')


def _map(data, report, base):
    ds = Dataset(); ds.bind('q', Q)
    identity = digest([data, report])
    def ident(path): return URIRef(base + 'quantitative/' + digest([identity, path]))
    graph = ds.graph(ident('graph'))
    def record(path, cls, obj):
        node = ident(path)
        graph.add((node, RDF.type, Q[cls]))
        graph.add((node, Q.recordJSON, Literal(canonical_json(obj))))
        for key, value in obj.items():
            if isinstance(value, (str, int, bool)):
                graph.add((node, Q[key], Literal(value)))
        return node
    snapshot = record('snapshot', 'Snapshot', {
        'input_sha256': digest(data), 'schema_version': data['schema_version'],
        'review_state': 'pending', 'storage_eligible': True,
        'execution_eligible': False, 'comparison_ready': report['comparison_ready']})
    graph.add((snapshot, Q.inputJSON, Literal(canonical_json(data))))
    study = record('study', 'Study', data['study'])
    graph.add((snapshot, Q.study, study))
    artifacts = {}
    for artifact in data['artifacts']:
        node = record('artifact/' + artifact['artifact_id'], 'Artifact', artifact)
        artifacts[artifact['artifact_id']] = node
        graph.add((snapshot, Q.artifact, node))
    def evidence(owner, path, anchors):
        for i, anchor in enumerate(anchors):
            node = record(path + '/anchor/' + str(i), 'Anchor', anchor)
            graph.add((owner, Q.evidence, node))
            graph.add((node, Q.artifact, artifacts[anchor['artifact_id']]))
    evidence(study, 'study/context', data['study']['context']['evidence'])
    quantities = {}
    for quantity in data['quantities']:
        qid = quantity['quantity_id']; path = 'quantity/' + qid
        node = record(path, 'Quantity', quantity); quantities[qid] = node
        graph.add((snapshot, Q.quantity, node))
        graph.add((node, Q.study, study))
        decimal_text = format(_decimal(quantity['reported_value_text']), 'f')
        if '.' not in decimal_text: decimal_text += '.0'
        graph.add((node, Q.reported_decimal, Literal(decimal_text, datatype=XSD.decimal)))
        unit = record(path + '/unit', 'UnitDeclaration', quantity['unit'])
        graph.add((node, Q.unit, unit))
        for key, value in report['quantities'][qid].items():
            graph.add((node, Q[key], Literal(value)))
        evidence(node, path, quantity['evidence'])
    for i, item in enumerate(report['issues']):
        node = record('issue/' + str(i), 'Issue', item)
        graph.add((snapshot, Q.issue, node))
        for qid in item['quantity_ids']: graph.add((node, Q.affects, quantities[qid]))
    # Explicit source issue quotes and original timing/conversion specifications
    # remain lossless in inputJSON/recordJSON; derived records are separate.
    for i, item in enumerate(report['calculations']):
        node = record('calculation/' + str(i), 'TimingCalculation', item)
        graph.add((snapshot, Q.calculation, node))
        for qid in item['input_ids']: graph.add((node, Q.input, quantities[qid]))
    for item in report['conversions']:
        node = record('conversion/' + item['conversion_id'], 'Conversion', item)
        graph.add((snapshot, Q.conversion, node))
        graph.add((node, Q.input, quantities[item['input_id']]))
    return ds, {'graph_iri': str(graph.identifier), 'snapshot_iri': str(snapshot),
                'input_sha256': digest(data), 'report_sha256': digest(report), 'base_iri': base}


def validate_quantitative_rdf(dataset, manifest):
    """Check scope, JSON/RDF fidelity, recomputed numbers/eligibility, then SHACL."""
    try:
        from pyshacl import validate
    except ImportError as exc:
        raise ValidationError('Quantitative RDF requires the optional rdf extra') from exc
    graph_id = URIRef(manifest['graph_iri'])
    if {g for _, _, _, g in dataset.quads()} != {graph_id}:
        raise ValidationError('Quantitative snapshot must have exactly its named graph and an empty default graph')
    graph = dataset.graph(graph_id)
    snapshot = URIRef(manifest['snapshot_iri'])
    if set(graph.subjects(RDF.type, Q.Snapshot)) != {snapshot}:
        raise ValidationError('Expected exactly the manifest snapshot')
    from .pipeline import _parse_json
    literals = list(graph.objects(snapshot, Q.inputJSON))
    if len(literals) != 1:
        raise ValidationError('Snapshot requires one immutable source JSON record')
    try:
        data = _parse_json(str(literals[0]))
    except (ValueError, TypeError) as exc:
        raise ValidationError('Invalid quantitative source JSON') from exc
    report = validate_quantitative(data)
    rebuilt, expected_manifest = _map(data, report, _base_iri(manifest['base_iri']))
    if any(manifest.get(k) != v for k, v in expected_manifest.items()):
        raise ValidationError('Quantitative manifest identity/digests do not match source data')
    if set(rebuilt.quads()) != set(dataset.quads()):
        raise ValidationError('Quantitative RDF differs from validated source mapping')
    shapes = Graph().parse(resource_path('quantitative', 'shapes.ttl'))
    conforms, results, text = validate(graph, shacl_graph=shapes, inference='none', do_owl_imports=False)
    if not conforms: raise ValidationError('Quantitative SHACL failed: ' + text)
    return results


def export_quantitative(data: dict, *, base_iri: str) -> PublicationResult:
    data = deepcopy(data)
    base = _base_iri(base_iri)
    report = validate_quantitative(data)
    dataset, manifest = _map(data, report, base)
    serialized = dataset.serialize(format='trig')
    parsed = Dataset().parse(data=serialized, format='trig')
    results = validate_quantitative_rdf(parsed, manifest)
    artifacts = [('dataset.trig', serialized), ('evidence.json', canonical_json(data) + '\n'),
        ('validation.json', json.dumps(report, indent=2) + '\n'),
        ('shacl-report.ttl', results.serialize(format='turtle'))]
    manifest.update(contract_version='quantitative-rdf-0.1', quantity_count=len(data['quantities']),
        triple_count=len(list(dataset.quads())), review_state='pending', shacl_conforms=True,
        dependencies={name: version(name) for name in ('rdflib', 'pyshacl')},
        resources_sha256={name: hashlib.sha256(resource_path('quantitative', name).read_bytes()).hexdigest()
                          for name in ('schema.json', 'shapes.ttl', 'vocabulary.ttl')},
        files_sha256={name: hashlib.sha256(text.encode()).hexdigest() for name, text in artifacts},
        scope='Provisional quantitative records; no scientific approval or execution eligibility.')
    return PublicationResult(tuple(artifacts), json.dumps(manifest, indent=2) + '\n')
