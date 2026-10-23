#!/usr/bin/env python3
"""Query directly asserted schema-level OWL restrictions; no DL inference."""
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL

D = Path(__file__).resolve().parent
G = Graph().parse(D / 'pouring-frame.ttl', format='turtle')
G.parse(D / 'dul-alignment.ttl', format='turtle')
G.parse(D.parent / 'cram-aicor-ontology.ttl', format='turtle')
PAF = Namespace('https://w3id.org/aicor/pouring-frame#')
AICOR = Namespace('http://aicor.knowledge/l2-ontology.owl#')

def restrictions(cls):
    result = []
    for r in G.objects(cls, RDFS.subClassOf):
        if (r, RDF.type, OWL.Restriction) in G:
            p = G.value(r, OWL.onProperty)
            filler = G.value(r, OWL.someValuesFrom)
            if p and filler:
                result.append((p.split('#')[-1], filler.split('#')[-1]))
    return sorted(set(result))

def show(label, cls):
    print('\n'+label)
    for prop, target in restrictions(cls):
        print(f'  {prop} -> some {target}')

show('CQ01 Main frame links', PAF.PouringKnowledgeFrame)
show('CQ02 Abstract pouring role schema', PAF.PouringRolePerspective)
show('CQ03 Existing intention (source ontology)', AICOR.PouringIntention)
show('CQ04 Existing causal template (source ontology)', AICOR.PouringTemplate)
show('CQ05 Candidate ordering', PAF.InitiationBeforeTerminationPattern)
show('CQ07 Rapid-tilt risk hypothesis', PAF.RapidTiltOutflowRiskHypothesis)
print('\nCQ06 Strategy classes:')
for strategy in [PAF.OrientationMediatedPouringStrategy,PAF.FeedbackRegulatedPouringStrategy,PAF.RapidOrientationChangeStrategy]:
    if (strategy, RDFS.subClassOf, PAF.PouringStrategy) in G or (strategy, RDFS.subClassOf, PAF.OrientationMediatedPouringStrategy) in G:
        print(' ',strategy.split('#')[-1])
