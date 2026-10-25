"""Archive qualified local-simulation summaries; never relabel them as paper results."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from makf_knowledge.quantitative import validate_quantitative
from makf_knowledge.quantitative_rdf import export_quantitative

HERE=Path(__file__).resolve().parent


def ingest(report_path, out_dir):
    raw=Path(report_path).read_bytes();report=json.loads(raw)
    if report.get('status')!='completed_with_gradient_gate':raise ValueError('A completed run report is required')
    if len(report['rollouts'])!=2 or any(len(r['records'])!=100 or not r['all_states_finite'] for r in report['rollouts']):
        raise ValueError('Require both complete 100-step rollouts')
    quantities=[];lines=['Local native-unit FluidLab CPU validation, not a paper reproduction or physical experiment.']
    for index,run in enumerate(report['rollouts']):
        case='zero' if index==0 else 'tilt'
        initial=Decimal(str(run['initial']['active_mass']));final=Decimal(str(run['final']['active_mass']))
        fraction=final/initial
        duration=Decimal(str(report['runtime']['dt']))*Decimal(report['runtime']['substeps'])*run['steps']
        particle_count=run['final']['active_particles']
        lines.append(f"{case}: control_wz={run['control_wz']}; {run['steps']} forward steps; {particle_count} active particles at final state; nominal horizon {duration} code time units (steps * dt * substeps); initial active mass {initial}, final active mass {final}, active mass fraction {fraction} (final / initial); finite states at every tested step.")
        for name,kind,value,role,unit,metric,denominator in [
            ('particles','total_particle_count',str(particle_count),'result',dict(status='explicit',symbol='count',reported_text='particles'),'Total active particles at the final recorded state, not a sampled observation budget.',None),
            ('mass-retention','mass_fraction',str(fraction),'result',dict(status='dimensionless',symbol='1',reported_text='fraction'),'Final active particle mass ledger divided by its initial ledger; not a fluid-transfer or grid-conservation metric.',str(initial)+' initial active mass in code units'),
            ('duration','duration',str(duration),'configuration',dict(status='simulation_units',symbol='code_time',reported_text='code time units'),'Nominal numerical duration = forward steps * integration dt * substeps; no SI time scale asserted.',None)]:
            q=dict(quantity_id=case+'-'+name,annex_record_id=case,quantity_kind=kind,role=role,subject=case+' control_wz='+str(run['control_wz']),reported_value_text=value,unit=unit,evidence=[dict(artifact_id='local-summary',exact_quote='PLACEHOLDER')],metric_definition=metric)
            if denominator:q['denominator']=denominator
            quantities.append(q)
    lines.append('Gradient gate: '+report['gradient']['status']+'. Optimization: '+report['optimization']['status']+'.')
    text='\n'.join(lines)+'\n'
    for q in quantities:q['evidence'][0]['exact_quote']=text
    data=dict(schema_version='0.1',study=dict(study_id='fluidlab-native-validation-001',title='Local FluidLab zero-action and small-tilt development checks',source_uri='urn:makf:local-simulation:fluidlab-validation-001',document_version='Raw runtime report SHA-256 '+hashlib.sha256(raw).hexdigest(),evidence_origin='local_simulation',synthetic_demo=False,simulator=dict(name='FluidLab/FluidEngine patched CPU runtime',version_status='reported',version='7295eb6ed7ee92b2be471fd30b432238577f28ce; runtime.patch from fluidlab_smoke_001; makf-fluidlab-smoke:005'),context=dict(status='partial',description='Seed 0; 40,604 particles; 64^3 grid; config initial pose; 100 steps at control 0 or 0.00115. Not SI calibrated, not a held-out benchmark, not verified as paper-result replication. Raw loss and height-threshold proxies remain in runtime artifacts; no pouring-success claim.',evidence=[dict(artifact_id='local-summary',exact_quote=text)]),transcription_method='Deterministic extraction from local report; duration is steps*dt*substeps and mass fraction is final ledger/initial ledger. Raw report hash retained.',review_state='pending'),artifacts=[dict(artifact_id='local-summary',text=text,sha256=hashlib.sha256(text.encode()).hexdigest(),locator='Local runtime validation-report.json, rollouts and gradient gate; full raw report retained beside this evidence')],quantities=quantities,conversions=[],timing_checks=[],issues=[])
    validation=validate_quantitative(data)
    (HERE/'local-evidence.json').write_text(json.dumps(data,indent=2)+'\n')
    (HERE/'local-evidence-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    export_quantitative(data,base_iri='https://example.org/makf/data/').save(out_dir)
    return validation


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--report',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args();r=ingest(a.report,a.out_dir);print(json.dumps({'quantity_count':r['quantity_count'],'comparison_ready':r['comparison_ready'],'execution_eligible':r['execution_eligible']}))
