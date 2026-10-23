#!/usr/bin/env python3
"""Parse, topology, migration and declared-restriction tests; no claim of OWL DL reasoning."""
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
from xml.etree import ElementTree as ET
import csv, json

D=Path(__file__).resolve().parents[1]; M=Namespace('https://w3id.org/aicor/makf#')
P=Namespace('https://w3id.org/aicor/pouring-frame#');G=Namespace('https://w3id.org/aicor/grasping-smoke#')
A=Namespace('http://aicor.knowledge/l2-ontology.owl#')
DUL=Namespace('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#')
files={
  'source':D/'sources/cram-aicor-ontology.ttl',
  'base':D/'sources/aicor-ontology.ttl',
  'bridge':D/'ontologies/dul-alignment.ttl',
  'core':D/'ontologies/makf-core.ttl',
  'pouring':D/'ontologies/pouring-frame.ttl',
  'grasping':D/'ontologies/grasping-smoke.ttl',
  'legacy':D/'legacy/pouring-frame.v0.1.ttl'
}
t={k:Graph().parse(v,format='turtle') for k,v in files.items()}
def check(cond,msg):
    if not cond: raise AssertionError(msg)
def subset_restrictions(cls,graph):
    return {(graph.value(r,OWL.onProperty),graph.value(r,OWL.someValuesFrom))
            for r in graph.objects(cls,RDFS.subClassOf)
            if (r,RDF.type,OWL.Restriction) in graph}

# Import chain is acyclic, independent of the base-file collision.
iri={
  'source':URIRef('http://aicor.knowledge/l2-ontology.owl'),
  'bridge':URIRef('https://w3id.org/aicor/dul-alignment'),
  'core':URIRef('https://w3id.org/aicor/makf'),
  'pouring':URIRef('https://w3id.org/aicor/pouring-frame'),
  'grasping':URIRef('https://w3id.org/aicor/grasping-smoke')
}
for name,v in iri.items(): check((v,RDF.type,OWL.Ontology) in t[name], f'ontology IRI missing {name}')
check(set(t['bridge'].objects(iri['bridge'],OWL.imports))=={iri['source'],URIRef('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl')},'bridge imports')
check(set(t['core'].objects(iri['core'],OWL.imports))=={iri['bridge']},'core imports')
for name in ('pouring','grasping'):
    check(set(t[name].objects(iri[name],OWL.imports))=={iri['core']},f'{name} imports')

# No named world individuals; core has no action-specific names or import.
for name in ('bridge','core','pouring','grasping'):
  graph=t[name]
  check(not list(graph.subjects(RDF.type,OWL.NamedIndividual)),f'{name} has named individuals')
  check(not list(graph.triples((None,OWL.sameAs,None))),f'{name} sameAs asserted')
  check(not any('soma' in str(x).lower() for tr in graph for x in tr),f'{name} mentions SOMA')
  check(not list(graph.triples((None,RDFS.subClassOf,DUL.Event))),f'{name} equates description with event')
  check(not list(graph.triples((None,RDFS.subClassOf,DUL.Action))),f'{name} equates description with action occurrence')
  check(not list(graph.triples((None,OWL.equivalentClass,None))),f'{name} has unreviewed class equivalence')
check(not any('pouring' in str(x).lower() or 'grasping' in str(x).lower()
              for tr in t['core'] for x in tr), 'core contains a specific action')
check((A.dul_Description,RDFS.subClassOf,DUL.Description) in t['bridge'],'DUL directional mapping')
check((A.dul_Event,RDFS.subClassOf,DUL.Event) not in t['bridge'],'unsafe DUL event mapping')
check((P.PouringKnowledgeFrame,RDFS.subClassOf,A.ManipulationFrame) not in t['pouring'],'runtime family dependency')
check((P.PouringActingHypothesis,RDFS.subClassOf,A.ManipulationHypothesis) not in t['pouring'],'evidence trace dependency')
check((M.ActingHypothesis,RDFS.subClassOf,A.Hypothesis) in t['core'],'hypothesis lineage')

# Check every referenced AICOR term is declared in SOURCE (type declarations only).
known=set()
for typ in [OWL.Class,OWL.ObjectProperty,OWL.DatatypeProperty]: known.update(t['source'].subjects(RDF.type,typ))
for name in ('core','pouring','grasping','bridge'):
  for s,p,o in t[name]:
    for x in (s,p,o):
      if isinstance(x,URIRef) and str(x).startswith(str(A)):
        check(x in known,f'{name} undefined AICOR source term {x}')

