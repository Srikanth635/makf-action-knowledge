#!/usr/bin/env python3
"""Export an ontology-grounded, action-profile-specific context for future LLM prompts.

This exports declared vocabulary and local subclass/restriction structure only,
not inferred facts, world-state instances, or scientific claims.
"""
from pathlib import Path
import yaml
from rdflib import URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL
from .validation import KIND_SUPERCLASSES, SemanticValidator, ValidationError, ROOT


def load_profile(path, validator):
    """Load local configuration and reject malformed profiles before graph lookup."""
    try:
        profile = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise ValidationError(f'Cannot read action profile: {path}') from exc
    if not isinstance(profile, dict):
        raise ValidationError('Action profile must be a mapping')
    for key in ('profile_id', 'ontology_action_class', 'ontology_frame_class'):
        if not isinstance(profile.get(key), str) or not profile[key].strip():
            raise ValidationError(f'Profile requires a nonempty {key}')
    for key in ('allowed_component_prefixes', 'allowed_predicate_prefixes'):
        values = profile.get(key)
        if (not isinstance(values, list) or not values
                or any(not isinstance(v, str) or v not in validator.prefixes for v in values)):
            raise ValidationError(f'Profile {key} must list registered prefixes')
    focus = profile.get('perspective_focus')
    if not isinstance(focus, dict) or not focus:
        raise ValidationError('Profile requires a nonempty perspective_focus mapping')
    for perspective, terms in focus.items():
        if (not isinstance(terms, list) or not terms
                or any(not isinstance(t, str) or not t for t in terms)):
            raise ValidationError(f'Profile perspective {perspective!r} must list class CURIEs')
        if any(t.split(':')[0] not in profile['allowed_component_prefixes'] for t in terms):
            raise ValidationError(f'Profile perspective {perspective!r} uses a disallowed prefix')
    validator.validate_profile(profile)
    return profile


def _class_entry(validator, term):
    iri = validator.require_declared(term, OWL.Class)
    parents = sorted(str(x) for x in validator.graph.objects(iri, RDFS.subClassOf)
                     if isinstance(x, URIRef))
    restrictions = []
    for node in validator.graph.objects(iri, RDFS.subClassOf):
        if isinstance(node, BNode):
            # Do not serialize unstable blank-node identifiers or expand anonymous expressions.
            for prop in validator.graph.objects(node, OWL.onProperty):
                for filler in validator.graph.objects(node, OWL.someValuesFrom):
                    if isinstance(prop, URIRef) and isinstance(filler, URIRef):
                        restrictions.append({'property_uri': str(prop),
                                             'some_values_from_uri': str(filler)})
    return {'curie': term, 'uri': str(iri), 'parent_uris': parents,
            'existential_restrictions': sorted(restrictions, key=lambda x: (
                x['property_uri'], x['some_values_from_uri']))}

def build_context(profile_path, root=ROOT):
    validator = SemanticValidator(root)
    p = load_profile(profile_path, validator)
    relevant = sorted({t for xs in p['perspective_focus'].values() for t in xs}
                      | {p['ontology_action_class'],p['ontology_frame_class']})
    entries = [_class_entry(validator, term) for term in relevant]
    predicates=[]
    for pred in sorted(validator.graph.subjects(RDF.type, OWL.ObjectProperty), key=str):
        if str(pred).startswith(validator.prefixes['makf']):
            predicates.append({'uri':str(pred),
                               'domains':sorted(str(x) for x in validator.graph.objects(pred,RDFS.domain)),
                               'ranges':sorted(str(x) for x in validator.graph.objects(pred,RDFS.range))})
    return {'profile_id':p['profile_id'], 'action_class':p['ontology_action_class'],
            'frame_class':p['ontology_frame_class'], 'perspective_focus':p['perspective_focus'],
            'known_class_declarations':entries, 'allowed_makf_properties':predicates,
            'IMPORTANT':'Vocabulary context only. It does not imply causal assertions or actual observed events.'}


def build_perspective_context(profile, validator, perspectives=None):
    """Select small, nonrecursive context from a validated profile and local graph.

    The profile controls focus classes; shared MAKF classes support E1 hypothesis
    conditions/effects without importing the entire action vocabulary. No ontology
    imports are fetched and no individuals or inferred axioms are exported.
    """
    order = tuple(validator.linkml['enums']['PerspectiveEnum']['permissible_values'])
    focus = profile['perspective_focus']
    if perspectives is None:
        selected = tuple(p for p in order if p in focus)
    else:
        if (not isinstance(perspectives, (tuple, list)) or not perspectives
                or any(not isinstance(p, str) or p not in focus for p in perspectives)):
            raise ValidationError('Select one or more perspectives present in the action profile')
        if len(set(perspectives)) != len(perspectives):
            raise ValidationError('Duplicate perspective selection')
        selected = tuple(p for p in order if p in perspectives)
    entries = {}
    for perspective in selected:
        terms = sorted(set(focus[perspective]))
        if len(terms) > 8:
            raise ValidationError(f'Perspective {perspective} exceeds the limit of 8 focus classes')
        entries[perspective] = [_class_entry(validator, term) for term in terms]
    # These are description classes, not physical instances. Include the strategy
    # hypothesis subtype so concernsStrategy can satisfy its declared domain.
    shared = sorted(set(KIND_SUPERCLASSES.values()) | {'makf:StrategyHypothesis'})
    shared = [t for t in shared if t.split(':')[0] in profile['allowed_component_prefixes']]
    classes = {validator.uri(t) for t in shared}
    classes.update(validator.uri(t) for p in selected for t in focus[p])
    properties = []
    for prop in sorted(set(validator.graph.subjects(RDF.type, OWL.ObjectProperty)), key=str):
        curies = [prefix + ':' + str(prop)[len(validator.prefixes[prefix]):]
                  for prefix in profile['allowed_predicate_prefixes']
                  if str(prop).startswith(validator.prefixes[prefix])]
        if not curies:
            continue
        domains = sorted(x for x in validator.graph.objects(prop, RDFS.domain) if isinstance(x, URIRef))
        ranges = sorted(x for x in validator.graph.objects(prop, RDFS.range) if isinstance(x, URIRef))
        if any(validator.subclass_or_equal(cls, bound) for cls in classes for bound in domains + ranges):
            properties.append({'curie': sorted(curies)[0], 'uri': str(prop),
                               'domains': list(map(str, domains)), 'ranges': list(map(str, ranges))})
    return {'profile_id': profile['profile_id'],
            'action_class': profile['ontology_action_class'],
            'frame_class': profile['ontology_frame_class'],
            'allowed_component_prefixes': profile['allowed_component_prefixes'],
            'allowed_predicate_prefixes': profile['allowed_predicate_prefixes'],
            'perspectives': entries,
            'shared_description_classes': [_class_entry(validator, t) for t in shared],
            'allowed_properties': properties,
            'scope': 'Selected declared classes and direct named restrictions only; '
                     'no remote imports, inferred axioms, individuals, or scientific evidence.'}

