# Fresh gradient verification and collision instrumentation

This experiment follows the exploratory [repeat diagnostics](../fluidlab_noise_003/README.md).
It uses new finite-difference scales, a saved engineering gate, interleaved baseline
measurements, separate-process controls and read-only collision observations.
It does not replace or edit the failed gate in gradient 002.

## Completed outcome

The **fresh development gate passes all five cases**, including corrected observer
and fresh-process controls. The largest median AD/FD discrepancy is about **1.78%**.
All three simulation workers exited zero: **177 forward evaluations and 34 reverse
passes**, including the separately declared observer recording correction. The
synthetic observer controls add no FluidLab rollout or reverse pass.

| Case | Median AD | FD at first new epsilon | FD at second new epsilon | Relative discrepancies |
| --- | ---: | ---: | ---: | --- |
| Vertical | 449.62311 | 444.14418 | 445.21476 | 1.219%, 0.980% |
| Horizontal | -53.35796 | -52.92298 | -53.14348 | 0.815%, 0.402% |
| Rotation | 11.47043 | 11.62461 | 11.26637 | 1.326%, 1.779% |
| Earlier vertical | 16374.83496 | 16448.65115 | 16452.06848 | 0.449%, 0.469% |
| Offset vertical | -298.48260 | -300.59826 | -299.77153 | 0.704%, 0.430% |

The minimum observed signal ratio is about 14.94 and maximum one-sided asymmetry
about 0.275. [analysis.json](analysis.json) records every calculation and gate;
[main-report.json](main-report.json) and [fresh-report.json](fresh-report.json)
retain raw measurements. No terminal or optimizer test was executed.

The earlier-action residual is **not resolved**: AD remains about 74–77 units below
the fresh finite differences, outside their observed repeat envelopes. The fresh
process gives median AD 16374.25195 versus 16374.83496 in the main process, a shift
of only 0.58301 (about 0.00356%). Exported reset hashes match. This control does not
explain the residual, nor establish equality of all hidden buffers. A 5% engineering
pass does not establish mathematically exact or generally accurate derivatives.

Corrected shadow observations found no zero, <=EPS or invalid/huge tangential norms
in the six instrumented probes. Minimum grid norm was about 5.1941e-7, compared
with EPS=1e-12. There were no active particle-contact branches in these short runs;
particle normalization behavior under active contact was therefore not exercised.
The shadow probes cover the first epsilon of the two instrumented cases, not all
five cases, both epsilons or backward intermediates.

The validated [identity comparisons](observer-corrected/mask-analysis.json) show
grid contact-membership differences of 1–2 queries for rotation and 25–26 for the
earlier-action case, compared with a single observed base. Friction-flag differences
are larger. MILK sign changes also occur before the perturbed action, demonstrating
that parameter changes are not the sole explanation for differences between runs.
These are sample/frame identity comparisons, not numbers of unique physical
contacts or proof of the gradient residual's cause.

[observer_controls.py](observer_controls.py) exercises the actual corrected
observer with synthetic contact inputs. It verifies zero-norm detection, a nonzero
inward friction flag, and distinct global records for reused local indices. Its
[result](observer-corrected/observer-controls.json) passes. All twelve corrected
NPZ exports match their counts and saved hashes. Ten
[corrupted-report controls](analysis-negative-controls.json) were rejected or
blocked the gate as intended. All 50 bundled resources verify; 109 runtime source
files identify only the two previously documented compatibility patches.

An API availability check confirmed GPT-6 Astra; the actual returned review model
was `gpt-6-astra`. Its [advisory review](model-review.json) supports this restricted
engineering outcome, highlights the earlier-action residual and shadow-observer
limits, and recommends separately defined terminal modes. It did not execute the
tests or independently approve the science. Exact input/response are retained.
The tolerance formula below is a maximum, not an additive relative-plus-absolute
rule; the review notes that distinction.

## Protocol and execution

[protocol.json](protocol.json) and the original executable inputs were saved and
hashed before launch; [execution.json](execution.json) preserves that record.
The main worker requests 153 forward evaluations and 23 reverse passes; a new,
sequential fresh-process worker requests six forwards and three reverse passes.
Both use the pinned smoke-001 CPU image, seed 0, 40,604 particles, dt=0.0002 and ten
substeps, four CPUs, 8 GiB and no network. Original numerical source is unchanged.

| Verification case | Horizon / action step / component | New epsilon values |
| --- | --- | --- |
| Vertical | 4 / 3 / 1 | 0.00008, 0.00006 |
| Horizontal | 4 / 3 / 0 | 0.00008, 0.00006 |
| Rotation | 4 / 3 / 5 | 0.00014, 0.00011 |
| Earlier vertical | 8 / 3 / 1 | 0.000024, 0.000016 |
| Vertical, x offset +0.02 | 8 / 7 / 1 | 0.00008, 0.00006 |

