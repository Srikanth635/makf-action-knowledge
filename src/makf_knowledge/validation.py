#!/usr/bin/env python3
"""Offline schema + ontology-guided verification of E1 candidate descriptions.

No external imports are resolved. This is NOT OWL reasoning, SHACL validation,
or scientific entailment verification.
"""
import argparse
import json
from pathlib import Path
import yaml
import jsonschema
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL

from .paths import RESOURCE_ROOT
from .schema import compile_schema
ROOT = RESOURCE_ROOT

ONTOLOGIES = (
    'cram-aicor-ontology.ttl', 'dul-alignment.ttl', 'makf-core.ttl',
    'pouring-frame.ttl', 'grasping-smoke.ttl',
)
KIND_SUPERCLASSES = {
    'hypothesis': 'makf:ActingHypothesis',
    'strategy': 'makf:GeneralizedStrategy',
    'applicability_condition': 'makf:ApplicabilityCondition',
    'predicted_effect': 'makf:PredictedEffectPattern',
    'phase_pattern': 'makf:PhasePattern',
    'observation_pattern': 'makf:ObservationPattern',
    'deviation_pattern': 'makf:DeviationPattern',
}

class ValidationError(ValueError):
    pass

class SemanticValidator:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.linkml = yaml.safe_load((self.root / 'schema/makf_extraction.linkml.yaml').read_text())
        self.json_schema = compile_schema(self.linkml)
        jsonschema.Draft202012Validator.check_schema(self.json_schema)
        self.structural_validator = jsonschema.Draft202012Validator(self.json_schema, format_checker=jsonschema.FormatChecker())
        self.prefixes = self.linkml['prefixes']
        self.graph = Graph()
        for name in ONTOLOGIES:
            self.graph.parse(self.root / 'ontology' / name, format='turtle')

    def uri(self, curie):
        if not isinstance(curie, str) or ':' not in curie:
            raise ValidationError(f'Expected ontology CURIE, received {curie!r}')
        prefix, local = curie.split(':', 1)
        if prefix not in self.prefixes or not local:
            raise ValidationError(f'Unregistered CURIE {curie!r}')
        if '/' in local or '#' in local:
            raise ValidationError(f'CURIE must identify a local term: {curie}')
        return URIRef(self.prefixes[prefix] + local)

    def require_declared(self, term, rdf_type):
        iri = self.uri(term)
        if (iri, RDF.type, rdf_type) not in self.graph:
            raise ValidationError(f'{term} not declared as {rdf_type.split("#")[-1]} in local ontologies')
        return iri

    def subclass_or_equal(self, child, parent):
        if child == parent:
            return True
        seen, agenda = set(), [child]
        while agenda:
            cur = agenda.pop()
            if cur in seen:
                continue
            seen.add(cur)
            for ancestor in self.graph.objects(cur, RDFS.subClassOf):
                if ancestor == parent:
                    return True
                if isinstance(ancestor, URIRef):
                    agenda.append(ancestor)
        return False

    def validate_profile(self, profile):
        self.require_declared(profile['ontology_action_class'], OWL.Class)
        frame = self.require_declared(profile['ontology_frame_class'], OWL.Class)
        if not self.subclass_or_equal(frame, self.uri('makf:ActionKnowledgeFrame')):
            raise ValidationError('Profile frame is not a MAKF ActionKnowledgeFrame subclass')
        declared_action = self.uri(profile['ontology_action_class'])
        has_action_type_restriction = any(
            isinstance(r, BNode)
            and (r, OWL.onProperty, self.uri('makf:hasActionCategory')) in self.graph
            and (r, OWL.someValuesFrom, declared_action) in self.graph
            for r in self.graph.objects(frame, RDFS.subClassOf)
        )
        if not has_action_type_restriction:
            raise ValidationError('Profile frame does not have an explicit hasActionCategory some restriction for this action')
        if not any((self.uri(t), RDF.type, OWL.Class) in self.graph for focus in profile['perspective_focus'].values() for t in focus):
            raise ValidationError('Profile has no grounded perspective types')
        for perspective, terms in profile['perspective_focus'].items():
            if perspective not in self.linkml['enums']['PerspectiveEnum']['permissible_values']:
                raise ValidationError(f'Unknown profile perspective: {perspective}')
            for term in terms:
                self.require_declared(term, OWL.Class)

    def validate_batch(self, data, profile):
        errors = list(self.structural_validator.iter_errors(data))
        if errors:
            first = sorted(errors, key=lambda e: str(list(e.absolute_path)))[0]
            raise ValidationError(f'JSON Schema: {list(first.absolute_path)}: {first.message}')
        if data['profile_id'] != profile['profile_id']:
            raise ValidationError('Batch profile_id does not match the loaded profile')
        self.validate_profile(profile)
        documents = {}
        for d in data['documents']:
            if d['document_id'] in documents:
                raise ValidationError('Duplicate document_id: ' + d['document_id'])
            passages = {}
            for p in d['passages']:
                if p['passage_id'] in passages:
                    raise ValidationError(f'Duplicate passage_id: {p["passage_id"]}')
                passages[p['passage_id']] = p
            documents[d['document_id']] = (d, passages)
        ids = set()
        warnings = []
        for c in data['candidates']:
            cid = c['candidate_id']
            if cid in ids:
                raise ValidationError('Duplicate candidate_id: ' + cid)
            ids.add(cid)
            if c['action_class'] != profile['ontology_action_class'] or c['frame_class'] != profile['ontology_frame_class']:
                raise ValidationError(f'{cid}: action/frame mismatch with profile')
            self.require_declared(c['action_class'], OWL.Class)
            self.require_declared(c['frame_class'], OWL.Class)
            kinds = {x['component_id']: x for x in c['components']}
            if len(kinds) != len(c['components']):
                raise ValidationError(f'{cid}: duplicate component_id')
            for comp in c['components']:
                ctype = comp.get('ontology_class')
                if comp['grounding_status'] == 'grounded':
                    if not ctype:
                        raise ValidationError(f'{cid}: grounded component lacks ontology_class')
                    pfx = ctype.split(':')[0]
                    if pfx not in profile['allowed_component_prefixes']:
                        raise ValidationError(f'{cid}: component class prefix {pfx} not allowed by profile')
                    comp_iri = self.require_declared(ctype, OWL.Class)
                    superclass = KIND_SUPERCLASSES.get(comp['component_kind'])
                    if superclass and not self.subclass_or_equal(comp_iri, self.uri(superclass)):
                        raise ValidationError(f'{cid}: {ctype} not a subclass of {superclass} for kind {comp["component_kind"]}')
                elif ctype or not comp.get('grounding_note'):
                    raise ValidationError(f'{cid}: needs_mapping requires grounding_note and no ontology_class')
            links = set()
            for l in c.get('structural_links', []):
                if l['subject_component'] not in kinds or l['object_component'] not in kinds:
                    raise ValidationError(f'{cid}: link endpoints must reference local components')
                pfx = l['predicate_curie'].split(':')[0]
                if pfx not in profile['allowed_predicate_prefixes']:
                    raise ValidationError(f'{cid}: predicate prefix {pfx} not allowed')
                predicate = self.require_declared(l['predicate_curie'], OWL.ObjectProperty)
                links.add((l['subject_component'], l['predicate_curie'], l['object_component']))
                s = kinds[l['subject_component']]
                o = kinds[l['object_component']]
                if s['grounding_status'] != 'grounded' or o['grounding_status'] != 'grounded':
                    continue
                for domain in self.graph.objects(predicate, RDFS.domain):
                    if isinstance(domain, URIRef) and not self.subclass_or_equal(self.uri(s['ontology_class']), domain):
                        raise ValidationError(f'{cid}: {s["ontology_class"]} violates predicate domain of {l["predicate_curie"]}')
                for range_class in self.graph.objects(predicate, RDFS.range):
                    if isinstance(range_class, URIRef) and not self.subclass_or_equal(self.uri(o['ontology_class']), range_class):
                        raise ValidationError(f'{cid}: {o["ontology_class"]} violates predicate range of {l["predicate_curie"]}')
            if c['epistemic_status'] == 'hypothesis':
                h_nodes = [v['component_id'] for v in kinds.values() if v['component_kind'] == 'hypothesis']
                for relation, required_kind in [('makf:hasApplicabilityCondition','applicability_condition'), ('makf:predictsPossibleEffect','predicted_effect')]:
                    if not any(s in h_nodes and p == relation and kinds[o]['component_kind'] == required_kind for s,p,o in links):
                        raise ValidationError(f'{cid}: hypothesis missing {relation} link to {required_kind}')
                if c['knowledge_kind'] == 'strategy_hypothesis' and not any(s in h_nodes and p == 'makf:concernsStrategy' and kinds[o]['component_kind'] == 'strategy' for s,p,o in links):
                    raise ValidationError(f'{cid}: strategy hypothesis must concern a strategy')
                if c['modality'] == 'necessary':
                    raise ValidationError(f'{cid}: hypothesis cannot be labeled necessary')
            if c['knowledge_kind'] in {'causal_hypothesis','strategy_hypothesis','deviation_hypothesis'} and c['epistemic_status'] != 'hypothesis':
                raise ValidationError(f'{cid}: hypothesis knowledge_kind requires epistemic_status=hypothesis')
            if c['derivation_mode'] in {'llm_inference','llm_proposal'}:
                if c['epistemic_status'] in {'definition', 'conditional_principle'} or c['evidence_status'] in {'corroborated', 'source_anchored'}:
                    raise ValidationError(f'{cid}: generated/inferred candidate cannot claim proven status or source-anchored support')
                if c['modality'] not in {'possible','conditional','speculative'}:
                    raise ValidationError(f'{cid}: generated/inferred candidate must be hedged')
            supports = c['source_support']
            asserted = False
            for sup in supports:
                if sup['document_id'] not in documents:
                    raise ValidationError(f'{cid}: unknown document_id: {sup["document_id"]}')
                document, passages = documents[sup['document_id']]
                if sup['passage_id'] not in passages:
                    raise ValidationError(f'{cid}: unknown passage_id: {sup["passage_id"]}')
                src = passages[sup['passage_id']]['text']
                quote = sup['exact_quote']
                if quote not in src:
                    raise ValidationError(f'{cid}: exact_quote does not occur verbatim in source passage')
                start, end = sup.get('start_char'), sup.get('end_char')
                if (start is None) != (end is None):
                    raise ValidationError(f'{cid}: start_char and end_char must be specified together')
                if start is not None and (start < 0 or end < start or src[start:end] != quote):
                    raise ValidationError(f'{cid}: source text offsets do not match exact_quote')
                asserted |= sup['support_role'] == 'asserts_claim'
                if document['synthetic_demo']:
                    warnings.append(f'{cid}: source is a SYNTHETIC demo, not published evidence')
            if c['derivation_mode'].startswith('source_') and not asserted:
                raise ValidationError(f'{cid}: source extraction requires an asserts_claim anchor')
            if c['evidence_status'] == 'source_anchored' and not asserted:
                raise ValidationError(f'{cid}: source_anchored requires asserts_claim source support')
            if c['evidence_status'] == 'corroborated':
                distinct = {s['document_id'] for s in supports if s['support_role'] == 'asserts_claim'}
                if len(distinct) < 2:
                    raise ValidationError(f'{cid}: corroborated needs at least two independently identified documents')
                warnings.append(f'{cid}: independent corroboration is not proven by document count')
            if c['evidence_status'] in {'source_anchored','corroborated'}:
                warnings.append(f'{cid}: quote matching does not prove scientific truth or entailment')
            if any(x['grounding_status'] == 'needs_mapping' for x in c['components']):
                warnings.append(f'{cid}: candidate has components pending ontology grounding')
        return {'status': 'PASS', 'batch_id': data['batch_id'], 'profile_id': data['profile_id'],
                'candidates': len(data['candidates']), 'warnings': sorted(set(warnings)),
                'scope': 'offline structural and local-ontology checks ONLY'}


def validate_file(path, profile_path, root=ROOT):
    validator = SemanticValidator(root)
    data = json.loads(Path(path).read_text())
    profile = yaml.safe_load(Path(profile_path).read_text())
    return validator.validate_batch(data, profile)

