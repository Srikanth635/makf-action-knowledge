"""Run only the saved exploratory protocol inside the pinned FluidLab image."""
import hashlib
import json
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path('/out')
protocol = json.loads((ROOT / 'protocol.json').read_text())
report = {'protocol': protocol, 'status': 'running', 'cases': [],
          'terminal_test_executed': False, 'optimization_executed': False,
          'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}


def save():
    temp = ROOT / 'repeat-report.tmp'
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    temp.replace(ROOT / 'repeat-report.json')


def fingerprint(value):
    digest = hashlib.sha256()

    def visit(item):
        if isinstance(item, np.ndarray):
            digest.update(str((item.dtype.str, item.shape)).encode())
            digest.update(np.ascontiguousarray(item).tobytes())
        elif isinstance(item, dict):
            for key in sorted(item):
                digest.update(json.dumps(key).encode())
                visit(item[key])
        elif isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
        else:
            digest.update(json.dumps(item).encode())

    visit(value)
    return digest.hexdigest()


try:
    import gym
    import fluidlab.envs
    import taichi as ti
    from fluidlab.configs.macros import MILK

    env = gym.make('Pouring-v0', seed=0, loss=True, loss_type='diff', renderer_type='GGUI')
    t = env.unwrapped.taichi_env
    initial = t.get_state()['state']
    initial_hash = fingerprint(initial)
    original_max = t.loss.max_loss_steps
    milk = t.loss.particle_mat.to_numpy() == MILK
    report['runtime'] = {'backend': str(ti.lang.impl.current_cfg().arch),
                         'particle_count': t.simulator.n_particles,
                         'dt': float(t.simulator.dt), 'substeps': int(t.simulator.n_substeps),
                         'original_max_loss_steps': original_max}
    report['initial_template_sha256_before'] = initial_hash
    sequence = [0]

    def evaluate(case, nominal, grad=False):
        sequence[0] += 1
        t.loss.max_loss_steps = original_max
        h = case['horizon']
        t.loss.temporal_range = [0, h]
        pose = np.asarray(protocol['base_pose'], dtype=np.float32)
        pose[0] += case['pose_offset_x']
        t.set_state(initial, grad_enabled=grad)
        t.apply_agent_action_p(pose)
        reset_hash = fingerprint(t.get_state()['state'])
        actions = []
        for step in range(h):
            action = np.zeros(6, dtype=np.float32)
            if step == case['action_step']:
                action[case['component']] = nominal
            actions.append(action)
            t.step(action)
        loss = float(t.get_final_loss()['loss'])
        state = t.get_state()['state']
        if not all(np.isfinite(state[key]).all() for key in ['x', 'v', 'C', 'F']):
            raise ValueError('Non-finite exported particle state')
        delta = state['x'][milk & state['used'].astype(bool)] - t.loss.init_particle_pos.to_numpy()[milk & state['used'].astype(bool)]
        result = {'sequence': sequence[0], 'nominal_control': nominal,
                  'represented_control': float(actions[case['action_step']][case['component']]),
                  'loss': loss, 'reset_state_sha256': reset_hash,
                  'active_particles': int(state['used'].sum()),
                  'milk_displacement_branch_counts': {
                      'positive_per_axis': (delta > 0).sum(axis=0).tolist(),
                      'negative_per_axis': (delta < 0).sum(axis=0).tolist(),
                      'exact_zero_per_axis': (delta == 0).sum(axis=0).tolist(),
                      'abs_below_1e_minus_6_per_axis': (np.abs(delta) < 1e-6).sum(axis=0).tolist()}}
        if grad:
            t.reset_grad()
            t.get_final_loss_grad()
            for action in reversed(actions):
                t.step_grad(action)
            t.apply_agent_action_p_grad(pose)
            result['autodiff'] = float(t.agent.get_grad(h)[case['action_step'], case['component']])
        if not np.isfinite(loss) or ('autodiff' in result and not np.isfinite(result['autodiff'])):
            raise ValueError('Non-finite loss or derivative')
        return result

    for case in protocol['cases']:
        tick = time.time()
        current = {'case': case, 'status': 'running', 'baseline_forward': [],
                   'baseline_autodiff': [], 'probes': [], 'baseline_tail': []}
        report['cases'].append(current)
        save()
        try:
            value = protocol['base_value']
            for i in range(protocol['baseline_forward_repeats']):
                current['baseline_forward'].append(evaluate(case, value))
            for i in range(protocol['baseline_autodiff_repeats']):
                current['baseline_autodiff'].append(evaluate(case, value, True))
            save()
            print('Baseline', case['id'], 'losses', [r['loss'] for r in current['baseline_forward']],
                  'AD', [r['autodiff'] for r in current['baseline_autodiff']], flush=True)
            epsilons = protocol['rotation_epsilons'] if case['component'] == 5 else protocol['standard_epsilons']
            for epsilon in epsilons:
                probe = {'epsilon': epsilon, 'plus': [], 'minus': []}
                current['probes'].append(probe)
                for repeat in range(protocol['perturbation_repeats_per_sign']):
                    order = [('plus', 1), ('minus', -1)]
                    if repeat % 2:
                        order.reverse()
                    for label, sign in order:
                        probe[label].append(evaluate(case, value + sign * epsilon))
                save()
                print('Probe', case['id'], epsilon,
                      'plus', [r['loss'] for r in probe['plus']],
                      'minus', [r['loss'] for r in probe['minus']], flush=True)
            for i in range(protocol['baseline_tail_repeats']):
                current['baseline_tail'].append(evaluate(case, value))
            runs = current['baseline_forward'] + current['baseline_autodiff'] + current['baseline_tail']
            runs += [r for p in current['probes'] for side in ['plus', 'minus'] for r in p[side]]
            current['exported_resets_identical'] = len(set(r['reset_state_sha256'] for r in runs)) == 1
            current['status'] = 'completed'
            print('Completed', case['id'], 'resets identical:', current['exported_resets_identical'], flush=True)
        except Exception as exc:
            current.update(status='ERROR', error_type=type(exc).__name__, error=str(exc))
            traceback.print_exc()
        current['seconds'] = time.time() - tick
        save()
    report['initial_template_sha256_after'] = fingerprint(initial)
    report['initial_template_unchanged'] = report['initial_template_sha256_after'] == initial_hash
    report['evaluations_completed'] = sequence[0]
    report['completed_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    report['status'] = 'completed' if all(c['status'] == 'completed' for c in report['cases']) else 'completed_with_errors'
    save()
    print('Finished', report['status'], 'evaluations', sequence[0], flush=True)
except BaseException as exc:
    report.update(status='ERROR', error_type=type(exc).__name__, error=str(exc))
    save()
    traceback.print_exc()
    raise