Each case has three base-control AD evaluations, one before, between and after the
two epsilon blocks. Each epsilon has four paired repeats, with a base forward
evaluation before each pair. Sign order alternates exactly twice each way. Case
and epsilon order remain fixed, so this is balanced within a block, not randomized
over every possible ordering. The scales were chosen after experiment 003 but
before these new measurements; these are fresh development measurements, not an
independent scientific benchmark or new physical conditions.

The gate requires both scales in all five cases to meet strict AD/FD error
`max(0.01, 0.05 * max(abs(AD), abs(FD)))`, empirical signal ratio above ten,
one-sided asymmetry at most 0.3 and observed FD envelope relative half-width at most
0.1. The two FD values must differ by at most 10%. No empirical noise allowance is
added to the error tolerance. Observer/reference and fresh-process agreement and
absence of observed denominator hazards are additional requirements. These are
engineering screening criteria, not calibrated scientific accuracy guarantees.
Observed ranges/envelopes are not statistical confidence intervals.

The fresh-process check covers the earlier-action eight-step condition, comparing
three forward and three AD base evaluations in a new container with the main
worker's same-condition baselines. Loss tolerance is the larger of 0.001 and five
times the larger observed range. AD tolerance is the largest of 0.02, five times
the larger observed AD range, and 0.5% of the median derivative scale. Exported
reset hashes must match. This can detect gross process/reset dependence under
these criteria; it does not establish equality of all internal buffers.

## Read-only observations and recording correction

Separate Taichi kernels recompute grid and particle collision inputs immediately
before the original forward kernels. They record contact/friction branches and
tangential-speed denominators without dividing by those speeds or writing native
simulator fields. Python wrappers preserve the original `.grad` functions, and
observations are disabled during the reverse pass. Shadow arithmetic can differ
from actual compiled temporaries, so these are observations of recomputed inputs,
not exact traces of the native kernel's intermediate values.

The observer uses three grid/particle branch codes: queried/no contact, contact
without an active friction flag, and contact with the flag active. Zero denotes an
unqueried identity. It records zero, <=EPS and invalid/huge tangential norms,
per-global-substep minimum norms, and identity masks. Per-action MILK displacement
sign snapshots cover the short objective's L1 terms. One observed base and each
perturbation are compared; differences also include numerical variation and do
not establish causation.

The first observer had a recording-index bug: upstream reuses a local 20-substep
memory window. Using that index accumulated counters across time while overwriting
masks. The artifact validator rejected the mismatch. Original inputs, reports and
arrays are retained and excluded from branch-identity claims and the final observer
gate. [original-observer-validation.json](original-observer-validation.json)
records the failure; this was an observer defect, not an identified physics defect.

[instrumentation-amendment.json](instrumentation-amendment.json) was saved before
the corrected run. The corrected observer records by global substep while reading
native state at its local index. Only the two observer/reference blocks are rerun,
in a new sequential process: **18 additional forwards and eight reverse passes**.
Derivative criteria, the original numerical verification and historical files are
unchanged. Corrected artifacts live under `observer-corrected/`. This correction
does not justify discarding or replacing a failed numerical check.

The executable scripts are [verify_dynamics.py](verify_dynamics.py), the original
[observer](collision_observer.py), its [recording correction](collision_observer_v2.py)
and [corrected observer worker](verify_observer_repair.py). The offline
[mask validator](analyze_masks.py) checks identities against counters and saved
hashes. [analyze_verification.py](analyze_verification.py) independently computes
the gates from raw losses and verifies unchanged historical artifact hashes.

## Scope and next decision

Every numerical comparison still concerns a four/eight-step partial MILK
displacement loss, with original `max_loss_steps=1000`; the original attraction
term at step 999 is excluded. Initial orientation is the reset default; the pose
API's last three entries do not implement orientation control. There is no SI
calibration, original-paper result match, task-level pouring metric or scientific
promotion. Original ontologies and paper/RDF approval states are unchanged.

A passing development gate would justify auditing and then testing an explicitly
shortened terminal objective. That audit must distinguish the native backward
surrogate from finite differences that recompute NumPy-selected targets/ranks and
scales. It would not establish full-objective correctness or justify a larger
optimizer run. A failed gate instead requires retaining the specific failure and
diagnosing it without retrospective tolerance changes. Terminal/optimizer execution
is not an automatic action in this protocol.

The completed [terminal source audit](terminal-audit.json) finds that native
backward treats NumPy-derived target position, ranking/membership and height-count
scale as constants during differentiation. Recomputed-target finite differences
also include their dependence on the parameter. Even unchanged target identity
does not make the two equal, since its position can move. The helper runs in both
forward and backward, so freezing only forward would be insufficient.

Next save a bounded protocol for separately labelled recomputed-target and
explicitly frozen-target shortened diagnostics, recording those fields for every
perturbation. Keep the earlier-action residual open with component/precision and
branch diagnostics. Establish each diagnostic's repeatability before optimization
or longer-horizon claims. This is the next development step; the original
1000-step objective remains untested.
