import json,time,sys,traceback
from pathlib import Path
import numpy as np
start=time.time()
report={'test':'native-unit headless FluidLab forward smoke','simulation_steps_requested':2,'optimizer_run':False,'paper_reproduction':False,'si_calibration':False}
try:
 import taichi as ti
 import gym
 import fluidlab.envs
 print('Creating registered pouring environment',flush=True)
 env=gym.make('Pouring-v0',seed=0,loss=True,loss_type='diff',renderer_type='GGUI')
 e=env.unwrapped
 report.update(actual_backend=str(ti.lang.impl.current_cfg().arch),python_version=sys.version,taichi_version=list(ti.__version__),particle_count=e.taichi_env.simulator.n_particles,grid_resolution=list(e.taichi_env.simulator.res),dt=float(e.taichi_env.simulator.dt),substeps=int(e.taichi_env.simulator.n_substeps))
 obs=env.reset();initial=e.taichi_env.get_state_RL()
 assert np.isfinite(obs).all()
 initial_x=initial['x'].copy();report['steps']=[]
 masses=e.taichi_env.simulator.particles_i.mass.to_numpy()
 initial_active_mass=float(np.sum(masses[initial['used'].astype(bool)]))
 report['initial_active_mass_code_units']=initial_active_mass
 first_x=None
 for i in range(2):
  tick=time.time();obs,reward,done,info=env.step(np.zeros(6,dtype=np.float32))
  state=e.taichi_env.get_state_RL();x=state['x'];v=state['v']
  assert np.isfinite(obs).all() and np.isfinite(x).all() and np.isfinite(v).all() and np.isfinite(reward)
  assert len(x)==len(initial_x)
  active=state['used'].astype(bool)
  active_mass=float(np.sum(masses[active]))
  assert np.isclose(active_mass,initial_active_mass,rtol=1e-6,atol=1e-8)
  if i==0:first_x=x.copy()
  report['steps'].append(dict(step=i+1,reward=float(reward),done=bool(done),positions_finite=True,velocities_finite=True,particle_count=len(x),active_particle_count=int(np.sum(active)),active_mass_code_units=active_mass,max_displacement_from_initial=float(np.max(np.linalg.norm(x-initial_x,axis=1))),elapsed_seconds=time.time()-tick))
  print('Completed step',i+1,report['steps'][-1],flush=True)
 env.reset()
 env.step(np.zeros(6,dtype=np.float32))
 repeated=e.taichi_env.get_state_RL()['x']
 reset_error=float(np.max(np.abs(repeated-first_x)))
 report['reset_replay_max_position_error']=reset_error
 report['reset_replay_tolerance']=1e-5
 assert np.isfinite(repeated).all() and reset_error <= 1e-5
 report['total_forward_steps_including_reset_replay']=3
 report['status']='PASS';report['initialization_and_steps_seconds']=time.time()-start
 Path('/out/smoke-report.json').write_text(json.dumps(report,indent=2)+'\n')
except BaseException as exc:
 report.update(status='FAIL',error_type=type(exc).__name__,error=str(exc),elapsed_seconds=time.time()-start)
 Path('/out/smoke-report.json').write_text(json.dumps(report,indent=2)+'\n')
 traceback.print_exc();raise
