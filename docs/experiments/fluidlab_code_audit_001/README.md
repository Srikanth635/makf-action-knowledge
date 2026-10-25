# FluidLab paper/code audit, 2026-10-25

This static audit compares the retained arXiv v1 paper evidence with the repository
linked by the official [FluidLab project page](https://fluidlab2023.github.io/):
[zhouxian/FluidLab](https://github.com/zhouxian/FluidLab).

Two revisions were inspected:

- `7295eb6ed7ee92b2be471fd30b432238577f28ce` (2023-12-15): fetched default-branch head.
- `51d06b4189922ebb3390ba3c14d0887e3e785a5c` (2023-02-09): the latest repository
  commit in the returned history dated before the paper's 2023-03-04 arXiv v1.

The historical simulator is under `fluidlab/engine/`; the later revision renamed
that directory to `fluidlab/fluidengine/`. Neither revision has been established as
the exact code/configuration used to produce the published experimental results.
Full fetched files and history remain at `/workspace/makf-source-audits/fluidlab-001/`.
[audit.json](audit.json) preserves ten exact, line-located excerpts with commit URLs,
file hashes and excerpt hashes. No downloaded code was executed.

## Findings

| Topic | Paper | Inspected code | Interpretation |
| --- | --- | --- | --- |
| Integration | 2e-3 seconds per step; ten substeps of 1e-4 seconds | `dt = 2e-4`; `n_substeps = int(2e-3 / self.dt)` in both revisions | Ten substeps imply a nominal 2e-3 code-time step. This differs from the paper's stated substep duration; it does not establish physical time scaling or intended paper settings. |
| Density parameters | Light 0.8; heavy 1.5 | Pouring uses MILK below WATER; `RHO[MILK]=0.5`, `RHO[WATER]=1.0`, with body initialization reading `RHO[material]` | Numerical defaults differ. No comparison to the paper's spatial ordering is asserted. |
| Material class | Prose says non-Newtonian; Table 4 says Liquid with μ=0, λ=277.78 | WATER/MILK map to MAT_LIQUID; μ=0 and λ=277.78 | Code supports the table's labels/parameters; it does not resolve all constitutive wording or experiment provenance. |
| Observation budget | 500 observed particles per fluid body | `_n_obs_ptcls_per_body = 500` | Supports observation budget, not total simulated particle count or verified runtime output. |
| Physical units | Material table gives no units | Audited paths do not establish physical reference scales | No SI density/modulus conversion is justified by this audit. |

GPT-6 Astra was confirmed available and used for one bounded advisory review of
these excerpts and the paper annex. It accepted four supplied findings and flagged
an unsupported claim comparing spatial order to the paper. That comparison was
removed from the assistant's revised audit; the original input is retained in
[audit-reviewed-input.json](audit-reviewed-input.json), along with the model's
[review](model-review.json). The revised finding was not re-reviewed until passing.
This is an evidence check, not human approval, full-paper review or execution proof.

## Quantitative graph snapshots

The paper-only quantitative export is at
`/workspace/makf-rdf-runs/quantitative-fluidlab-001/`: ten quantities and 441 quads.

[code-annotated-evidence.json](code-annotated-evidence.json) adds pinned code excerpts
and source/code mismatch issues to a separate input. All ten original quantity
objects remain unchanged. It validates and exports to
`/workspace/makf-rdf-runs/quantitative-fluidlab-code-audit-001/`: ten quantities and
525 quads. The source arithmetic conflict, unknown units and material ambiguity are
retained. Execution eligibility remains false, comparison remains blocked, and
review remains pending. Neither snapshot is merged automatically into E1 claims.

The remaining step is to identify the exact published experiment artifacts and
reference scales, then record a supported resolution. Do not silently replace the
paper values with repository defaults or call those defaults SI measurements.
