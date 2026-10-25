# FluidLab local forward, gradient and optimization pilot

Completed on CPU using the pinned, headless runtime from
[smoke 001](../fluidlab_smoke_001/README.md). No physical-unit calibration or
published-result reproduction is claimed. This is development evidence, not a
validated pouring controller.

## Protocol and execution

[protocol.json](protocol.json) was saved before executing the cases. The upstream
code, numerical engine and runtime patch were unchanged. The config initial pose
`[0.6, 0.7, 0.5, 0, 0, 0]` was applied in each reset. Seed 0, 40,604 particles,
64³ grid, dt=0.0002 and ten substeps were used. Docker allowed four CPUs, 8 GiB,
no network and the existing headless hostname selection. Taichi used Arch.x64.

The run performed:

1. 100 zero-action steps.
2. 100 steps with only control component 5 set to 0.00115 (native angular control;
   no radian/second or SI interpretation asserted).
3. A four-step directional derivative check against two central differences.
4. Three bounded one-parameter sign-gradient updates, gated by that check.

Raw measurements, all 200 rollout samples, gradient probes and optimizer trials are
in [validation-report.json](validation-report.json). [validate_dynamics.py](validate_dynamics.py)
is the exact executed harness; [run.log](run.log) preserves progress and warnings.
Source/runtime identity and interpretation limits are in [provenance.json](provenance.json).

## Forward results

| Quantity at step 100 | Zero action | Small tilt |
| --- | ---: | ---: |
| Active particles | 40,604 | 40,604 |
| Active mass ledger, native units | 1.85870361328125 | 1.85870361328125 |
| Finite positions, velocities and recorded losses | All tested steps | All tested steps |
| Maximum speed, native units | 0.55239 | 0.58835 |
| Active WATER particles with y < 0.55 | 14 | 46 |
| Scaled step loss returned by upstream | 1.02947 | 1.19156 |
| Runtime for 100 steps | About 55.26 s | About 38.44 s |

Each trajectory spans 0.2 code-time units. The two cases total 200 steps, not one
200-step trajectory. The first includes initial JIT costs. Counts below y=0.55 are
an explicitly chosen movement diagnostic; they are not spillage or useful transfer
success, and source material labels must not be silently treated as measured real
liquid properties. Mass is the active-particle ledger, not a full conservation study.
These results do not establish that either controller is better at pouring.

## Directional derivative check

The objective is the sum of the first four upstream diff-loss steps. The original
`max_loss_steps` remains 1000, so the terminal attraction term at step 999 is not
included. This is a **partial milk-displacement diagnostic objective**, plus the
upstream constant terms, not the complete pouring objective.

The varied parameter was last-step action component 1 (vertical displacement
control), centered at 0.001. Changing only the final action keeps the detached
first-step position reference independent of the finite-difference perturbation.

| Method | Derivative | Absolute difference from autodiff | Relative difference |
| --- | ---: | ---: | ---: |
| Autodiff | 449.61508 | — | — |
| Central difference, epsilon 1e-4 | 443.82095 | 5.79413 | About 1.29% |
| Central difference, epsilon 3e-5 | 448.06798 | 1.54710 | About 0.34% |

The predeclared gate was finite/informative derivative magnitude >=1e-5 and, for
both differences, error <= max(0.01, 0.15 * max(abs(AD), abs(FD))). It passed.
The gate is permissive and this is one local direction at one pose/control value.
Two epsilon values do not establish a convergence region, contact-gradient accuracy,
or correctness for earlier controls, the full action space or long horizons.

## Bounded pilot

After the gate passed, three sign-gradient proposals decreased that same four-step
partial loss. Each proposal was checked with a fresh forward evaluation; only
lower-loss proposals were accepted. This is not the upstream Adam optimizer and
not its published 500-iteration experiment.

The last-step vertical control moved from 0.001 to 0.0007. The reevaluated initial
loss was 23.7832737 and final loss was 23.6804028: **about 0.43% lower**. Small repeat
numerical differences are visible in the raw records. This demonstrates local
accepted descent on a short diagnostic, not convergence or a learned pouring skill.

GPT-6 Astra was confirmed available and reviewed the result interpretation. Its
[advisory assessment](model-review.json) supports the restricted conclusions and
recommends repeat/noise characterization, wider epsilon sweeps, more directions,
and the terminal objective before stronger claims. It did not execute the tests
or provide independent scientific approval.

## Local knowledge records

[ingest_results.py](ingest_results.py) converts the completed run into six scalar
records: final total active-particle count, active-mass retention fraction, and
nominal numerical duration for each case. It preserves the raw report hash, explicit
metric definitions, native/unknown physical units and partial context.

[local-evidence.json](local-evidence.json) and its validation report pass the scalar
contract. The RDF export is at
`/workspace/makf-rdf-runs/local-fluidlab-validation-001/`: **six quantities,
226 quads**, with `evidence_origin=local_simulation` and review pending. Comparison
readiness and archival execution eligibility remain false. No original paper values
or model-selected research claims were replaced.

The numerical derivative and generic loss are retained in raw artifacts, rather
than forced into unsupported quantitative quantity kinds. The derived duration and
mass fraction state their formulas and inputs; neither invents a physical time or
mass scale. The active mass fraction is not a pouring success fraction.

Validation: four new offline ingestion checks and the relevant quantitative suite
pass (**47 tests** total); **50/50 resources** remain unchanged and verified. Inputs
with incomplete runs, missing steps or non-finite mass cannot produce an evidence
bundle. Data/RDF artifact hashes were checked separately.

## Repeat and next work

Use the image and prepared source from smoke 001, mount an empty output directory,
and run this harness as `python validate_dynamics.py` under the same Docker limits.
Use a new output path. It takes a few minutes on this CPU environment. No application
package code, original ontologies or upstream numerical source were changed.

Next, quantify repeat-evaluation noise, then sweep epsilon and additional control
directions/horizons/contact regimes with a predeclared protocol. Extend to the full
terminal objective before larger optimization. Separately define task-level outcome
metrics and longer baseline/tilt rollouts, then evaluate optimized controls on fresh
conditions. Physical unit calibration and matching the original published experiment
still require additional evidence.
