import json,time,traceback
from pathlib import Path
import numpy as np
ROOT=Path('/out');protocol=json.loads((ROOT/'protocol.json').read_text())
report={'protocol':protocol,'cases':[],'terminal':{'status':'blocked_until_gate'},'status':'running'}
def save():
 (ROOT/'gradient-report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
try:
 import gym,fluidlab.envs,taichi as ti
 env=gym.make('Pouring-v0',seed=0,loss=True,loss_type='diff',renderer_type='GGUI');t=env.unwrapped.taichi_env
 initial=t.get_state()['state'];original_max=t.loss.max_loss_steps
 report['runtime']={'backend':str(ti.lang.impl.current_cfg().arch),'particle_count':t.simulator.n_particles,'dt':float(t.simulator.dt),'substeps':int(t.simulator.n_substeps)}
 def evaluate(case,value,grad=False,terminal=False):
  h=case['horizon'];t.loss.max_loss_steps=h if terminal else original_max;t.loss.temporal_range=[0,h]
  pose=np.asarray(protocol['base_pose'],dtype=np.float32);pose[0]+=case['pose_offset_x']
  t.set_state(initial,grad_enabled=grad);t.apply_agent_action_p(pose);actions=[]
  for i in range(h):
   a=np.zeros(6,dtype=np.float32)
   if i==case['action_step']:a[case['component']]=value
   actions.append(a);t.step(a)
  loss=float(t.get_final_loss()['loss'])
  if not np.isfinite(loss):raise ValueError('Non-finite loss')
  if not grad:return loss
  t.reset_grad();t.get_final_loss_grad()
  for a in reversed(actions):t.step_grad(a)
  t.apply_agent_action_p_grad(pose)
  g=float(t.agent.get_grad(h)[case['action_step'],case['component']])
  if not np.isfinite(g):raise ValueError('Non-finite derivative')
  return loss,g
 base=protocol['cases'][0];value=protocol['base_value']
 losses=[evaluate(base,value) for _ in range(protocol['forward_noise_repeats'])]
 grads=[evaluate(base,value,True) for _ in range(protocol['autodiff_noise_repeats'])]
 loss_spread=max(losses+[x[0] for x in grads])-min(losses+[x[0] for x in grads]);ad_values=[x[1] for x in grads];ad_spread=max(ad_values)-min(ad_values)
 report['noise']={'forward_losses':losses,'autodiff_runs':grads,'loss_range':loss_spread,'autodiff_range':ad_spread,'note':'Measured at base case only, not a bound for every later pose/regime.'};save();print('Noise',report['noise'],flush=True)
 def check(case,terminal=False):
  tick=time.time();loss,ad=evaluate(case,value,True,terminal);samples=[]
  for eps in protocol['epsilons']:
   plus=evaluate(case,value+eps,False,terminal);minus=evaluate(case,value-eps,False,terminal)
   forward=(plus-loss)/eps;backward=(loss-minus)/eps;fd=(plus-minus)/(2*eps)
   scale=max(abs(ad),abs(fd),1e-12);noise_bound=loss_spread/eps+ad_spread
   separated=abs(plus-minus)>protocol['minimum_signal_to_noise']*max(loss_spread,1e-12)
   informative=separated and max(abs(ad),abs(fd))>1e-5
   threshold=max(protocol['absolute_tolerance'],protocol['relative_tolerance']*scale)+noise_bound
   asym=abs(forward-backward)/max(abs(forward),abs(backward),1e-12)
   samples.append(dict(epsilon=eps,plus_loss=plus,minus_loss=minus,fd=fd,ad_error=abs(ad-fd),threshold=threshold,noise_bound=noise_bound,one_sided_forward=forward,one_sided_backward=backward,asymmetry=asym,informative=bool(informative),passes=bool(informative and abs(ad-fd)<=threshold and asym<=protocol['maximum_one_sided_asymmetry'])))
  adjacent=[abs(a['fd']-b['fd'])/max(abs(a['fd']),abs(b['fd']),1e-12) for a,b in zip(samples,samples[1:])]
  pair_pass=any(a['passes'] and b['passes'] and stability<=protocol['adjacent_fd_relative_stability'] for a,b,stability in zip(samples,samples[1:],adjacent))
  result={'case':case,'terminal_diagnostic':terminal,'loss':loss,'autodiff':ad,'samples':samples,'adjacent_fd_relative_changes':adjacent,'status':'PASS' if pair_pass else 'FAIL' if any(s['informative'] for s in samples) else 'UNINFORMATIVE','seconds':time.time()-tick}
  print('Case',case.get('id','terminal'),result['status'],'AD',ad,'FD',[s['fd'] for s in samples],flush=True)
  return result
 for case in protocol['cases']:
  try:result=check(case)
  except Exception as exc:
   result={'case':case,'status':'ERROR','error_type':type(exc).__name__,'error':str(exc)};traceback.print_exc()
  report['cases'].append(result);save()
 passed=[r for r in report['cases'] if r['status']=='PASS'];failures=[r for r in report['cases'] if r['status'] in ['FAIL','ERROR']]
 long_pass=all(any(r['case']['id']==name and r['status']=='PASS' for r in report['cases']) for name in ['earlier_vertical_h8','offset_vertical_h8'])
 gate=not failures and len(passed)>=protocol['minimum_informative_cases'] and long_pass
 report['broader_gate_passed']=bool(gate)
 if gate:
  try:report['terminal']=check(protocol['terminal_diagnostic_if_gate_passes'],True)
  except Exception as exc:report['terminal']={'status':'ERROR','error':str(exc)};traceback.print_exc()
 else:report['terminal']={'status':'blocked_by_broader_gate','reason':'No terminal test or optimizer inference after failed/insufficient broader checks.'}
 report['status']='completed';save()
except BaseException as exc:
 report.update(status='ERROR',error_type=type(exc).__name__,error=str(exc));save();traceback.print_exc();raise
