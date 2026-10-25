"""Independently compute the frozen development gates from archived raw losses."""
import hashlib
import json
import math
import statistics as stats
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, label):
    if not ok:
        raise ValueError(label)


def f32(value):
    return struct.unpack('=f', struct.pack('=f', value))[0]


def values(rows, key='loss'):
    return [r[key] for r in rows]


def span(xs):
    return max(xs) - min(xs)


def agreement(reference, candidate, protocol):
    settings = protocol['control_agreement']
    ref_losses, test_losses = values(reference), values(candidate)
    ref_grad, test_grad = [r['autodiff'] for r in reference if 'autodiff' in r], [r['autodiff'] for r in candidate if 'autodiff' in r]
    loss_error = abs(stats.median(ref_losses) - stats.median(test_losses))
    loss_tolerance = max(settings['absolute_loss_floor'], settings['range_multiplier'] * max(span(ref_losses), span(test_losses)))
    grad_error = abs(stats.median(ref_grad) - stats.median(test_grad))
    grad_tolerance = max(settings['absolute_ad_floor'], settings['range_multiplier'] * max(span(ref_grad), span(test_grad)),
                         settings['relative_ad_floor'] * max(abs(stats.median(ref_grad)), abs(stats.median(test_grad))))
    return {'loss_error': loss_error, 'loss_tolerance': loss_tolerance,
            'autodiff_error': grad_error, 'autodiff_tolerance': grad_tolerance,
            'passed': loss_error <= loss_tolerance and grad_error <= grad_tolerance}


def analyze(main, fresh, protocol, corrected):
    for report, mode in [(main, 'main'), (fresh, 'fresh'), (corrected, 'observer')]:
        require(report['status'] == 'completed' and report['mode'] == mode, 'Incomplete worker')
        require(report['protocol'] == protocol, 'Protocol changed')
        require(report['initial_template_unchanged'] and report['initial_template_sha256_before'] == report['initial_template_sha256_after'], 'Initial template changed')
        require(not report['terminal_test_executed'] and not report['optimization_executed'], 'Unexpected execution scope')
        require([r['sequence'] for r in report['runs']] == list(range(1, len(report['runs']) + 1)), 'Run sequence')
        for row in report['runs']:
            require(math.isfinite(row['loss']), 'Non-finite loss')
            require(row['represented_control'] == f32(row['nominal_control']), 'Represented control')
            require(row['active_particles'] == report['runtime']['particle_count'], 'Active count changed')
            if 'autodiff' in row: require(math.isfinite(row['autodiff']), 'Non-finite AD')
    require(len(main['runs']) == 153 and len(fresh['runs']) == 6, 'Evaluation accounting')
    require(sum('autodiff' in r for r in main['runs']) == 23 and sum('autodiff' in r for r in fresh['runs']) == 3, 'Reverse accounting')
    require(len(corrected['runs']) == 18 and sum('autodiff' in r for r in corrected['runs']) == 8, 'Corrected observer accounting')
    gate = protocol['gate']
    output = {'scope': 'Predeclared engineering development gate; not physical/scientific correctness.', 'cases': [], 'observers': []}
    for case in protocol['cases']:
        rows = [r for r in main['runs'] if r['phase'] == 'verification' and r['case_id'] == case['id']]
        require(len(rows) == 27, 'Case run count')
        base = [r for r in rows if r['label'] in ['center', 'base_ad']]
        ads = [r for r in rows if r['label'] == 'base_ad']
        require(len(ads) == protocol['autodiff_repeats'] and len(base) == 11, 'Baseline counts')
        baseline, ad = stats.median(values(base)), stats.median(values(ads, 'autodiff'))
        require(all(r['nominal_control'] == protocol['base_value'] for r in base), 'Nominal baseline')
        result = {'id': case['id'], 'baseline_loss_range': span(values(base)),
                  'autodiff_median': ad, 'autodiff_range': span(values(ads, 'autodiff')), 'samples': []}
        require(len(set(r['reset_state_sha256'] for r in main['runs'] if r['case_id'] == case['id'])) == 1, 'Exported reset mismatch')
        for eps in case['epsilons']:
            subset = [r for r in rows if r['epsilon'] == eps]
            for block in range(protocol['paired_repeats']):
                labels = [r['label'] for r in subset if r['block'] == block]
                require(labels == (['center', 'minus', 'plus'] if block % 2 else ['center', 'plus', 'minus']), 'Balanced schedule')
            plus, minus = ([r for r in subset if r['label'] == label] for label in ['plus', 'minus'])
            require(len(plus) == len(minus) == protocol['paired_repeats'], 'Perturbation count')
            for group, sign in [(plus, 1), (minus, -1)]:
                require(all(r['nominal_control'] == protocol['base_value'] + sign * eps for r in group), 'Nominal perturbation')
            p, m, center = plus[0]['represented_control'], minus[0]['represented_control'], f32(protocol['base_value'])
            require(p > center > m, 'Degenerate perturbation')
            pl, mi = values(plus), values(minus)
            fd = (stats.median(pl) - stats.median(mi)) / (p - m)
            lower, upper = (min(pl) - max(mi)) / (p - m), (max(pl) - min(mi)) / (p - m)
            scale = max(abs(fd), abs(ad), 1e-12)
            ratio = abs(stats.median(pl) - stats.median(mi)) / max(span(values(base)), span(pl), span(mi), 1e-12)
            forward, backward = (stats.median(pl) - baseline) / (p - center), (baseline - stats.median(mi)) / (center - m)
            asym = abs(forward - backward) / max(abs(forward), abs(backward), 1e-12)
            tolerance = max(gate['absolute_ad_fd_tolerance'], gate['relative_ad_fd_tolerance'] * scale)
            halfwidth = (upper - lower) / (2 * scale)
            good = (abs(ad - fd) <= tolerance and ratio > gate['minimum_signal_ratio']
                    and asym <= gate['maximum_asymmetry'] and halfwidth <= gate['maximum_relative_fd_envelope_half_width'])
            result['samples'].append({'epsilon': eps, 'fd': fd, 'observed_fd_envelope': [lower, upper],
                'relative_ad_fd_discrepancy': abs(ad - fd) / scale, 'absolute_ad_fd_tolerance': tolerance,
                'empirical_signal_ratio': ratio, 'asymmetry': asym, 'relative_envelope_half_width': halfwidth,
                'passed': good})
        a, b = [s['fd'] for s in result['samples']]
        result['relative_fd_change'] = abs(a - b) / max(abs(a), abs(b), 1e-12)
        result['passed'] = all(s['passed'] for s in result['samples']) and result['relative_fd_change'] <= gate['maximum_relative_fd_change']
        output['cases'].append(result)
    for name in protocol['instrumented_cases']:
        references = [r for r in corrected['runs'] if r['case_id'] == name and r['phase'] == 'observer_reference']
        observed = [r for r in corrected['runs'] if r['case_id'] == name and r['phase'] == 'observed']
        require(len(references) == 6 and [r['label'] for r in observed] == ['base', 'plus', 'minus'], 'Observer schedule')
        require(set(r['reset_state_sha256'] for r in references + observed) ==
                set(r['reset_state_sha256'] for r in main['runs'] if r['case_id'] == name),
                'Corrected observer exported reset differs')
        control = agreement(references, [observed[0]], protocol)
        hazards = []
        for r in observed:
            counts = r['observer']['counts_grid_particle']
            hazards.append({'label': r['label'], 'zero_norm': sum(domain[2] for domain in counts),
                            'norm_at_or_below_EPS': sum(domain[3] for domain in counts),
                            'invalid_or_huge_norm': sum(domain[4] for domain in counts)})
        output['observers'].append({'id': name, 'baseline_agreement': control, 'hazards': hazards,
            'passed': control['passed'] and all(not any(h[k] for k in ['zero_norm', 'norm_at_or_below_EPS', 'invalid_or_huge_norm']) for h in hazards)})
    fresh_case = protocol['fresh_process_case']
    same = [r for r in main['runs'] if r['phase'] == 'verification' and r['case_id'] == fresh_case and r['label'] in ['base_ad', 'center']]
    require(len(fresh['runs']) == protocol['fresh_forward_repeats'] + protocol['fresh_ad_repeats'], 'Fresh repeats')
    require(all(r['case_id'] == fresh_case and r['nominal_control'] == protocol['base_value'] for r in fresh['runs']), 'Fresh case/control')
    fresh_control = agreement(same, fresh['runs'], protocol)
    fresh_control['exported_reset_match'] = set(r['reset_state_sha256'] for r in same) == set(r['reset_state_sha256'] for r in fresh['runs'])
    fresh_control['passed'] = fresh_control['passed'] and fresh_control['exported_reset_match']
    output['fresh_process_control'] = fresh_control
    output['original_observer_masks_valid'] = False
    output['observer_source'] = 'observer-corrected/observer-report.json; original local-index masks excluded'
    output['broader_development_gate_passed'] = (all(c['passed'] for c in output['cases'])
        and all(o['passed'] for o in output['observers']) and fresh_control['passed'])
    return output


