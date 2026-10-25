"""Rebuild this one worked fixture; not a production publication API."""
import hashlib
import json
from pathlib import Path
from rdflib import Dataset, Graph, Namespace, RDF, RDFS, Literal, URIRef, XSD

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PUB = Namespace('https://example.org/makf/publication/0.1#')
BASE = 'https://example.org/makf/data/'
PROV = Namespace('http://www.w3.org/ns/prov#')
DCT = Namespace('http://purl.org/dc/terms/')
PREFIXES = {'makf': 'https://w3id.org/aicor/makf#', 'paf': 'https://w3id.org/aicor/pouring-frame#',
            'gsf': 'https://w3id.org/aicor/grasping-smoke#', 'aicor': 'http://aicor.knowledge/l2-ontology.owl#',
            'dul': 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def ident(kind, value): return URIRef(BASE + kind + '/' + digest(value))
def expand(value):
    prefix, local = value.split(':', 1)
    return URIRef(PREFIXES[prefix] + local)

def build():
    batch = json.loads((ROOT / 'docs/experiments/e23_pouring/quality-selected.json').read_text())
    evaluation = json.loads((ROOT / 'docs/experiments/e23_pouring/quality-evaluation.json').read_text())
    assessment = evaluation['selection']
    assert assessment['status'] == 'model_reviewed_subset'
    assert assessment['human_review_required'] is True
    assert set(assessment['selected_candidate_ids']) == {c['candidate_id'] for c in batch['candidates']}
    ds = Dataset()
    for p, n in [('pub', PUB), ('prov', PROV), ('dct', DCT), *PREFIXES.items()]: ds.bind(p, n)
    sg = ds.graph(ident('sources-graph', ['0.1', batch]))
    cg = ds.graph(ident('candidates-graph', ['0.1', batch, digest(assessment)]))
    b = ident('batch', batch)
    def val(g, node, prop, value, datatype=None):
        g.add((node, prop, Literal(value, datatype=datatype)))
    cg.add((b, RDF.type, PUB.Batch))
    val(cg,b,PUB.batchId,batch['batch_id']); val(cg,b,PUB.profileId,batch['profile_id'])
    doc_ids, passage_ids = {}, {}
    for d in batch['documents']:
        node = ident('source', d); doc_ids[d['document_id']] = node
        sg.add((node, RDF.type, PUB.SourceSnapshot)); cg.add((b,PUB.document,node))
        for key, prop in [('document_id',PUB.documentId),('title',DCT.title),('uri',PUB.sourceURI),('doi',PUB.doi),('synthetic_demo',PUB.syntheticDemo)]:
            if key in d: val(sg,node,prop,d[key])
        for p in d['passages']:
            pn = ident('passage', [str(node),p]); passage_ids[(d['document_id'],p['passage_id'])] = pn
            sg.add((pn,RDF.type,PUB.Passage)); sg.add((pn,PUB.document,node)); sg.add((node,PUB.passage,pn))
            for key,prop in [('passage_id',PUB.passageId),('text',PUB.text),('locator',PUB.locator)]:
                if key in p: val(sg,pn,prop,p[key])
    run = None
    if 'extraction_run' in batch:
        r = batch['extraction_run']; run = ident('run',r)
        cg.add((run,RDF.type,PUB.ExtractionRun)); cg.add((run,RDF.type,PROV.Activity))
        for key,prop in [('engine',PUB.engine),('model_name',PUB.modelName),('prompt_version',PUB.promptVersion)]:
            if key in r: val(cg,run,prop,r[key])
        if 'recorded_at' in r: val(cg,run,PUB.recordedAt,r['recorded_at'],XSD.dateTime)
    for c in batch['candidates']:
        claim = ident('claim', [c,batch['profile_id'],sorted(map(str,doc_ids.values()))])
        cg.add((claim,RDF.type,PUB.Claim)); cg.add((b,PUB.claim,claim))
        if run: cg.add((claim,PROV.wasGeneratedBy,run))
        for key,prop in [('candidate_id',PUB.candidateId),('statement',PUB.statement),('knowledge_kind',PUB.knowledgeKind),
                         ('modality',PUB.modality),('epistemic_status',PUB.epistemicStatus),('derivation_mode',PUB.derivationMode),
                         ('evidence_status',PUB.evidenceStatus),('reviewer_note',PUB.reviewerNote)]:
            if key in c: val(cg,claim,prop,c[key])
        for perspective in c['perspectives']: val(cg,claim,PUB.perspective,perspective)
        cg.add((claim,PUB.actionClass,expand(c['action_class']))); cg.add((claim,PUB.frameClass,expand(c['frame_class'])))
        components = {}
        for comp in c['components']:
            node = ident('component',[str(claim),comp]); components[comp['component_id']] = node
            cg.add((node,RDF.type,PUB.Component)); cg.add((claim,PUB.hasComponent,node))
            for key,prop in [('component_id',PUB.componentId),('component_kind',PUB.componentKind),('description',PUB.description),
                             ('grounding_status',PUB.groundingStatus),('grounding_note',PUB.groundingNote)]:
                if key in comp: val(cg,node,prop,comp[key])
            if 'ontology_class' in comp: cg.add((node,PUB.groundedClass,expand(comp['ontology_class'])))
        for link in c.get('structural_links',[]):
            node = ident('link',[str(claim),link]); cg.add((node,RDF.type,PUB.StructuralLink)); cg.add((claim,PUB.structuralLink,node))
            cg.add((node,PUB.subjectComponent,components[link['subject_component']]))
            cg.add((node,PUB.objectComponent,components[link['object_component']]))
            cg.add((node,PUB.predicate,expand(link['predicate_curie'])))
        for support in c['source_support']:
            node = ident('evidence',[str(claim),support]); cg.add((node,RDF.type,PUB.EvidenceAnchor)); cg.add((claim,PUB.evidence,node))
            cg.add((node,PUB.document,doc_ids[support['document_id']]))
            cg.add((node,PUB.passage,passage_ids[(support['document_id'],support['passage_id'])]))
            for key,prop in [('exact_quote',PUB.exactQuote),('support_role',PUB.supportRole),('start_char',PUB.startChar),('end_char',PUB.endChar)]:
                if key in support: val(cg,node,prop,support[key])
        review = ident('review',[str(claim),digest(assessment)])
        cg.add((review,RDF.type,PUB.Review)); cg.add((claim,PUB.review,review)); cg.add((review,PUB.assesses,claim))
        val(cg,review,PUB.reviewState,'model_selected_provisional'); val(cg,review,PUB.reviewerKind,'model')
        val(cg,review,PUB.artifactSha256,digest(assessment))
        val(cg,review,PUB.artifactPath,'docs/experiments/e23_pouring/quality-evaluation.json#selection')
    return ds, {'sources_graph':str(sg.identifier),'candidates_graph':str(cg.identifier),'input_sha256':digest(batch),
                'assessment_sha256':digest(assessment),'contract_version':'draft-0.1'}

if __name__ == '__main__':
    ds,manifest=build()
    ds.serialize(destination=HERE/'worked-example.trig',format='trig')
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    vocab=Graph(); vocab.bind('pub',PUB)
    for cls in ['Batch','SourceSnapshot','Passage','Claim','Component','EvidenceAnchor','StructuralLink','ExtractionRun','Review']:
        vocab.add((PUB[cls],RDF.type,RDFS.Class)); vocab.add((PUB[cls],RDFS.comment,Literal('Draft 0.1 publication record; not a physical event.')))
    for _,p,_,_ in ds.quads():
        if str(p).startswith(str(PUB)): vocab.add((p,RDF.type,RDF.Property))
    for prop in ['structuralLink','subjectComponent','objectComponent','predicate','reviewerNote','startChar','endChar','doi']:
        vocab.add((PUB[prop],RDF.type,RDF.Property))
    vocab.serialize(destination=HERE/'vocabulary.ttl',format='turtle')
    print('Built worked fixture with',sum(1 for _ in ds.quads()),'quads')
