# Per-condition repeats and rotational sensitivity diagnostics

This is exploratory calibration following the failed broader gate in
[gradient 002](../fluidlab_gradient_002/README.md). It does not replace that gate
or authorize terminal tests or optimization. The protocol and executed inputs are
preserved separately from the historical experiment.

## Completed results

All **164 forward evaluations and 15 reverse passes** completed on CPU. Exported
restored-state hashes match within each condition and across conditions with the
same pose; the offset pose has a different hash. The initial-state template stayed
unchanged, all checked forward particle states and losses/derivatives were finite,
and all 40,604 active particles were retained. No terminal evaluation or optimizer
was executed. [repeat-report.json](repeat-report.json) retains every measurement;
[analysis.json](analysis.json) is the reproducible summary; [run.log](run.log)
preserves warnings. The Docker process exited zero; its exit-time Taichi cache-lock
warning is retained. These facts do not establish full internal reset determinism,
physical conservation or successful pouring.

The baseline loss range includes all ten base-control evaluations per condition.
AD ranges use the three reverse passes per condition.

| Condition | Baseline loss range | AD median | AD range |
| --- | ---: | ---: | ---: |
| Four-step vertical | 0.000106812 | 449.62494 | 0.0200195 |
| Four-step horizontal | 0.000135422 | -53.35726 | 0.000537872 |
| Four-step rotation | 0.000164032 | 11.47894 | 0.0162783 |
| Eight-step earlier vertical | 0.000762939 | 16374.9375 | 1.5214844 |
| Eight-step vertical, x offset +0.02 | 0.000961304 | -298.48154 | 0.0210876 |

Variability depends on the condition. These observed ranges cannot serve as global
uncertainty bounds, and even repeated observations do not bound all future runs.

For rotation, AD median is **11.47894**. The signal ratio uses that condition's
baseline and each perturbation's observed loss ranges, rather than the earlier
vertical-only noise estimate.

| Epsilon | FD from median losses | AD/FD relative discrepancy | Empirical signal ratio | Interpretation |
| --- | ---: | ---: | ---: | --- |
| 0.00030 | 12.03219 | 4.60% | 44.01 | One-sided asymmetry 0.377 |
| 0.00020 | 12.02106 | 4.51% | 29.31 | Coarser exploratory probe |
| 0.00015 | 11.47588 | 0.027% | 20.99 | Closer local agreement |
| 0.00010 | 11.42502 | 0.470% | 13.93 | Closer local agreement |
| 0.00007 | 11.25336 | 1.97% | 9.60 | Below separation marker |
| 0.00005 | 12.24518 | 6.26% | 7.47 | Below separation marker |
| 0.00003 | 11.82555 | 2.93% | 4.33 | Below separation marker |

The intermediate scales provide a useful candidate region for a new verification
experiment. The smallest scales lack sufficient empirical signal separation, and
the coarsest retains uneven one-sided slopes. This is consistent with sensitivity
to perturbation scale and numerical variation; it does not isolate the cause or
prove either correct or incorrect autodiff. There is no evidence here justifying
an arbitrary numerical-engine or physics change.

Many final MILK displacement components are exactly zero or near zero; their
aggregate counts vary across evaluations. This confirms proximity to absolute-loss
kinks in the recorded snapshots, without identifying particle-level branch
transitions or a causal link to the rotational discrepancy. Contact branches were
not logged. All historical gradient-002 artifact hashes were rechecked unchanged;
that broader gate remains failed.

The earlier-action eight-step case remains unresolved: at its finest epsilon
3e-5, median FD is 16415.13744 versus AD 16374.93750 (about 0.245% relative
discrepancy). Its observed FD envelope, 16407.50805–16421.74958, does not overlap
the observed AD range. This is larger than the sampled repeat variation, though
finite-step curvature and systematic rounding remain possible explanations.
Exploratory rotational agreement does not resolve this separate discrepancy.

GPT-6 Astra was confirmed API-listed and returned the recorded advisory review
as `gpt-6-astra`. Its [assessment](model-review.json) supports the restricted
interpretation and calls for fresh verification, more balanced/interleaved
measurements, execution-mode/drift reporting and source instrumentation. It did
not execute the simulator or independently approve the science. Exact input and
response are retained in [reviewed-input.json](reviewed-input.json) and
[review-response.json](review-response.json).

Post-review, the offline summary additionally reports forward/AD-associated/tail
baseline groups separately, including their median shifts. The review input stays
unchanged. A [source follow-up](review-followup.json) records another audit item:
the friction code divides by tangential speed before multiplying by a small-speed
flag. The bottle material has friction 0.1, selecting that source branch. A zero
speed could make this expression invalid; whether it occurred in these runs is
unestablished. No physics or derivative patch was made. Instrument that expression
and relevant branches before attributing any observed discrepancy to it.

## Fixed protocol and runtime

[protocol.json](protocol.json) was saved before execution. It specifies all five
previous conditions, with five forward baseline repeats, three baseline AD repeats,
and two more forward baseline repeats after the perturbation sweep. Every plus and
minus perturbation has three repeats; their execution order alternates by repeat
index to expose order sensitivity rather than always placing one sign first.

