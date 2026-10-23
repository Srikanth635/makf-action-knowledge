#!/usr/bin/env python3
"""Direct declared OWL restriction traversal; does not attempt DL inference."""
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL

ROOT = Path(__file__).resolve().parents[1]
G = Graph()
for f in ['sources/cram-aicor-ontology.ttl', 'ontologies/dul-alignment.ttl',
          'ontologies/makf-core.ttl','ontologies/pouring-frame.ttl', 'ontologies/grasping-smoke.ttl']:
    G.parse(ROOT / f, format='turtle')
MAKF = Namespace('https://w3id.org/aicor/makf#')
PAF = Namespace('https://w3id.org/aicor/pouring-frame#')
GSF = Namespace('https://w3id.org/aicor/grasping-smoke#')
A = Namespace('http://aicor.knowledge/l2-ontology.owl#')


def local(uri):
    return str(uri).split('#')[-1]


def restrictions(c):
    """Only DIRECT someValuesFrom restrictions attached to cls."""
    rs=[]
    for r in G.objects(c,RDFS.subClassOf):
        if (r,RDF.type,OWL.Restriction) not in G: continue
        p=G.value(r,OWL.onProperty); val=G.value(r,OWL.someValuesFrom)
        if p is not None and val is not None:
            rs.append((p,val))
    return sorted(set(rs),key=lambda v:(str(v[0]),str(v[1])))


def show(name, cls):
    print('\n'+name)
    for prop,target in restrictions(cls):
        print('  '+local(prop)+' some '+local(target))

show('POURING: main knowledge frame',PAF.PouringKnowledgeFrame)
show('GRASPING: main knowledge frame',GSF.GraspingKnowledgeFrame)
show('POURING: roles',PAF.PouringRolePerspective)
show('GRASPING: roles',GSF.GraspingRolePerspective)
show('POURING: candidate hypothesis',PAF.RapidTiltOutflowRiskHypothesis)
show('GRASPING: candidate hypothesis',GSF.ContactStabilityHypothesis)
show('CRAM-AICOR: original pouring class',A.Pouring)
print('\nAll results reflect declared restrictions, not facts about a world.')
