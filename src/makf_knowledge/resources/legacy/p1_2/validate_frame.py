#!/usr/bin/env python3
"""Lightweight syntactic/integrity validation, explicitly NOT OWL DL reasoning."""
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef

D=Path(__file__).resolve().parent
base=Graph().parse(D.parent/'aicor-ontology.ttl')
cram=Graph().parse(D.parent/'cram-aicor-ontology.ttl')
frame=Graph().parse(D/'pouring-frame.ttl')
bridge=Graph().parse(D/'dul-alignment.ttl')
PAF=Namespace('https://w3id.org/aicor/pouring-frame#')
A=Namespace('http://aicor.knowledge/l2-ontology.owl#')
DUL=Namespace('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#')

assert all((t, RDF.type, OWL.Ontology) in frame for t in [URIRef('https://w3id.org/aicor/pouring-frame')])
assert len(list(frame.subjects(RDF.type,OWL.NamedIndividual)))==0
assert len(list(bridge.subjects(RDF.type,OWL.NamedIndividual)))==0
assert len(set(frame.subjects(RDF.type,OWL.Class)))>=30
assert len(set(frame.subjects(RDF.type,OWL.ObjectProperty)))>=25
assert (URIRef('https://w3id.org/aicor/pouring-frame'),OWL.imports,URIRef('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl')) in frame
assert (URIRef('https://w3id.org/aicor/pouring-frame'),OWL.imports,URIRef('http://aicor.knowledge/l2-ontology.owl')) in frame
assert (A.dul_Description,RDFS.subClassOf,DUL.Description) in bridge
assert (A.dul_Concept,RDFS.subClassOf,DUL.Concept) in bridge
assert (A.ParticipantRole,RDFS.subClassOf,DUL.Role) in bridge
assert (A.dul_Event,RDFS.subClassOf,DUL.Event) not in bridge
assert not list(bridge.triples((None,OWL.equivalentClass,None)))
assert (PAF.PouringKnowledgeFrame,RDFS.subClassOf,A.ManipulationFrame) not in frame
assert (PAF.PouringActingHypothesis,RDFS.subClassOf,A.ManipulationHypothesis) not in frame
assert (PAF.PouringActingHypothesis,RDFS.subClassOf,A.Hypothesis) in frame
assert not list(frame.triples((None,OWL.sameAs,None)))

# Validate AICOR IRIs in extension occur as named terms in the expanded source.
source_terms=set(cram.subjects(RDF.type,OWL.Class)) | set(cram.subjects(RDF.type,OWL.ObjectProperty)) | set(cram.subjects(RDF.type,OWL.DatatypeProperty))
for s,p,o in frame:
    for term in (s,p,o):
        if isinstance(term,URIRef) and str(term).startswith(str(A)):
            assert term in source_terms or (term,p,RDF.type) in cram, f'Unknown AICOR term: {term}'

required={
    PAF.hasActionCategory,PAF.hasRolePerspective,PAF.hasIntentionalPerspective,
    PAF.hasCausalPerspective,PAF.hasTemporalPerspective,PAF.hasProceduralPerspective,
    PAF.hasObservationalPerspective,PAF.hasHypothesisPerspective,
    PAF.hasDeviationPerspective,PAF.hasApplicabilityPerspective
}
restrictions=set()
for r in frame.objects(PAF.PouringKnowledgeFrame,RDFS.subClassOf):
    if (r,RDF.type,OWL.Restriction) in frame: restrictions.add(frame.value(r,OWL.onProperty))
assert required.issubset(restrictions)

# Nothing in this module tries to model a physical instance by a new class
# inheriting official dul:Event/Situation/Action.
assert not list(frame.triples((None,RDFS.subClassOf,DUL.Event)))
assert not list(frame.triples((None,RDFS.subClassOf,DUL.Action)))
assert not list(frame.triples((None,RDFS.subClassOf,DUL.Situation)))
assert not any('soma' in str(t).lower() for g in (frame,bridge) for triple in g for t in triple)

print('PASS: Turtle parsed; baseline class/property IRIs verified; DUL import present;')
print('      eight perspectives plus applicability; no named world instances;')
print('      no unreviewed AICOR-DUL event equivalences.')
print(f'      AICOR: {len(base)} triples; CRAM-AICOR: {len(cram)} triples;')
print(f'      pouring frame: {len(frame)} triples; bridge: {len(bridge)} triples.')
print('LIMIT: Not an OWL 2 DL consistency or satisfiability proof. Resolve and run imported DUL with a DL reasoner before publication.')
