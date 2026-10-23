"""Offline ontology inspection and direct OWL restriction lookup.

Only explicit asserted axioms are reported. Import resolution and reasoning are out of scope.
"""
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS
from .paths import RESOURCE_ROOT

ACTIVE = ('cram-aicor-ontology.ttl','dul-alignment.ttl','makf-core.ttl','pouring-frame.ttl','grasping-smoke.ttl')
ALL = ('aicor-ontology.ttl',) + ACTIVE

def list_ontologies():
    results=[]
    for name in ALL:
        g=Graph().parse(RESOURCE_ROOT/'ontology'/name,format='turtle')
        identifiers=sorted(str(s) for s in g.subjects(RDF.type,OWL.Ontology))
        results.append(dict(filename=name,iris=identifiers,triples=len(g),classes=len(set(g.subjects(RDF.type,OWL.Class))),object_properties=len(set(g.subjects(RDF.type,OWL.ObjectProperty))),datatype_properties=len(set(g.subjects(RDF.type,OWL.DatatypeProperty))),active=name in ACTIVE))
    return results

def ontology_graph(names=ACTIVE):
    g=Graph()
    for name in names:
        if name not in ALL:
            raise ValueError(f'Unknown ontology resource: {name}')
        g.parse(RESOURCE_ROOT/'ontology'/name,format='turtle')
    return g

def describe_class(term, graph=None):
    """Return directly asserted superclasses and existential restrictions for a CURIE/IRI."""
    g=graph if graph is not None else ontology_graph()
    prefixes={'aicor':'http://aicor.knowledge/l2-ontology.owl#',
              'makf':'https://w3id.org/aicor/makf#',
              'paf':'https://w3id.org/aicor/pouring-frame#',
              'gsf':'https://w3id.org/aicor/grasping-smoke#',
              'dul':'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#'}
    if ':' in term and not term.startswith('http'):
        p,local=term.split(':',1)
        if p not in prefixes:raise ValueError(f'Unsupported prefix: {p}')
        iri=URIRef(prefixes[p]+local)
    else: iri=URIRef(term)
    if (iri,RDF.type,OWL.Class) not in g:
        raise ValueError(f'Class not explicitly declared in local loaded ontology: {term}')
    parents=[]; restrictions=[]
    for anc in g.objects(iri,RDFS.subClassOf):
        if isinstance(anc, URIRef): parents.append(str(anc))
        elif isinstance(anc,BNode):
            prop=g.value(anc,OWL.onProperty); target=g.value(anc,OWL.someValuesFrom)
            if prop is not None and target is not None:
                restrictions.append({'predicate':str(prop),'some_values_from':str(target)})
    return {'class':str(iri),'parents':sorted(set(parents)),
            'some_values_from':sorted(restrictions,key=lambda x:(x['predicate'],x['some_values_from'])),
            'scope':'direct asserted OWL restrictions only, not inferred'}