if __name__ == '__main__':
    protocol = json.loads((ROOT / 'protocol.json').read_text())
    main = json.loads((ROOT / 'main-report.json').read_text())
    fresh = json.loads((ROOT / 'fresh-report.json').read_text())
    corrected = json.loads((ROOT / 'observer-corrected/observer-report.json').read_text())
    result = analyze(main, fresh, protocol, corrected)
    masks = json.loads((ROOT / 'observer-corrected/mask-analysis.json').read_text())
    require(len(masks['artifacts_verified']) == 12 and len(masks['cases']) == 2, 'Observer artifact verification')
    controls = json.loads((ROOT / 'observer-corrected/observer-controls.json').read_text())
    require(controls['passed'], 'Observer positive controls')
    amendment = json.loads((ROOT / 'instrumentation-amendment.json').read_text())
    for name, sha in amendment['replacement_inputs_sha256'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, 'Amended input changed')
    execution = json.loads((ROOT / 'execution.json').read_text())
    for name, digest in execution['input_sha256'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Executed input changed')
    for name, digest in execution['historical_provenance_sha256'].items():
        prov = ROOT.parent / name / 'provenance.json'
        require(hashlib.sha256(prov.read_bytes()).hexdigest() == digest, 'History changed')
        for file, sha in json.loads(prov.read_text())['files_sha256'].items():
            require(hashlib.sha256((prov.parent / file).read_bytes()).hexdigest() == sha, 'Historical file changed')
    result['historical_artifact_hashes_unchanged'] = True
    (ROOT / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2, allow_nan=False))
