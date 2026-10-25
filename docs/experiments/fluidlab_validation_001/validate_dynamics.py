"""Bounded CPU rollouts and directional finite differences; no paper/SI claims."""
import json,time,sys,traceback,ast
from pathlib import Path
import numpy as np
import yaml
ROOT=Path('/out')
config={'rollout_steps':100,'control_values':[0.0,0.00115],'initial_pose':[0.6,0.7,0.5,0.0,0.0,0.0],
 'gradient_horizon':4,'gradient_parameter':'last-step vertical displacement control, component 1',
 'gradient_control':0.001,'epsilons':[0.0001,0.00003],'absolute_tolerance':0.01,'relative_tolerance':0.15,
 'minimum_gradient_magnitude':1e-5,'optimizer_iterations_if_gate_passes':3,'optimizer_horizon':4,
 'note':'Short local CPU development check; no SI calibration or paper replication.'}
(ROOT/'protocol.json').write_text(json.dumps(config,indent=2)+'\n')
report={'protocol':config,'rollouts':[],'gradient':{'status':'not_run'},'optimization':{'status':'not_run'}}
def save(): (ROOT/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 import taichi as ti
 import gym,fluidlab.envs
 start=time.time();env=gym.make('Pouring-v0',seed=0,loss=True,loss_type='diff',renderer_type='GGUI');e=env.unwrapped;t=e.taichi_env
 state=t.get_state()['state'];pose=np.asarray(config['initial_pose'],dtype=np.float32)
 masses=t.simulator.particles_i.mass.to_numpy();material=t.simulator.particles_i.mat.to_numpy()
 report['runtime']={'backend':str(ti.lang.impl.current_cfg().arch),'python':sys.version,'taichi':list(ti.__version__),'particle_count':len(masses),'dt':float(t.simulator.dt),'substeps':int(t.simulator.n_substeps)}
 def reset(grad=False):
  t.set_state(state,grad_enabled=grad);t.apply_agent_action_p(pose)
 def snapshot():
  s=t.get_state_RL();x=s['x'];v=s['v'];active=s['used'].astype(bool)
  if not(np.isfinite(x).all() and np.isfinite(v).all()):raise ValueError('Non-finite physical state')
  return dict(active_particles=int(active.sum()),active_mass=float(np.sum(masses[active])),
    max_speed=float(np.max(np.linalg.norm(v[active],axis=1))) if active.any() else 0.,
    water_below_y_055=int(np.sum(active&(material==0)&(x[:,1]<0.55))),
    milk_active=int(np.sum(active&(material==1))),water_active=int(np.sum(active&(material==0))))
 for control in config['control_values']:
  reset();initial=snapshot();records=[];tic=time.time()
  for i in range(config['rollout_steps']):
   a=np.zeros(6,dtype=np.float32);a[5]=control;t.step(a)
   current=snapshot();current.update(step=i+1,step_loss=float(t.get_step_loss()['loss']))
   if not np.isfinite(current['step_loss']):raise ValueError('Non-finite loss')
   records.append(current)
   if (i+1)%10==0:print('rollout',control,'step',i+1,'active',current['active_particles'],flush=True)
  item={'control_wz':control,'steps':config['rollout_steps'],'initial':initial,'final':records[-1],
        'all_states_finite':True,'seconds':time.time()-tic,'records':records}
  report['rollouts'].append(item);save()
 # Use the same partial-horizon objective for AD and finite differences. Only the
 # final action changes, keeping the detached first-step reference independent.
 h=config['gradient_horizon'];t.loss.temporal_range=[0,h]
 def objective(value,grad=False):
  reset(grad);actions=[]
  for i in range(h):
   a=np.zeros(6,dtype=np.float32)
   if i==h-1:a[1]=value
   actions.append(a);t.step(a)
  loss=float(t.get_final_loss()['loss'])
  if not np.isfinite(loss):raise ValueError('Non-finite objective')
  if not grad:return loss
  t.reset_grad();t.get_final_loss_grad()
  for a in reversed(actions):t.step_grad(a)
  t.apply_agent_action_p_grad(pose)
  gradient=t.agent.get_grad(h)
  return loss,float(gradient[h-1,1])
 try:
  tic=time.time();value=config['gradient_control'];loss,ad=objective(value,True)
  samples=[]
  for epsilon in config['epsilons']:
   plus=objective(value+epsilon);minus=objective(value-epsilon);fd=(plus-minus)/(2*epsilon)
   error=abs(ad-fd);threshold=max(config['absolute_tolerance'],config['relative_tolerance']*max(abs(ad),abs(fd)))
   samples.append(dict(epsilon=epsilon,plus_loss=plus,minus_loss=minus,finite_difference=fd,absolute_error=error,threshold=threshold,within_tolerance=bool(np.isfinite(ad) and np.isfinite(fd) and error<=threshold)))
  informative=max([abs(ad)]+[abs(x['finite_difference']) for x in samples])>=config['minimum_gradient_magnitude']
  gate=informative and all(x['within_tolerance'] for x in samples)
  report['gradient']={'status':'PASS' if gate else 'FAIL' if informative else 'UNINFORMATIVE','base_loss':loss,'autodiff':ad,'finite_differences':samples,'informative':bool(informative),'seconds':time.time()-tic};save()
  print('Gradient result',json.dumps(report['gradient']),flush=True)
  if gate:
   # Bounded one-parameter gradient-descent pilot; not the upstream 500-iteration optimizer.
   theta=value;history=[]
   for i in range(config['optimizer_iterations_if_gate_passes']):
    loss,grad=objective(theta,True)
    candidate=float(np.clip(theta-0.0001*np.sign(grad),-0.02,0.02))
    trial=objective(candidate)
    accepted=trial<loss
    history.append(dict(iteration=i,control=theta,loss=loss,gradient=grad,candidate=candidate,candidate_loss=trial,accepted=accepted))
    if accepted:theta=candidate
   report['optimization']={'status':'completed_bounded_pilot','method':'one-parameter sign-gradient descent with forward acceptance check','iterations':history,'final_control':theta,'final_loss':objective(theta)}
  else:report['optimization']={'status':'blocked_by_gradient_gate','reason':'No optimizer inference/promotion when derivative check fails or is uninformative.'}
 except Exception as exc:
  report['gradient']={'status':'ERROR','error_type':type(exc).__name__,'error':str(exc)}
  report['optimization']={'status':'blocked_by_gradient_gate'};traceback.print_exc()
 report['status']='completed_with_gradient_gate';report['total_seconds']=time.time()-start;save()
except BaseException as exc:
 report.update(status='ERROR',error_type=type(exc).__name__,error=str(exc));save();traceback.print_exc();raise
