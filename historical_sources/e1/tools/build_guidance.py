#!/usr/bin/env python3
"""Export an ontology-grounded, action-profile-specific context for future LLM prompts.

This exports declared vocabulary and local subclass/restriction structure only,
not inferred facts, world-state instances, or scientific claims.
"""
import argparse
import json
from pathlib import Path
import yaml
from rdflib import URIRef, BNode
from rdflib.namespace import RDFS, OWL
from validate import SemanticValidator, ROOT

def build_context(profile_path):
    validator = SemanticValidator(ROOT)
    p = yaml.safe_load(Path(profile_path).read_text())
    validator.validate_profile(p)
    relevant = sorted({t for xs in p['perspective_focus'].values() for t in xs}
                      | {p['ontology_action_class'],p['ontology_frame_class']})
    entries = []
    for term in relevant:
        iri = validator.uri(term)
        parents = sorted(str(x) for x in validator.graph.objects(iri, RDFS.subClassOf) if isinstance(x,URIRef))
        restrictions = []
        for x in validator.graph.objects(iri,RDFS.subClassOf):
            if isinstance(x,BNode):
                predicate = next(iter(validator.graph.objects(x, OWL.onProperty)), None)
                filler = next(iter(validator.graph.objects(x, OWL.someValuesFrom)), None)
                if predicate is not None and filler is not None:
                    restrictions.append({'property_uri':str(predicate),'some_values_from_uri':str(filler)})
        entries.append({'curie':term, 'uri':str(iri), 'parent_uris':parents,
                        'existential_restrictions':restrictions})
    predicates=[]
    for pred in sorted(validator.graph.subjects(predicate=None, object=OWL.ObjectProperty), key=str):
        if str(pred).startswith(validator.prefixes['makf']):
            predicates.append({'uri':str(pred),
                               'domains':[str(x) for x in validator.graph.objects(pred,RDFS.domain)],
                               'ranges':[str(x) for x in validator.graph.objects(pred,RDFS.range)]})
    return {'profile_id':p['profile_id'], 'action_class':p['ontology_action_class'],
            'frame_class':p['ontology_frame_class'], 'perspective_focus':p['perspective_focus'],
            'known_class_declarations':entries, 'allowed_makf_properties':predicates,
            'IMPORTANT':'Vocabulary context only. It does not imply causal assertions or actual observed events.'}

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--profile', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    ctx=build_context(args.profile)
    Path(args.out).write_text(json.dumps(ctx,indent=2)+'\n')
    print('Wrote',args.out)
