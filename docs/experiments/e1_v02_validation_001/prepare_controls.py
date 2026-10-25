"""Build a frozen, assistant-annotated calibration set before any live review."""
from copy import deepcopy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent / 'corpus_expansion_001'


def build():
    batch=json.loads((CORPUS/'semantic-v02-proposals.json').read_text())
    positive=deepcopy(batch['candidates'])
    soft=json.loads((CORPUS/'softgym-reviewed.json').read_text())
    for index in (0,2):
        c=deepcopy(soft['candidates'][index])
        c.update(knowledge_kind='benchmark_definition',epistemic_status='definition')
        c['components']=[dict(component_id='description',component_kind='generic_description',
            description=c['statement'],grounding_status='needs_mapping',
            grounding_note='No precise offered class is established for this benchmark definition.')]
        positive.append(c)
    positive.append(deepcopy(json.loads((CORPUS/'softgym-selected.json').read_text())['candidates'][0]))
    examples=[]
    for i,c in enumerate(positive):
        c['candidate_id']=f'valid-{i+1}'
        examples.append(dict(candidate=c,expected_pass=True,reason='Source-scoped description with complete cited evidence and candid or appropriate mapping.'))
    mutations=[
        (0,'incomplete reward citation',lambda c:c['source_support'][0].update(exact_quote='PourWater Pour a cup of water into a target cup.')),
        (2,'unsupported universal claim',lambda c:c.update(statement='The paper proves that differentiable simulation always achieves perfect pouring for every fluid.')),
        (0,'unrelated grounded class',lambda c:c['components'][0].update(grounding_status='grounded',ontology_class='paf:PouringStrategy')),
        (1,'opposite task objective',lambda c:c.update(statement='The FluidLab pouring objective is to keep all the light liquid inside the glass.')),
        (0,'unsupported component detail',lambda c:c['components'][0].update(description='The benchmark reward includes a viscosity sensor measuring fluid viscosity in pascal seconds.')),
        (2,'invented causal conclusion',lambda c:c.update(statement='The reported experiments establish that viscosity is the sole cause of all pouring failures.')),
    ]
    for i,(index,reason,mutate) in enumerate(mutations):
        c=deepcopy(positive[index]);c['candidate_id']=f'invalid-{i+1}';mutate(c)
        if reason=='unrelated grounded class':c['components'][0].pop('grounding_note',None)
        examples.append(dict(candidate=c,expected_pass=False,reason=reason))
    batch.update(batch_id='e1-v02-review-calibration',candidates=[e['candidate'] for e in examples])
    batch.pop('extraction_run',None)
    labels={'annotation_origin':'assistant-authored, not independent domain ground truth',
        'scope':'Development calibration on known sources; not a held-out benchmark.',
        'decision_rule':'Pass only if evidence_complete, scope_supported and mapping_supported are all true.',
        'pilot_gate':'No false acceptance or rejection in this small fixed set; failures block reliance on automatic promotion.',
        'repetitions_per_model':2,
        'cases':[{k:v for k,v in e.items() if k!='candidate'}|{'candidate_id':e['candidate']['candidate_id']} for e in examples]}
    return batch,labels

if __name__=='__main__':
    batch,labels=build()
    for name,value in [('controls.json',batch),('expected.json',labels)]:
        with (HERE/name).open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
    print('Frozen 12 controls: six positive and six adversarial.')
