"""Validate completeness and summarize raw repeats offline, without a pass gate."""
import hashlib
import json
import math
import statistics
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def f32(value):
    return struct.unpack('=f', struct.pack('=f', value))[0]


def spread(values):
    return max(values) - min(values)


def analyze(report, protocol):
    require(report['protocol'] == protocol, 'Protocol mismatch')
    require(report['status'] == 'completed', 'Incomplete/error experiment')
    require([r['case'] for r in report['cases']] == protocol['cases'], 'Case mismatch')
    require(report['initial_template_unchanged'] and
            report['initial_template_sha256_before'] == report['initial_template_sha256_after'],
            'Initial template changed')
    require(not report['terminal_test_executed'] and not report['optimization_executed'],
            'Unexpected terminal or optimizer run')
    summary = {'scope': 'Exploratory calibration only; observed ranges are not confidence bounds.',
               'cases': [], 'verification_gate_status': 'not_executed'}
    all_runs = []
    reset_by_pose = {}
    for result in report['cases']:
        require(result['status'] == 'completed', 'Incomplete case')
        base, ad, tail = (result[k] for k in ['baseline_forward', 'baseline_autodiff', 'baseline_tail'])
        for runs, count in [(base, protocol['baseline_forward_repeats']),
                            (ad, protocol['baseline_autodiff_repeats']),
                            (tail, protocol['baseline_tail_repeats'])]:
            require(len(runs) == count, 'Repeat count')
        epsilons = protocol['rotation_epsilons'] if result['case']['component'] == 5 else protocol['standard_epsilons']
        require([p['epsilon'] for p in result['probes']] == epsilons, 'Epsilon sweep')
        baseline = base + ad + tail
        runs = list(baseline)
        base_values = [r['loss'] for r in baseline]
        ad_values = [r['autodiff'] for r in ad]
        base_median = statistics.median(base_values)
        ad_median = statistics.median(ad_values)
        case = {'id': result['case']['id'], 'baseline_loss_median': base_median,
                'baseline_loss_range': spread(base_values), 'autodiff_median': ad_median,
                'autodiff_range': spread(ad_values), 'samples': []}
        case['baseline_execution_groups'] = {}
        for label, group in [('forward', base), ('with_reverse_pass', ad), ('tail', tail)]:
            values = [r['loss'] for r in group]
            case['baseline_execution_groups'][label] = {
                'count': len(values), 'median': statistics.median(values),
                'min': min(values), 'max': max(values), 'range': spread(values)}
        case['tail_minus_initial_forward_loss_median'] = (
            statistics.median(r['loss'] for r in tail) - statistics.median(r['loss'] for r in base))
        for probe in result['probes']:
            for sign in ['plus', 'minus']:
                require(len(probe[sign]) == protocol['perturbation_repeats_per_sign'], 'Perturbation repeats')
                for run in probe[sign]:
                    expected = protocol['base_value'] + (1 if sign == 'plus' else -1) * probe['epsilon']
                    require(run['nominal_control'] == expected, 'Nominal perturbation')
            plus, minus = ([r['loss'] for r in probe[sign]] for sign in ['plus', 'minus'])
            p, m = (probe[sign][0]['represented_control'] for sign in ['plus', 'minus'])
            center = f32(protocol['base_value'])
            require(p > center > m, 'Degenerate represented perturbation')
            gap = p - m
            fd = (statistics.median(plus) - statistics.median(minus)) / gap
            lower = (min(plus) - max(minus)) / gap
            upper = (max(plus) - min(minus)) / gap
            local_range = max(spread(base_values), spread(plus), spread(minus), 1e-12)
            signal_ratio = abs(statistics.median(plus) - statistics.median(minus)) / local_range
            forward = (statistics.median(plus) - base_median) / (p - center)
            backward = (base_median - statistics.median(minus)) / (center - m)
            case['samples'].append({
                'epsilon': probe['epsilon'], 'represented_central_denominator': gap,
                'plus_loss_range': spread(plus), 'minus_loss_range': spread(minus),
                'central_difference_median_losses': fd,
                'central_difference_observed_envelope': [lower, upper],
                'empirical_signal_ratio': signal_ratio,
                'signal_separated': signal_ratio > protocol['empirical_signal_ratio_marker'],
                'ad_relative_discrepancy': abs(ad_median - fd) / max(abs(ad_median), abs(fd), 1e-12),
                'one_sided_forward': forward, 'one_sided_backward': backward,
                'one_sided_asymmetry': abs(forward - backward) / max(abs(forward), abs(backward), 1e-12),
                'observed_fd_and_ad_ranges_overlap': lower <= max(ad_values) and upper >= min(ad_values)})
            runs += probe['plus'] + probe['minus']
        hashes = set(r['reset_state_sha256'] for r in runs)
        require(len(hashes) == 1 and result['exported_resets_identical'], 'Exported reset mismatch')
        offset = result['case']['pose_offset_x']
        if offset in reset_by_pose:
            require(reset_by_pose[offset] == next(iter(hashes)), 'Same-pose reset changed across cases')
        reset_by_pose[offset] = next(iter(hashes))
        for run in baseline:
            require(run['nominal_control'] == protocol['base_value'], 'Nominal base control')
        for run in runs:
            require(run['represented_control'] == f32(run['nominal_control']), 'Float32 control mismatch')
            require(math.isfinite(run['loss']), 'Non-finite loss')
            if 'autodiff' in run:
                require(math.isfinite(run['autodiff']), 'Non-finite derivative')
            require(run['active_particles'] == report['runtime']['particle_count'], 'Active count changed')
            counts = run['milk_displacement_branch_counts']
            totals = [sum(values) for values in zip(counts['positive_per_axis'],
                      counts['negative_per_axis'], counts['exact_zero_per_axis'])]
            require(len(set(totals)) == 1, 'Invalid branch partition')
            require(all(0 <= n <= totals[0] for n in counts['abs_below_1e_minus_6_per_axis']), 'Invalid proximity counts')
        branches = [r['milk_displacement_branch_counts']['exact_zero_per_axis'] for r in runs]
        case['exact_zero_displacement_counts_per_axis_range'] = [[min(b[i] for b in branches), max(b[i] for b in branches)] for i in range(3)]
        case['exported_resets_identical'] = True
        case['evaluations'] = len(runs)
        summary['cases'].append(case)
        all_runs += runs
    require(sorted(r['sequence'] for r in all_runs) == list(range(1, len(all_runs) + 1)), 'Sequence gaps/duplicates')
    require(report['evaluations_completed'] == len(all_runs), 'Evaluation count')
    require(len(set(reset_by_pose.values())) == len(reset_by_pose), 'Different poses have identical exported state')
    summary['evaluations'] = len(all_runs)
    summary['autodiff_evaluations'] = sum('autodiff' in r for r in all_runs)
    summary['initial_template_unchanged'] = True
    summary['completeness_and_consistency_checks'] = 'passed'
    return summary


if __name__ == '__main__':
    raw = json.loads((ROOT / 'repeat-report.json').read_text())
    fixed = json.loads((ROOT / 'protocol.json').read_text())
    result = analyze(raw, fixed)
    execution = json.loads((ROOT / 'execution.json').read_text())
    history = ROOT.parent / 'fluidlab_gradient_002' / 'provenance.json'
    require(hashlib.sha256(history.read_bytes()).hexdigest() == execution['historical_gate_provenance_sha256'],
            'Historical provenance changed')
    for name, digest in json.loads(history.read_text())['files_sha256'].items():
        require(hashlib.sha256((history.parent / name).read_bytes()).hexdigest() == digest,
                'Historical artifact changed: ' + name)
    for name, digest in execution['input_sha256'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Executed input changed')
    require(result['evaluations'] == execution['expected_forward_evaluations'], 'Expected forward count')
    require(result['autodiff_evaluations'] == execution['expected_reverse_evaluations'], 'Expected reverse count')
    result['previous_failed_gate_unchanged'] = True
    (ROOT / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2, allow_nan=False))
