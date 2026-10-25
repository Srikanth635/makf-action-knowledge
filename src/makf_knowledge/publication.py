"""Offline E1-to-RDF snapshots. Validation is not scientific or human approval."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef, XSD

from .guidance import load_profile
from .paths import RESOURCE_ROOT, profile_path
from .pipeline import _parse_json
from .validation import ONTOLOGIES, SemanticValidator, ValidationError

PUB = Namespace('https://example.org/makf/publication/0.1#')
PROV = Namespace('http://www.w3.org/ns/prov#')
DCT = Namespace('http://purl.org/dc/terms/')
CONTRACT_VERSION = 'draft-0.1'


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


def read_json(path: str | Path) -> dict:
    """Reject duplicate keys/non-finite numbers, including in assessment artifacts."""
    value = _parse_json(Path(path).read_bytes().decode('utf-8'))
    if not isinstance(value, dict):
        raise ValidationError('Expected a JSON object')
    return value


def _base_iri(value: str) -> str:
    url = urlsplit(value)
    if (url.scheme not in {'http', 'https'} or not url.hostname or url.query or url.fragment
            or url.username is not None or url.password is not None
            or re.search(r'[\s<>"{}|\\^`\x00-\x1f\x7f]', value)):
        raise ValidationError('Data base must be an absolute HTTP(S) IRI without credentials, query or fragment')
    return value.rstrip('/') + '/'


def _assessment(batch: dict, selection: dict | None, reviewed_batch: dict | None) -> tuple[dict, str, str]:
    if selection is None:
        if reviewed_batch is not None:
            raise ValidationError('A reviewed batch requires a selection manifest')
        return ({'status': 'pending', 'input_sha256': digest(batch),
                 'scope': 'Export recorded without an attached review decision.'}, 'pending', 'system')
    required = {'status', 'selected_candidate_ids', 'withheld_candidate_ids',
                'reviewed_batch_sha256', 'review_response_sha256', 'human_review_required', 'scope'}
    if set(selection) != required or selection['status'] != 'model_reviewed_subset' or selection['human_review_required'] is not True:
        raise ValidationError('Only an advisory model selection manifest is supported; human promotion is unavailable')
    for key in ('reviewed_batch_sha256', 'review_response_sha256'):
        if not isinstance(selection[key], str) or not re.fullmatch('[0-9a-f]{64}', selection[key]):
            raise ValidationError('Selection requires SHA-256 review artifact identifiers')
    if not isinstance(selection['scope'], str) or not selection['scope'].strip():
        raise ValidationError('Selection scope must be nonempty')
    for key in ('selected_candidate_ids', 'withheld_candidate_ids'):
        values = selection[key]
        if (not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values)
                or len(values) != len(set(values))):
            raise ValidationError('Selection IDs must be unique strings')
    if reviewed_batch is None:
        raise ValidationError('Model selection requires the original reviewed batch to bind the decision to content')
    # E2 selection hashes predate the compact canonical JSON used for RDF identities.
    reviewed_digest = hashlib.sha256(json.dumps(
        reviewed_batch, sort_keys=True, ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()
    if reviewed_digest != selection['reviewed_batch_sha256']:
        raise ValidationError('Selection does not match the reviewed batch digest')
    selected, withheld = set(selection['selected_candidate_ids']), set(selection['withheld_candidate_ids'])
    original_ids = [c['candidate_id'] for c in reviewed_batch['candidates']]
    if (not selected or selected & withheld or selected | withheld != set(original_ids)
            or len(original_ids) != len(set(original_ids))):
        raise ValidationError('Selection must partition the original candidate IDs')
    expected = deepcopy(reviewed_batch)
    expected['candidates'] = [c for c in expected['candidates'] if c['candidate_id'] in selected]
    if canonical_json(expected) != canonical_json(batch):
        raise ValidationError('Selected batch must preserve the reviewed candidates, order, sources and audit metadata')
    return deepcopy(selection), 'model_selected_provisional', 'model'


def _map_batch(batch: dict, assessment: dict, state: str, reviewer: str,
               validator: SemanticValidator, base: str) -> tuple[Dataset, dict]:
    def ident(kind, value):
        return URIRef(base + kind + '/' + digest(value))

    def values(graph, node, obj, mapping):
        for key, prop in mapping:
            if key in obj:
                graph.add((node, prop, Literal(obj[key])))

    ds = Dataset()
    for prefix, ns in [('pub', PUB), ('prov', PROV), ('dct', DCT), *validator.prefixes.items()]:
        ds.bind(prefix, ns)
    sources = ds.graph(ident('sources-graph', ['0.1', batch]))
    candidates = ds.graph(ident('candidates-graph', ['0.1', batch, digest(assessment)]))
    batch_node = ident('batch', batch)
    candidates.add((batch_node, RDF.type, PUB.Batch))
    values(candidates, batch_node, batch, [('batch_id', PUB.batchId), ('profile_id', PUB.profileId)])
    documents, passages = {}, {}
    for doc in batch['documents']:
        node = ident('source', doc)
        documents[doc['document_id']] = node
        sources.add((node, RDF.type, PUB.SourceSnapshot))
        candidates.add((batch_node, PUB.document, node))
        values(sources, node, doc, [('document_id', PUB.documentId), ('title', DCT.title),
            ('uri', PUB.sourceURI), ('doi', PUB.doi), ('synthetic_demo', PUB.syntheticDemo)])
        for passage in doc['passages']:
            pn = ident('passage', [str(node), passage])
            passages[(doc['document_id'], passage['passage_id'])] = pn
            sources.add((pn, RDF.type, PUB.Passage))
            sources.add((pn, PUB.document, node))
            sources.add((node, PUB.passage, pn))
            values(sources, pn, passage, [('passage_id', PUB.passageId), ('text', PUB.text), ('locator', PUB.locator)])
    run = None
    if 'extraction_run' in batch:
        audit = batch['extraction_run']
        run = ident('run', audit)
        candidates.add((run, RDF.type, PUB.ExtractionRun))
        candidates.add((run, RDF.type, PROV.Activity))
        values(candidates, run, audit, [('engine', PUB.engine), ('model_name', PUB.modelName), ('prompt_version', PUB.promptVersion)])
        if 'recorded_at' in audit:
            candidates.add((run, PUB.recordedAt, Literal(audit['recorded_at'], datatype=XSD.dateTime)))
    for candidate in batch['candidates']:
        claim = ident('claim', [candidate, batch['profile_id'], sorted(map(str, documents.values()))])
        candidates.add((batch_node, PUB.claim, claim))
        candidates.add((claim, RDF.type, PUB.Claim))
        if run is not None:
            candidates.add((claim, PROV.wasGeneratedBy, run))
        values(candidates, claim, candidate, [('candidate_id', PUB.candidateId), ('statement', PUB.statement),
            ('knowledge_kind', PUB.knowledgeKind), ('modality', PUB.modality), ('epistemic_status', PUB.epistemicStatus),
            ('derivation_mode', PUB.derivationMode), ('evidence_status', PUB.evidenceStatus), ('reviewer_note', PUB.reviewerNote)])
        for perspective in candidate['perspectives']:
            candidates.add((claim, PUB.perspective, Literal(perspective)))
        candidates.add((claim, PUB.actionClass, validator.uri(candidate['action_class'])))
        candidates.add((claim, PUB.frameClass, validator.uri(candidate['frame_class'])))
        components = {}
        for comp in candidate['components']:
            node = ident('component', [str(claim), comp])
            components[comp['component_id']] = node
            candidates.add((node, RDF.type, PUB.Component))
            candidates.add((claim, PUB.hasComponent, node))
            values(candidates, node, comp, [('component_id', PUB.componentId), ('component_kind', PUB.componentKind),
                ('description', PUB.description), ('grounding_status', PUB.groundingStatus), ('grounding_note', PUB.groundingNote)])
            if 'ontology_class' in comp:
                candidates.add((node, PUB.groundedClass, validator.uri(comp['ontology_class'])))
        for link in candidate.get('structural_links', []):
            node = ident('link', [str(claim), link])
            candidates.add((node, RDF.type, PUB.StructuralLink))
            candidates.add((claim, PUB.structuralLink, node))
            candidates.add((node, PUB.subjectComponent, components[link['subject_component']]))
            candidates.add((node, PUB.objectComponent, components[link['object_component']]))
            candidates.add((node, PUB.predicate, validator.uri(link['predicate_curie'])))
        for support in candidate['source_support']:
            node = ident('evidence', [str(claim), support])
            candidates.add((node, RDF.type, PUB.EvidenceAnchor))
            candidates.add((claim, PUB.evidence, node))
            candidates.add((node, PUB.document, documents[support['document_id']]))
            candidates.add((node, PUB.passage, passages[(support['document_id'], support['passage_id'])]))
            values(candidates, node, support, [('exact_quote', PUB.exactQuote), ('support_role', PUB.supportRole),
                ('start_char', PUB.startChar), ('end_char', PUB.endChar)])
        review = ident('review', [str(claim), digest(assessment)])
        candidates.add((review, RDF.type, PUB.Review))
        candidates.add((claim, PUB.review, review))
        candidates.add((review, PUB.assesses, claim))
        candidates.add((review, PUB.reviewState, Literal(state)))
        candidates.add((review, PUB.reviewerKind, Literal(reviewer)))
        candidates.add((review, PUB.artifactSha256, Literal(digest(assessment))))
        candidates.add((review, PUB.artifactPath, Literal('assessment.json')))
    return ds, {'sources_graph': str(sources.identifier), 'candidates_graph': str(candidates.identifier),
                'input_sha256': digest(batch), 'assessment_sha256': digest(assessment),
                'contract_version': CONTRACT_VERSION, 'data_base_iri': base}


def validate_dataset(dataset: Dataset, manifest: dict, *, root=RESOURCE_ROOT) -> tuple[Graph, str]:
    """SHACL for exactly one export closure; not an arbitrary RDF importer or E1 replacement."""
    try:
        from pyshacl import validate
    except ImportError as exc:
        raise ValidationError('RDF export requires the optional dependency: pip install "makf-action-knowledge[rdf]"') from exc
    expected = {URIRef(manifest[key]) for key in ('sources_graph', 'candidates_graph')}
    actual = {g for _, _, _, g in dataset.quads()}
    if len(expected) != 2 or actual != expected:
        raise ValidationError('RDF snapshot must contain exactly its two named graphs, with an empty default graph')
    closure = Graph()
    for graph_id in expected:
        for triple in dataset.graph(graph_id):
            closure.add(triple)
    source_types = {PUB.SourceSnapshot, PUB.Passage}
    for subject, rdf_type in closure.subject_objects(RDF.type):
        if str(rdf_type).startswith(str(PUB)):
            home = manifest['sources_graph' if rdf_type in source_types else 'candidates_graph']
            for quad in dataset.quads((subject, None, None, None)):
                if str(quad[3]) != home:
                    raise ValidationError('Record properties crossed source/candidate graph boundaries')
    shapes = Graph().parse(Path(root) / 'publication/shapes.ttl', format='turtle')
    conforms, report, text = validate(closure, shacl_graph=shapes, inference='none', do_owl_imports=False)
    if not conforms:
        raise ValidationError('RDF SHACL validation failed: ' + text)
    return report, text


@dataclass(frozen=True)
class PublicationResult:
    """Immutable serialized artifacts; manifest.json is the bundle completion marker."""
    artifacts: tuple[tuple[str, str], ...]
    manifest_json: str

    def save(self, directory: str | Path) -> None:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=False, mode=0o700)
        try:
            for name, text in self.artifacts:
                (target / name).write_bytes(text.encode('utf-8'))
            # Consumers must ignore a bundle without this atomically installed marker.
            marker = target / '.manifest.tmp'
            marker.write_bytes(self.manifest_json.encode('utf-8'))
            marker.replace(target / 'manifest.json')
        except BaseException:
            shutil.rmtree(target)
            raise


def export_batch(batch: dict, *, base_iri: str, profile: str | Path = 'pouring',
                 selection: dict | None = None, reviewed_batch: dict | None = None,
                 root=RESOURCE_ROOT) -> PublicationResult:
    """Validate E1 + local ontology + RDF, then prepare a local provisional snapshot.

    No remote imports, source fetches, model calls, or human approval promotion.
    Selection manifests require the original batch; review remains advisory.
    """
    base = _base_iri(base_iri)
    batch, selection, reviewed_batch = deepcopy((batch, selection, reviewed_batch))
    validator = SemanticValidator(root)
    path = (Path(root) / 'profiles' / profile_path(str(profile)).name
            if str(profile) in {'pouring', 'grasping'} else Path(profile))
    loaded_profile = load_profile(path, validator)
    e1_report = validator.validate_batch(batch, loaded_profile)
    if reviewed_batch is not None:
        validator.validate_batch(reviewed_batch, loaded_profile)
    assessment, state, reviewer = _assessment(batch, selection, reviewed_batch)
    dataset, manifest = _map_batch(batch, assessment, state, reviewer, validator, base)
    report, _ = validate_dataset(dataset, manifest, root=root)
    # Exercise serialization too; all checks complete before any output is created.
    serialized = dataset.serialize(format='trig')
    parsed = Dataset().parse(data=serialized, format='trig')
    if set(parsed.quads()) != set(dataset.quads()):
        raise ValidationError('RDF serialization did not preserve the mapped dataset')
    artifacts = [('dataset.trig', serialized), ('candidates.json', canonical_json(batch) + '\n'),
                 ('assessment.json', canonical_json(assessment) + '\n'),
                 ('validation.json', json.dumps({'e1': e1_report, 'shacl_conforms': True}, indent=2) + '\n'),
                 ('shacl-report.ttl', report.serialize(format='turtle'))]
    if reviewed_batch is not None:
        artifacts.append(('reviewed-batch.json', canonical_json(reviewed_batch) + '\n'))
    resource_names = [f'ontology/{name}' for name in ONTOLOGIES] + [
        'schema/makf_extraction.linkml.yaml', 'publication/shapes.ttl', 'publication/vocabulary.ttl']
    manifest.update(review_state=state, candidate_count=len(batch['candidates']),
        quad_count=len(list(dataset.quads())), shacl_conforms=True,
        dependencies={name: version(name) for name in ('rdflib', 'pyshacl')},
        profile_sha256=digest(loaded_profile),
        resource_sha256={name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in resource_names},
        files_sha256={name: hashlib.sha256(text.encode('utf-8')).hexdigest() for name, text in artifacts},
        scope='Local provisional RDF records; no scientific acceptance, human promotion or OWL inference.')
    return PublicationResult(tuple(artifacts), json.dumps(manifest, indent=2) + '\n')
