"""Recompute the saved experiment gate from raw losses; no simulator or API calls."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
protocol = json.loads((ROOT / 'protocol.json').read_text())
report = json.loads((ROOT / 'gradient-report.json').read_text())
checks = 0


def require(condition, message):
    global checks
    if not condition:
        raise ValueError(message)
    checks += 1


def number(actual, expected, label):
    require(math.isfinite(actual) and math.isclose(actual, expected,
            rel_tol=1e-12, abs_tol=1e-12), label)


require(report['status'] == 'completed', 'Incomplete run')
require(report['protocol'] == protocol, 'Protocol mismatch')
require([r['case'] for r in report['cases']] == protocol['cases'], 'Case mismatch')
noise = report['noise']
require(len(noise['forward_losses']) == protocol['forward_noise_repeats'], 'Forward repeats')
require(len(noise['autodiff_runs']) == protocol['autodiff_noise_repeats'], 'AD repeats')
losses = noise['forward_losses'] + [r[0] for r in noise['autodiff_runs']]
grads = [r[1] for r in noise['autodiff_runs']]
require(all(math.isfinite(x) for x in losses + grads), 'Non-finite noise data')
loss_range = max(losses) - min(losses)
ad_range = max(grads) - min(grads)
number(noise['loss_range'], loss_range, 'Loss range')
number(noise['autodiff_range'], ad_range, 'AD range')


def classify(result):
    if result['status'] == 'ERROR':
        require(bool(result.get('error')), 'Missing error detail')
        return 'ERROR'
    require([s['epsilon'] for s in result['samples']] == protocol['epsilons'], 'Epsilon order')
    loss, ad = result['loss'], result['autodiff']
    require(math.isfinite(loss) and math.isfinite(ad), 'Non-finite base data')
    informative, passing, differences = [], [], []
    for sample in result['samples']:
        eps = sample['epsilon']
        plus, minus = sample['plus_loss'], sample['minus_loss']
        forward, backward = (plus - loss) / eps, (loss - minus) / eps
        fd = (plus - minus) / (2 * eps)
        bound = loss_range / eps + ad_range
        tolerance = max(protocol['absolute_tolerance'],
                        protocol['relative_tolerance'] * max(abs(ad), abs(fd), 1e-12)) + bound
        asymmetry = abs(forward - backward) / max(abs(forward), abs(backward), 1e-12)
        separated = abs(plus - minus) > protocol['minimum_signal_to_noise'] * max(loss_range, 1e-12)
        useful = separated and max(abs(ad), abs(fd)) > 1e-5
        passes = useful and abs(ad - fd) <= tolerance and asymmetry <= protocol['maximum_one_sided_asymmetry']
        for key, value in [('fd', fd), ('noise_bound', bound), ('threshold', tolerance),
                           ('one_sided_forward', forward), ('one_sided_backward', backward),
                           ('asymmetry', asymmetry), ('ad_error', abs(ad - fd))]:
            number(sample[key], value, key)
        require(sample['informative'] == useful, 'Informative flag')
        require(sample['passes'] == passes, 'Sample gate')
        informative.append(useful)
        passing.append(passes)
        differences.append(fd)
    stable = []
    for i, (a, b) in enumerate(zip(differences, differences[1:])):
        change = abs(a - b) / max(abs(a), abs(b), 1e-12)
        number(result['adjacent_fd_relative_changes'][i], change, 'FD stability')
        stable.append(change <= protocol['adjacent_fd_relative_stability'])
    pair = any(a and b and s for a, b, s in zip(passing, passing[1:], stable))
    expected = 'PASS' if pair else 'FAIL' if any(informative) else 'UNINFORMATIVE'
    require(result['status'] == expected, 'Case gate')
    return expected


statuses = [classify(result) for result in report['cases']]
long_ids = ['earlier_vertical_h8', 'offset_vertical_h8']
long_pass = all(any(r['case']['id'] == name and r['status'] == 'PASS'
                   for r in report['cases']) for name in long_ids)
gate = ('FAIL' not in statuses and 'ERROR' not in statuses
        and statuses.count('PASS') >= protocol['minimum_informative_cases'] and long_pass)
require(report['broader_gate_passed'] == gate, 'Broader gate')
if gate:
    require(report['terminal']['case'] == protocol['terminal_diagnostic_if_gate_passes'], 'Terminal case')
    classify(report['terminal'])
else:
    require(report['terminal']['status'] == 'blocked_by_broader_gate', 'Terminal blocking')
print(json.dumps({'checks': checks, 'case_statuses': statuses,
                  'broader_gate_passed': gate, 'terminal_status': report['terminal']['status']}, indent=2))
