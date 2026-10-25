"""Execute the frozen 004 protocol in the pinned runtime, Python 3.7 compatible."""
import argparse
import hashlib
import json
import time
import traceback
from pathlib import Path

import numpy as np


def fingerprint(value):
    h = hashlib.sha256()
    def visit(x):
        if isinstance(x, np.ndarray):
            h.update(str((x.dtype.str, x.shape)).encode())
            h.update(np.ascontiguousarray(x).tobytes())
        elif isinstance(x, dict):
            for k in sorted(x):
                h.update(json.dumps(k).encode()); visit(x[k])
        elif isinstance(x, (list, tuple)):
            for child in x: visit(child)
        else:
            h.update(json.dumps(x).encode())
    visit(value)
    return h.hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['observer'], required=True)
args = parser.parse_args()
ROOT = Path('/out')
protocol = json.loads((ROOT / 'protocol.json').read_text())
report = {'protocol': protocol, 'mode': args.mode, 'status': 'running',
          'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'runs': [], 'terminal_test_executed': False, 'optimization_executed': False}


def save():
    p = ROOT / (args.mode + '-report.tmp')
    p.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    p.replace(ROOT / (args.mode + '-report.json'))


try:
    import gym
    import fluidlab.envs
    import taichi as ti
    from fluidlab.configs.macros import MILK, EPS
    from collision_observer_v2 import CollisionObserver

    t = gym.make('Pouring-v0', seed=0, loss=True, loss_type='diff', renderer_type='GGUI').unwrapped.taichi_env
    initial = t.get_state()['state']
    initial_hash = fingerprint(initial)
    original_max = t.loss.max_loss_steps
    milk = t.loss.particle_mat.to_numpy() == MILK
    observer = CollisionObserver(t.simulator) if args.mode == 'observer' else None
    report['runtime'] = {'backend': str(ti.lang.impl.current_cfg().arch),
                         'particle_count': t.simulator.n_particles, 'dt': float(t.simulator.dt),
                         'substeps': int(t.simulator.n_substeps), 'EPS': EPS,
                         'original_max_loss_steps': original_max, 'max_substeps_local': t.simulator.max_substeps_local,
                         'friction': float(t.agent.rigid.mesh.friction),
                         'collide_type': t.agent.collide_type}
    assert t.agent.collide_type == 'both' and t.agent.rigid.mesh.friction <= 10
    report['initial_template_sha256_before'] = initial_hash
    save()

    def evaluate(case, nominal, phase, label, grad=False, observe=False, epsilon=None, block=None):
        number = len(report['runs']) + 1
        print('Start', number, phase, case['id'], label, flush=True)
        t.loss.max_loss_steps = original_max
        t.loss.temporal_range = [0, case['horizon']]
        pose = np.asarray(protocol['base_pose'], dtype=np.float32)
        pose[0] += case['pose_offset_x']
        t.set_state(initial, grad_enabled=grad)
        t.apply_agent_action_p(pose)
        reset = fingerprint(t.get_state()['state'])
        if observer is not None:
            observer.enabled = observe
            if observe: observer.clear()
        actions, signs, branches = [], [], []
        for step in range(case['horizon']):
            action = np.zeros(6, dtype=np.float32)
            if step == case['action_step']: action[case['component']] = nominal
            actions.append(action)
            t.step(action)
            delta = t.simulator.get_x()[milk] - t.loss.init_particle_pos.to_numpy()[milk]
            branch = np.sign(delta).astype(np.int8)
            branches.append({'step': step, 'negative_per_axis': (delta < 0).sum(axis=0).tolist(),
                             'zero_per_axis': (delta == 0).sum(axis=0).tolist(),
                             'positive_per_axis': (delta > 0).sum(axis=0).tolist(),
                             'near_zero_per_axis': (np.abs(delta) < 1e-6).sum(axis=0).tolist(),
                             'sign_sha256': hashlib.sha256(branch.tobytes()).hexdigest()})
            if observe: signs.append(branch)
        loss = float(t.get_final_loss()['loss'])
        state = t.get_state()['state']
        if not np.isfinite(loss) or not all(np.isfinite(state[k]).all() for k in ['x', 'v', 'C', 'F']):
            raise ValueError('Non-finite forward loss/state')
        result = {'sequence': number, 'phase': phase, 'case_id': case['id'], 'label': label,
                  'epsilon': epsilon, 'block': block, 'nominal_control': nominal,
                  'represented_control': float(actions[case['action_step']][case['component']]),
                  'reset_state_sha256': reset, 'loss': loss,
                  'active_particles': int(state['used'].sum()), 'loss_branches': branches}
        if observe:
            result['observer'] = observer.export(ROOT / ('collision-%03d.npz' % number), case['horizon'])
            path = ROOT / ('loss-signs-%03d.npz' % number)
            np.savez_compressed(str(path), signs=np.asarray(signs))
            result['loss_sign_artifact'] = path.name
        if observer is not None: observer.enabled = False
        if grad:
            t.reset_grad(); t.get_final_loss_grad()
            for action in reversed(actions): t.step_grad(action)
            t.apply_agent_action_p_grad(pose)
            result['autodiff'] = float(t.agent.get_grad(case['horizon'])[case['action_step'], case['component']])
            if not np.isfinite(result['autodiff']): raise ValueError('Non-finite AD derivative')
        report['runs'].append(result)
        save()
        print('Done', number, 'loss', loss, 'AD', result.get('autodiff'), flush=True)

    if args.mode == 'observer':
        for case in protocol['cases']:
            if case['id'] not in protocol['instrumented_cases']: continue
            for i in range(protocol['instrumentation_reference_forward_repeats']):
                evaluate(case, protocol['base_value'], 'observer_reference', 'base_forward')
            for i in range(protocol['instrumentation_reference_ad_repeats']):
                evaluate(case, protocol['base_value'], 'observer_reference', 'base_ad', grad=True)
            eps = case['epsilons'][0]
            for label, sign in [('base', 0), ('plus', 1), ('minus', -1)]:
                evaluate(case, protocol['base_value'] + sign * eps, 'observed', label,
                         grad=sign == 0, observe=True, epsilon=eps if sign else None)
    report['initial_template_sha256_after'] = fingerprint(initial)
    report['initial_template_unchanged'] = fingerprint(initial) == initial_hash
    report['status'] = 'completed'
    report['completed_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    save()
except BaseException as exc:
    report.update(status='ERROR', error_type=type(exc).__name__, error=str(exc))
    save(); traceback.print_exc(); raise
