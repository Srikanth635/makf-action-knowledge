"""Regression checks carried forward from P1.3; asserted axioms, not DL proof."""
import csv
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL
from makf_knowledge.paths import resource_path
from makf_knowledge.ontology import ontology_graph

A='http://aicor.knowledge/l2-ontology.owl#'
M='https://w3id.org/aicor/makf#'
P='https://w3id.org/aicor/pouring-frame#'
GS='https://w3id.org/aicor/grasping-smoke#'
DUL='http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#'


def restrictions(g,cls):
    result={}
    for v in g.objects(URIRef(cls),RDFS.subClassOf):
        if isinstance(v,BNode):
            p=g.value(v,OWL.onProperty)
            c=g.value(v,OWL.someValuesFrom)
            if p and c:result[str(p)]=str(c)
    return result


def test_dependency_chain():
    g=ontology_graph()
    imports=lambda iri:{str(x) for x in g.objects(URIRef(iri),OWL.imports)}
    assert imports('https://w3id.org/aicor/dul-alignment')=={'http://aicor.knowledge/l2-ontology.owl','http://www.ontologydesignpatterns.org/ont/dul/DUL.owl'}
    assert imports('https://w3id.org/aicor/makf')=={'https://w3id.org/aicor/dul-alignment'}
    assert imports('https://w3id.org/aicor/pouring-frame')=={'https://w3id.org/aicor/makf'}
    assert imports('https://w3id.org/aicor/grasping-smoke')=={'https://w3id.org/aicor/makf'}


def test_generic_makf_is_action_neutral():
    g=Graph().parse(resource_path('ontology','makf-core.ttl'),format='turtle')
    assert not any('pouring' in str(x).lower() or 'grasping' in str(x).lower() for t in g for x in t)
    assert (URIRef(M+'ActingHypothesis'),RDFS.subClassOf,URIRef(A+'Hypothesis')) in g


def test_pouring_grasping_share_perspectives():
    g=ontology_graph()
    expected={'hasActionCategory','hasRolePerspective','hasIntentionalPerspective','hasCausalPerspective','hasTemporalPerspective','hasProceduralPerspective','hasObservationalPerspective','hasHypothesisPerspective','hasDeviationPerspective','hasApplicabilityPerspective'}
    for fr,action in ((P+'PouringKnowledgeFrame',A+'Pouring'),(GS+'GraspingKnowledgeFrame',A+'Grasping')):
        r=restrictions(g,fr)
        assert {M+x for x in expected} <= set(r)
        assert r[M+'hasActionCategory']==action


def test_no_named_world_individuals():
    for name in ('makf-core.ttl','pouring-frame.ttl','grasping-smoke.ttl','dul-alignment.ttl'):
        g=Graph().parse(resource_path('ontology',name),format='turtle')
        assert not list(g.subjects(RDF.type,OWL.NamedIndividual))
        assert not any('soma' in str(x).lower() for t in g for x in t)


def test_dul_bridge_is_not_unsafe_event_equivalence():
    g=Graph().parse(resource_path('ontology','dul-alignment.ttl'),format='turtle')
    assert (URIRef(A+'dul_Description'),RDFS.subClassOf,URIRef(DUL+'Description')) in g
    assert (URIRef(A+'dul_Event'),RDFS.subClassOf,URIRef(DUL+'Event')) not in g
    assert not list(g.triples((None,OWL.equivalentClass,None)))


def test_version_collision_documented_by_raw_files():
    a=Graph().parse(resource_path('ontology','aicor-ontology.ttl'),format='turtle')
    c=Graph().parse(resource_path('ontology','cram-aicor-ontology.ttl'),format='turtle')
    iri=URIRef('http://aicor.knowledge/l2-ontology.owl')
    assert (iri,RDF.type,OWL.Ontology) in a
    assert (iri,RDF.type,OWL.Ontology) in c
    assert len(c)>len(a)


def test_p12_migration_targets_declare_symbols():
    import pathlib
    path=resource_path('reports','p1_3','migration_map.csv')
    with path.open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==69
    g=ontology_graph()
    for row in rows:
        target=URIRef(row['new_iri'])
        assert (target,RDF.type,OWL.Class) in g or (target,RDF.type,OWL.ObjectProperty) in g
