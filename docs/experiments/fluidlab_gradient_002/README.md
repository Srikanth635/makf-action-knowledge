# Expanded FluidLab gradient development checks

Four of five cases pass the saved development gate. The rotational case does not
provide two adjacent informative, stable finite-difference checks, so the broader
gate **fails**. The terminal diagnostic and further optimization were not run.
This identifies a validation gap; it does not establish an autodiff defect.

## Execution and evidence

[protocol.json](protocol.json) was saved before execution. The exact executed
[harness](gradient_sweep.py), [raw measurements](gradient-report.json) and
[runtime log](run.log) are archived. The original protocol was neither relaxed
nor retried after observing the results. All five planned cases completed without
a case error. The Docker command exited successfully; the scientific gate failed.

The runtime is the pinned CPU/headless environment from
[smoke 001](../fluidlab_smoke_001/README.md): source commit
`7295eb6ed7ee92b2be471fd30b432238577f28ce`, image
`sha256:acde0a489d16cbb51b54802672942fa130935b42519eec599011af7d70540888`,
Taichi 1.1.0, Python 3.7.17, Arch.x64, 40,604 particles, dt=0.0002 and ten
substeps. Docker had no network, four CPUs and 8 GiB. No integration equations,
material values or upstream numerical source were changed for this experiment.
The log records GPU fallback and an exit-time Taichi cache-lock warning; the
completed report and zero process exit were preserved.

The loss sums the first four or eight upstream diff-loss steps. Its original
`max_loss_steps=1000` remains in effect, excluding attraction at step 999. The
varied action occurs after the first step, preserving the first-step detached
reference across that case's perturbations. Initial pose is
`[0.6, 0.7, 0.5, 0, 0, 0]`, with the stated x offset in the fifth case. Pose
variation probes sensitivity; it does not establish a particular contact regime.

## Repeat variation

Five identical forward evaluations and three evaluations with reverse passes were
made at the first, four-step vertical base condition. The loss range across all
eight was **0.000118255615234375**; the three AD derivatives ranged over
**0.005950927734375**, around 449.63.

These are observed ranges at one condition, not statistical confidence bounds or
verified noise bounds at every pose, action or horizon. Float32 losses and parallel
accumulation can affect small differences; this experiment does not isolate the
cause of variability. No fixed-seed determinism claim is made.

The later base-case AD value (449.61667) is outside the initial three-repeat range
(449.62778–449.63373), further showing that those repeats are not a bound on later
evaluations. A post-run [float32 control audit](control-representation.json) records
represented actions: central-denominator differences from nominal `2*epsilon` are
at most 8.24e-7 in relative terms here. That small representation discrepancy does
not explain the rotational gap; loss quantization/cancellation remains a separate
limitation. Saved classifications still use the executed nominal-epsilon protocol.

## Directional results

Each parameter is centered at 0.001 in native control units. Action-step indices
start at zero. FD columns are central differences, computed from the raw losses.

| Case | Horizon / action step / component | AD | FD, eps=3e-4 | FD, eps=1e-4 | FD, eps=3e-5 | Case gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Vertical | 4 / 3 / 1 | 449.617 | 434.294 | 444.126 | 449.816 | PASS |
| Horizontal | 4 / 3 / 0 | -53.358 | -54.954 | -53.596 | -54.963 | PASS |
| Rotation | 4 / 3 / 5 | 11.479 | 12.029 | 11.415 | 8.965 | FAIL |
| Earlier vertical | 8 / 3 / 1 | 16373.485 | 15317.128 | 15897.217 | 16431.427 | PASS |
| Vertical, x offset +0.02 | 8 / 7 / 1 | -298.480 | -318.247 | -300.446 | -302.887 | PASS |