# Every referenced MAKF term from action modules must be declared in core.
makf_terms=set(t['core'].subjects(RDF.type,OWL.Class)) | set(t['core'].subjects(RDF.type,OWL.ObjectProperty))
for name in ('pouring','grasping'):
  for tr in t[name]:
    for x in tr:
      if isinstance(x,URIRef) and str(x).startswith(str(M)):
        check(x in makf_terms,f'{name} missing MAKF symbol: {x}')

expected=[M.hasActionCategory,M.hasRolePerspective,M.hasIntentionalPerspective,M.hasCausalPerspective,
          M.hasTemporalPerspective,M.hasProceduralPerspective,M.hasObservationalPerspective,
          M.hasHypothesisPerspective,M.hasDeviationPerspective,M.hasApplicabilityPerspective]
for name,frame in [('pouring',P.PouringKnowledgeFrame),('grasping',G.GraspingKnowledgeFrame)]:
  got=dict(subset_restrictions(frame,t[name]))
  check(all(prop in got for prop in expected),f'{name} 10 aspect links incomplete')
  check(got[M.hasActionCategory]==(A.Pouring if name=='pouring' else A.Grasping),'wrong category')
  check((frame,RDFS.subClassOf,M.ActionKnowledgeFrame) in t[name], 'frame not subclass MAKF')

# Generic hypothesis support and strongly typed action variants.
check((M.GeneralizedStrategy,RDFS.subClassOf,DUL.Plan) in t['core'],'generic plan description absent')
check((P.PouringStrategy,RDFS.subClassOf,A.GeneralizedActionPlan) in t['pouring'],'lost pouring CRAM plan tie')
check((G.ContactGuidedGraspStrategy,RDFS.subClassOf,M.GeneralizedStrategy) in t['grasping'],'second action strategy not using MAKF')
check((M.predictsPossibleEffect,P.UncontrolledOutflowPredictionPattern) in subset_restrictions(P.RapidTiltOutflowRiskHypothesis,t['pouring']), 'lost pour risk hypothesis')
check((M.predictsPossibleEffect,G.StableCouplingPrediction) in subset_restrictions(G.ContactStabilityHypothesis,t['grasping']), 'second action hypothesis failure')

# Catalog points to files with matching ontology IRIs (except DUL, explicitly external).
ct=ET.parse(D/'config/catalog-v001.xml').getroot()
ns='{urn:oasis:names:tc:entity:xmlns:xml:catalog}'
for node in ct.findall(ns+'uri'):
  path=(D/'config'/node.attrib['uri']).resolve()
  check(path.is_file(), f'catalog target missing {path}')
  check((URIRef(node.attrib['name']),RDF.type,OWL.Ontology) in Graph().parse(path,format='turtle'), 'catalog logical IRI mismatch')

# Deterministic migration, full coverage for previously declared properties and classes.
with (D/'reports/migration_map.csv').open(newline='') as f:
    mappings=list(csv.DictReader(f))
legacy_syms=set(t['legacy'].subjects(RDF.type,OWL.Class))|set(t['legacy'].subjects(RDF.type,OWL.ObjectProperty))
check(len(mappings)==len(legacy_syms),f'migration rows {len(mappings)} != legacy symbols {len(legacy_syms)}')
check({URIRef(r['old_iri']) for r in mappings}==legacy_syms,'migration mapping does not cover P1.2')
for row in mappings:
  new=URIRef(row['new_iri']); dst=t['core'] if row['target_module']=='makf-core.ttl' else t['pouring']
  check((new,RDF.type,OWL.Class) in dst or (new,RDF.type,OWL.ObjectProperty) in dst,f'migration target not declared {new}')

result={
  'baseline_classes':len([u for u in set(t['base'].subjects(RDF.type,OWL.Class)) if str(u).startswith(str(A))]),
  'cram_classes':len([u for u in set(t['source'].subjects(RDF.type,OWL.Class)) if str(u).startswith(str(A))]),
  'makf_classes':len(set(t['core'].subjects(RDF.type,OWL.Class))),
  'makf_object_properties':len(set(t['core'].subjects(RDF.type,OWL.ObjectProperty))),
  'pouring_classes':len(set(t['pouring'].subjects(RDF.type,OWL.Class))),
  'grasping_test_classes':len(set(t['grasping'].subjects(RDF.type,OWL.Class))),
  'migration_rows':len(mappings),
  'tests_status':'PASS',
  'reasoner_status':'NOT RUN: official DUL file and external DL reasoner not present'
}
(D/'reports/validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: syntax, imports/catalog, symbol inventory, cross-action competency structure, conditional hypotheses, migration coverage')
print(json.dumps(result,indent=2))
