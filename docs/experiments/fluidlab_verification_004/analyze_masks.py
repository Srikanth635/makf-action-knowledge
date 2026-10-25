"""Validate NPZ observer exports and count observed branch identity changes."""
import hashlib
import json
import argparse
from pathlib import Path
import numpy as np

ROOT = Path('/out')
parser = argparse.ArgumentParser()
parser.add_argument('--report', default='main-report.json')
args = parser.parse_args()
report = json.loads((ROOT / args.report).read_text())
output = {'scope': 'Shadow branch observations, not exact compiled intermediates. Changes can reflect both numerical variation and parameter changes; no causal attribution.',
          'cases': [], 'artifacts_verified': []}
for name in report['protocol']['instrumented_cases']:
    runs = [r for r in report['runs'] if r['phase'] == 'observed' and r['case_id'] == name]
    if [r['label'] for r in runs] != ['base', 'plus', 'minus']:
        raise ValueError('Missing instrumented case')
    loaded = []
    for run in runs:
        obs = run['observer']
        with np.load(str(ROOT / obs['artifact']), allow_pickle=False) as data:
            grid, particles = data['grid_mask'], data['particle_mask']
            counts, minimum = data['counts'], data['minimum']
        if not (np.isfinite(minimum).all() and (counts >= 0).all()):
            raise ValueError('Invalid observer arrays')
        if counts.shape != (obs['frames'], 2, 7) or counts.sum(axis=0).tolist() != obs['counts_grid_particle']:
            raise ValueError('Counter mismatch')
        for domain, mask, key in [(0, grid, 'grid_mask_sha256'), (1, particles, 'particle_mask_sha256')]:
            if hashlib.sha256(mask.tobytes()).hexdigest() != obs[key]:
                raise ValueError('Mask hash mismatch')
            if not np.isin(mask, [0, 1, 2, 3]).all():
                raise ValueError('Unknown mask code')
            for column, selector in [(0, mask > 0), (1, mask >= 2), (6, mask == 3)]:
                if not np.array_equal(np.count_nonzero(selector, axis=1), counts[:, domain, column]):
                    raise ValueError('Mask/counter mismatch')
        with np.load(str(ROOT / run['loss_sign_artifact']), allow_pickle=False) as data:
            signs = data['signs']
        if not np.isin(signs, [-1, 0, 1]).all() or signs.shape[0] != len(run['loss_branches']):
            raise ValueError('Invalid loss sign snapshots')
        for step, item in enumerate(run['loss_branches']):
            if hashlib.sha256(signs[step].tobytes()).hexdigest() != item['sign_sha256']:
                raise ValueError('Loss branch hash')
            for value, key in [(-1, 'negative_per_axis'), (0, 'zero_per_axis'), (1, 'positive_per_axis')]:
                if (signs[step] == value).sum(axis=0).tolist() != item[key]:
                    raise ValueError('Loss branch count')
        loaded.append((grid, particles, signs))
        output['artifacts_verified'] += [obs['artifact'], run['loss_sign_artifact']]
    base = loaded[0]
    changes = []
    for run, arrays in zip(runs[1:], loaded[1:]):
        result = {'label': run['label']}
        for domain, initial, perturbed in [('grid', base[0], arrays[0]), ('particle', base[1], arrays[1])]:
            result[domain] = {
                'query_membership_changes_per_substep': np.count_nonzero((initial > 0) != (perturbed > 0), axis=1).tolist(),
                'contact_membership_changes_per_substep': np.count_nonzero((initial >= 2) != (perturbed >= 2), axis=1).tolist(),
                'friction_flag_changes_per_substep': np.count_nonzero((initial == 3) != (perturbed == 3), axis=1).tolist()}
        result['milk_sign_changes_per_action'] = np.count_nonzero(base[2] != arrays[2], axis=(1, 2)).tolist()
        result['milk_opposite_sign_changes_per_action'] = np.count_nonzero(base[2] * arrays[2] == -1, axis=(1, 2)).tolist()
        changes.append(result)
    output['cases'].append({'id': name, 'comparisons_to_single_observed_base': changes})
(ROOT / 'mask-analysis.json').write_text(json.dumps(output, indent=2) + '\n')
print('Validated', len(output['artifacts_verified']), 'observer artifacts')
