# Evidence needed for exact experiment / SI calibration

Prepared as a local clarification brief; no message has been sent to anyone.

- Which commit and full configuration produced the published fine-grained Pouring
  result? Include seed(s), optimizer variants/budget, loss definition and any code
  modifications, plus a checkpoint/result manifest and artifact hashes if available.
- Which densities were used: Table 4's 0.8/1.5 or the public code defaults 0.5/1.0?
  Was there an untracked material/configuration override?
- Is the intended integration 2e-3 seconds per step with ten 2e-4-second substeps?
  The paper states 1e-4 while the inspected code uses 2e-4. Identify the published run.
- Are coordinates, time, density and Lamé parameters intentionally in numerical
  simulation units? If physical conversion is intended, specify reference scales,
  constitutive assumptions, mass/volume conventions and calibration artifacts.
- Was the public pouring launcher tested with a renderer_type argument, or was a
  different launcher/constructor used? Identify runtime, Gym and Taichi versions.

A reply containing physical-looking numbers without source/version/calibration
provenance is insufficient for silently converting existing quantitative records.
