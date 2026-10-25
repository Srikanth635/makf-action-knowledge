# FluidLab prerequisite investigation, 2026-10-25

This investigation establishes a candidate **new native-unit reproduction** and
records what still prevents claiming a reproduction of the published experiment
or calibrated physical quantities. Original paper values and RDF eligibility
flags are unchanged. No FluidLab code, optimizer or simulator was executed.

Subsequent update: the [separate CPU smoke experiment](../fluidlab_smoke_001/README.md)
has now executed initialization and short forward/reset checks successfully. This
prerequisite report retains its original static-only scope; optimization, physical
calibration and exact published-result matching remain unverified.

## What is now established

The public OpenReview author note [Code Release](https://openreview.net/forum?id=wAAUKkoszGT),
dated 2023-02-09, explicitly says that the anonymous repository was transferred to
`https://github.com/zhouxian/FluidLab`. The retrieved note is preserved in
[author-code-release.json](author-code-release.json). This strengthens the official
repository provenance; it does not identify a particular paper-result checkpoint.

[reproduction-profile.json](reproduction-profile.json) pins commit
`7295eb6ed7ee92b2be471fd30b432238577f28ce`, 22 relevant source files with SHA-256,
and a candidate command/settings. Source snapshots are preserved in this directory.
The configuration and launch path specify:

| Setting | Pinned source value |
| --- | --- |
| Environment | Pouring-v0 |
| Seed | 0 |
| Optimizer / iterations | Adam / 500 |
| Learning rate | 1e-4 |
| Horizon | 1000 |
| Observed particles per body | 500 |
| Integration | dt=2e-4, nominal step=2e-3, 10 substeps in code units |
| Gravity | (0, -20, 0), physical scale unestablished |

The proposed command is recorded for a future isolated runtime; it was not run.
It would produce a new optimization result, not recover the authors' reported run.

## Concrete compatibility issue

Static inspection finds that `fluidlab/run.py` passes `renderer_type` to `gym.make`,
which forwards constructor arguments to the registered `PouringEnv`. The pinned
`PouringEnv.__init__` lacks that keyword and has no catch-all keyword parameter.
Its base class accepts the keyword, but that does not change the subclass signature.

[proposed-renderer-compatibility.patch](proposed-renderer-compatibility.patch) adds
the parameter, retains it and forwards it to the renderer setup. The patch applies
to the pinned source and the result parses. It has **not** been runtime-tested or
applied to the preserved source snapshots. Any reproduction using it must record
both the upstream commit and patch hash as a modified implementation.

[check_profile.py](check_profile.py) independently checks all 22 file hashes,
configuration values, integration arithmetic, the static signature mismatch, and
patch application/parsing. It never imports FluidLab. Run:

```bash
.venv/bin/python docs/experiments/fluidlab_prerequisites_001/check_profile.py
```

The saved result is [static-checks.json](static-checks.json). All integrity/config
checks pass; runtime and execution remain unverified.

## Published experiment artifacts

The pinned repository tree has no tracked `.pkl`, `.pickle`, `.npy`, `.npz`, `.pt`,
`.pth` or `.ckpt` files, and the GitHub responses list no public tags/releases. The
README describes generating trajectories into `logs/policies/{exp_name}`; logs and
targets are ignored by Git. These facts describe the inspected sources, not every
possible external distribution. See [discovery.json](discovery.json) for scope.

The paper metadata and public review search link the official repository, but no
matching per-run checkpoint/result manifest was found. Direct OpenReview forum/PDF
requests returned HTTP 403. Public search metadata was readable; no access control
was bypassed. Consequently, no camera-ready PDF byte comparison is claimed. The
existing arXiv v1 is preserved as the explicit paper version.

The inspected runtime manifest pins Python 3.7.13, Gym 0.21.0 and Taichi 1.1.0.
This project's Python 3.12 environment is not a verified replacement. The source
initializes Taichi with `arch=ti.gpu`. No `nvidia-smi` command or NVIDIA device nodes
were observed here; other compute/rendering backends have not been tested. Neither
GPU absence in general nor successful CPU fallback is inferred.

## Physical units

No physical length/time/mass reference scales were established by the inspected
paper, source paths and public release note. This is a bounded negative finding,
not a claim that an author cannot supply them. Values such as gravity -20, a cup
radius 0.18 or density 1.0 are insufficient to infer metres, seconds or kg/m³.
Even assuming physical gravity would constrain a length/time ratio, not determine
all reference scales; such an assumption would not be a reported calibration.

The paper's sim-to-real discussion concerns Latte Art (Stirring), Ice Cream
(Dynamic), Gathering and Mixing, not a calibrated fine-grained Pouring run. Its
qualitative demonstrations do not supply the missing pouring parameter scales.
The exact excerpt is retained in [paper-sim-to-real.txt](paper-sim-to-real.txt).

**Native-unit execution and physical-unit claims have different prerequisites.**
A tested implementation can be run and compared within its declared numerical
system without first converting to SI. Physical-unit conversion and comparison to
laboratory measurements require additional reference-scale/model evidence. The
archival scalar/RDF contract still intentionally marks execution unsupported.

## Next concrete actions

1. Create an isolated runtime compatible with the pinned dependency manifest and
   verify a usable Taichi compute/rendering backend. Apply the proposed patch in
   that isolated checkout and run a small native-unit smoke test before optimization.
2. Preserve a new run's exact source/patch/config/environment hashes, seed, hardware,
   time integration, initialization, loss definitions, output artifacts and numerical
   checks. Label it as a new reproduction experiment in code units.
3. For an exact paper-result claim, obtain a matching experiment manifest/checkpoint
   and identify the code/configuration that produced the published result. For SI
   claims, obtain physical reference scales or a documented calibration. The
   [clarification brief](clarifications.md) lists the required evidence; it was not sent.

These findings do not silently replace the paper density/timing values or enable
execution eligibility. Completing the public-source inspection cannot manufacture
missing experimental records or a compatible GPU/runtime.