The gate requires signal separation above ten times the measured base loss range,
informative derivative magnitude above 1e-5, AD/FD error no greater than
`max(0.01, 0.05 * max(abs(AD), abs(FD))) + loss_range/epsilon + AD_range`, and
one-sided slope asymmetry at most 0.3. A case needs two adjacent passing epsilon
samples with FD relative change at most 0.1. The global gate requires no failed or
error case, at least three passing cases, and both eight-step cases passing.
These are predeclared development criteria, not scientifically calibrated accuracy
guarantees. In particular, the added empirical noise allowance means PASS does
not assert a strict 5% error bound.

For rotation:

- At eps=3e-4, one-sided slopes are 9.117 and 14.941. Their normalized asymmetry
  is 0.3898, exceeding 0.3, despite AD/central-FD agreement within the error gate.
- At eps=1e-4, the sample passes: AD=11.4793, FD=11.4155, asymmetry=0.0756.
- At eps=3e-5, the plus-minus loss signal is 0.0005378723, below the required
  0.0011825562. It is uninformative under this protocol. The FD change from the
  previous epsilon is also about 21.47%, exceeding 10%.

Thus there is only one qualifying rotational sample. The larger perturbation may
reflect curvature or nonsmooth behavior; the smaller one is insufficiently
separated from observed repeat variation. These measurements cannot identify an
incorrect derivative, a contact transition or a numerical-engine bug.

[verify_report.py](verify_report.py) independently recomputes differences, noise
allowances, sample flags, adjacent stability and the global gate from raw losses.
Its saved [verification result](verification.json) records 170 successful numerical
and consistency checks. This verifies report arithmetic, not simulator physics.

An API availability check confirmed the current GPT models; the actual returned
review model was `gpt-6-astra`. Its [advisory review](model-review.json) supports
the conservative interpretation and highlights the limited noise sampling,
float32 cancellation and need to record represented actions. The exact
[review input](reviewed-input.json) and [response](review-response.json) are retained.
The model did not execute the simulator, inspect all upstream loss code or provide
independent scientific approval. Source semantics above are based on the pinned
code audited separately, not inferred from the model's response.

The shortened eight-step terminal test was conditional on the broader gate and
remains unexecuted. Even a future pass of that test would not validate the original
1000-step objective. No optimization, pouring-success, SI-calibration or
published-result-reproduction claim follows from this experiment.

## Next work, in order

1. Measure repeat variation separately at each condition, including repeated
   rotational plus/minus losses. Check resets and record realized float32 action
   values. Preserve this failed gate and its criteria.
2. Run a fixed diagnostic grid around the rotational parameter to separate
   curvature, branch/contact sensitivity and cancellation. Audit angular-control
   mapping and loss/reference semantics. Treat this as exploratory calibration;
   choose a separate verification protocol before its execution rather than
   retrospectively changing this pass/fail result.
3. If parallel numerical variation dominates, compare an isolated single-thread
   CPU condition, recording it as a new runtime. Do not silently substitute it for
   these measurements or alter physics to obtain a pass.
4. Establish a new broader verification gate with per-condition noise measurements.
   After it passes, audit and test an explicitly shortened terminal objective,
   including the semantics of discrete particle selection and detached targets.
   Extend horizons toward the original objective before larger optimization.
5. Define task-level transfer/spillage metrics and evaluate controls against
   forward-only baselines and fresh conditions. Physical calibration and matching
   published results remain separate prerequisites for those claims.

The existing scalar/RDF schema has no derivative or generic-loss quantity kind.
These measurements stay in provenance-linked experiment artifacts; no unsupported
quantity kind, scientific approval or graph promotion was added. Existing paper
claims, prior local evidence and original ontologies remain unchanged.

## Recheck and reproduce

Run `.venv/bin/python docs/experiments/fluidlab_gradient_002/verify_report.py`
from the repository to verify the saved arithmetic offline. For a new simulation,
use the prepared source and image from smoke 001, copy this harness into the
source mount, and mount a new output directory containing this protocol at `/out`.
Run `python gradient_sweep.py` with the same container resource limits, no network
and a headless hostname containing `matrix`. Preserve the new output separately.
CPU execution takes a few minutes and need not be bitwise repeatable.
