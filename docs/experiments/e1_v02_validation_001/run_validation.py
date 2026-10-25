"""Explicit live calibration and fresh extraction, with fixed cases and no repair loop."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from makf_knowledge.extraction import ExtractionRequest,SourceDocument,SourcePassage
from makf_knowledge.pipeline import extract
from makf_knowledge.providers import FixtureProvider,OpenAIProvider
from makf_knowledge.quality import OpenAIReviewer,review_quality,select_reviewed,CHECKS
from makf_knowledge.publication import export_batch

HERE=Path(__file__).resolve().parent
CORPUS=HERE.parent/'corpus_expansion_001'


def request(batch_id,docs):
    return ExtractionRequest(batch_id,tuple(SourceDocument(d['document_id'],d['title'],d['synthetic_demo'],
        tuple(SourcePassage(**p) for p in d['passages']),d.get('uri'),d.get('doi')) for d in docs),
        'pouring',('procedural','applicability','observational'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    parser.add_argument('--extract-model',required=True)
    parser.add_argument('--review-model',required=True)
    args=parser.parse_args()
    root=args.out_dir;root.mkdir(parents=True,exist_ok=False,mode=0o700)
    controls=json.loads((HERE/'controls.json').read_text())
    labels=json.loads((HERE/'expected.json').read_text())
    expected={c['candidate_id']:c for c in labels['cases']}
    initial=extract(request(controls['batch_id'],controls['documents']),FixtureProvider(json.dumps(controls)))
    if initial.report['status']!='provisional':
        raise ValueError('Controls failed mechanical validation: '+str(initial.report))
    initial.save(root/'controls-input')
    config={'extract_model':args.extract_model,'review_model':args.review_model,
        'controls_sha256':hashlib.sha256((HERE/'controls.json').read_bytes()).hexdigest(),
        'expected_sha256':hashlib.sha256((HERE/'expected.json').read_bytes()).hexdigest(),
        'planned_model_calls':8,'revision_calls':0,'repetitions_per_model':2,
        'max_output_tokens_per_call':9000,'timeout_seconds':180,
        'scope':'Assistant-annotated development calibration, not held-out or scientific validation.'}
    (root/'config.json').write_text(json.dumps(config,indent=2)+'\n')

    def calibration(model,rep):
        client=OpenAIReviewer(model,max_output_tokens=9000,timeout=180)
        try:result=review_quality(initial,client)
        finally:client.close()
        key=model+'-repeat-'+str(rep);result.save(root/key)
        rows=result.report.get('assessments',[])
        decisions=[dict(candidate_id=r['candidate_id'],expected_pass=expected[r['candidate_id']]['expected_pass'],
            actual_pass=all(r[k] for k in CHECKS),checks={k:r[k] for k in CHECKS},rationale=r['rationale']) for r in rows]
        summary={'task':'calibration','model':model,'repeat':rep,'status':result.report['status'],
            'false_acceptances':sum(r['actual_pass'] and not r['expected_pass'] for r in decisions),
            'false_rejections':sum(not r['actual_pass'] and r['expected_pass'] for r in decisions),
            'assessed':len(decisions),'decisions':decisions,'provider':result.report['provider']}
        print(json.dumps({k:v for k,v in summary.items() if k not in {'decisions','provider'}}),flush=True)
        return summary

    def fresh(key):
        doc=json.loads((CORPUS/(key+'-source.json')).read_text())
        client=OpenAIProvider(args.extract_model,max_output_tokens=9000,timeout=180)
        try:result=extract(request('e1-v02-fresh-'+key,[doc]),client)
        finally:client.close()
        directory=root/('fresh-'+key);result.save(directory)
        summary={'task':'fresh','source':key,'status':result.report['status'],'provider':result.report.get('provider'),
            'candidate_count':result.report.get('candidate_count',0)}
        if result.batch is not None:
            reviewer=OpenAIReviewer(args.review_model,max_output_tokens=9000,timeout=180)
            try:review=review_quality(result,reviewer)
            finally:reviewer.close()
            review.save(directory/'quality-review')
            summary.update(review_status=review.report['status'],review_provider=review.report['provider'],
                assessments=review.report.get('assessments',[]),knowledge_kinds=[c['knowledge_kind'] for c in result.batch['candidates']])
            if review.report['status'] in {'review_passed','changes_required'}:
                selection=select_reviewed(result,review,directory/'selection')
                summary['selected_candidate_ids']=selection['selected_candidate_ids']
                summary['withheld_candidate_ids']=selection['withheld_candidate_ids']
                if selection['selected_candidate_ids']:
                    batch=json.loads((directory/'selection/candidates.json').read_text())
                    export_batch(batch,base_iri='https://example.org/makf/data/',selection=selection,reviewed_batch=result.batch).save(directory/'rdf')
                    summary['shacl_conforms']=True
        print(json.dumps({k:v for k,v in summary.items() if k not in {'assessments','provider','review_provider'}}),flush=True)
        return summary

    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(calibration,m,r) for m in dict.fromkeys([args.extract_model,args.review_model]) for r in (1,2)]
        jobs += [pool.submit(fresh,key) for key in ('softgym','fluidlab')]
        results=[]
        for job in as_completed(jobs):results.append(job.result())
    summary={'config':config,'results':results}
    (root/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':main()