All cases use epsilons 3e-4, 1e-4 and 3e-5. Rotation additionally uses 2e-4, 1.5e-4,
7e-5 and 5e-5, in the order saved in the protocol. This requests **164 forward
evaluations and 15 reverse passes**. The grid is diagnostic, not an independent
verification set. No tolerance is adjusted after viewing the results.

The unchanged smoke-001 CPU image uses Python 3.7.17 and Taichi 1.1.0. Source commit
is `7295eb6ed7ee92b2be471fd30b432238577f28ce`; image ID is
`sha256:acde0a489d16cbb51b54802672942fa130935b42519eec599011af7d70540888`.
There are 40,604 particles, dt=0.0002 and ten substeps. Docker has four CPUs, 8 GiB,
no network and the existing headless hostname convention. [execution.json](execution.json)
records the arguments and input hashes; [repeat_probes.py](repeat_probes.py) is the
executed harness. Read-only diagnostic exports do not change the integration
equations, timestep or materials.

The objective still sums only four or eight upstream diff-loss steps, leaving
`max_loss_steps=1000`. The original terminal attraction term is excluded. The
first-step particle reference is unchanged by each tested action. Initial pose is
`[0.6, 0.7, 0.5, 0, 0, 0]`, with x offset +0.02 only in the fifth case.

## What is measured

Every evaluation records its loss, represented float32 control, chronological
sequence number, active-particle count and hash of the exported state immediately
after reset and pose application. The initial-state template is hashed before and
after execution. These checks cover exported particle state and agent
position/quaternion; they do not establish equality of every hidden simulator
buffer. Forward state finiteness is checked before the reverse pass.

The final active MILK displacement relative to the upstream first-step reference
is counted per axis as positive, negative, exactly zero and absolute magnitude
below 1e-6. These are loss-branch proximity diagnostics. Aggregate counts do not
identify which particles switched branches and are not contact counts.

[analyze_report.py](analyze_report.py) checks completeness, sequence continuity,
repeat counts, control representation, exported resets and unchanged historical
artifacts. It computes:

- Baseline loss ranges including forward, AD and final baseline repeats, and AD
  ranges separately for every condition.
- Central differences of median plus/minus losses using the actual represented
  float32 denominator, with an observed envelope from repeated loss extrema.
- One-sided slopes and asymmetry, AD/FD relative discrepancy, and a descriptive
  signal ratio using the largest observed baseline/plus/minus loss range.

Signal separation above ten is a diagnostic marker, not a pass gate. Neither
observed ranges nor envelopes are statistical confidence bounds; three repeats
can miss larger variability. They also do not capture deterministic float32
rounding bias. Promoting final losses to Python float does not recover lost
precision. No formal derivative-accuracy claim follows from this calibration.

## Source interpretation

[source-audit.json](source-audit.json) retains exact excerpts, line references and
whole-file hashes for seven inspected upstream files. Component 5 supplies the
third angular component, divided over ten substeps with configured scale 1. The
effector applies a world-coordinate quaternion rotation and normalizes it.
Physical angular units are not inferred from that implementation.

The initial-pose API applies position only; upstream has a TODO for orientation.
The experiments use the reset default orientation rather than claiming an
orientation-control test. The partial diff objective has zero WATER-distance
weight and L1 MILK displacement terms. Absolute-value kinks, collision conditions
and quaternion operations are possible sensitivity sources. The audit does not
identify a defect or prove which mechanism caused the earlier gap. Actual grid
collision branches are not instrumented in this experiment.

## Verification and future use

After the run, use `.venv/bin/python docs/experiments/fluidlab_noise_003/analyze_report.py`
to regenerate the offline summary from the archived report. It rejects incomplete
experiments and changed historical artifacts. No model or simulator is called by
that analysis. Eight corrupted-report controls were correctly rejected, including
missing repeats, inconsistent resets, non-finite losses and an unexpected terminal
run; see [analysis-negative-controls.json](analysis-negative-controls.json).
The 109-file runtime source check identifies only the two already recorded
compatibility patches; all 50 bundled project resources verify. A repeat simulation
must use a new output directory and retain its
own runtime and input provenance.

Exploratory agreement can identify a useful numerical scale for a future,
separately fixed verification protocol. It cannot retroactively turn gradient 002
into a pass. First add read-only diagnostics for the collision denominator and
relevant loss/contact branches; compare fresh-process and same-process resets.
Use more balanced/interleaved measurement ordering and separately reported baseline
groups in fresh verification. Keep the earlier-action discrepancy explicit and
assess finite-step curvature and rounding bias rather than assigning it to noise
alone. A new broader verification gate is required before any shortened
terminal diagnostic, followed by longer-horizon and original-objective checks.
These raw derivatives/losses remain experiment artifacts because the scalar/RDF
contract does not support those quantity kinds. Paper claims, graph approval
states and original ontologies are unchanged. Successful pouring, SI calibration
and paper reproduction remain unverified.
