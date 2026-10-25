# Progress as of 2026-10-25

## Fresh partial-gradient development gate passes

[Verification 004](experiments/fluidlab_verification_004/README.md) completes 177
forward evaluations and 34 reverse passes across main, fresh-process and corrected
observer workers. All five cases pass both new perturbation scales under a saved
strict 5%/absolute-0.01 max-style gate, without added noise allowance. Maximum median
AD/FD discrepancy is about 1.78%. Fresh-process agreement and exported resets pass.

An observer recording bug around the reused 20-substep local-memory window was
caught and corrected using global recording indices. Original files are retained;
only the observer blocks were rerun under a saved amendment, with no numerical
criteria changes. Corrected masks validate, synthetic zero-norm/indexing controls
pass, and no denominator hazards were observed in the six shadow probes. Actual
native intermediates, backward safety and other contact conditions are unverified.

The earlier-action residual remains about 0.45–0.47%, beyond observed repeat
envelopes; the fresh-process median shift is much smaller. GPT-6 Astra's advisory
review supports a limited engineering pass, not exact gradient/physics validation.
All 50 bundled resources verify and historical experiment hashes remain unchanged.

Next run separately defined, bounded shortened-terminal diagnostics. The source
audit identifies NumPy-derived target/rank/scale fields held constant by native AD;
recomputed-target differences and explicitly frozen-target diagnostics are distinct
objectives. No terminal or optimizer run, original-horizon validation, SI calibration,
paper replication or scientific/RDF promotion is claimed.

## Per-condition noise and rotational diagnostics completed

The [repeat experiment](experiments/fluidlab_noise_003/README.md) completes 164
forward evaluations and 15 reverse passes over all five earlier conditions, with
three repeats of every perturbed loss and a denser rotational sweep. Exported reset
states match within conditions and same poses; the initial template is unchanged.
Baseline loss ranges vary from about 0.000107 to 0.000961. These are empirical
observations, not global/statistical error bounds or proof of full internal reset.

For rotation, finite differences at eps=0.00015 and 0.0001 differ from median AD
by about 0.027% and 0.470%. The three smaller probes lack sufficient signal
separation; the coarsest has asymmetric slopes. The measurements support a useful
exploratory scale window, not a numerical-engine fix or a new verification pass.
The previous failed gate is byte-for-byte preserved; no terminal or optimizer run
was performed. GPT-6 Astra's advisory review supports this scope; it also identifies
a remaining eight-step earlier-action discrepancy (about 0.245% at the finest probe)
outside the observed repeat ranges. Source inspection finds a possible zero-speed
normalization hazard in the friction branch; occurrence/causation is unestablished.
Next instrument these expressions/branches and reset controls, then predeclare
fresh verification with per-condition noise before terminal/longer-horizon checks. All 50
bundled resources verify; original ontology and paper/RDF approval states are unchanged.

## Expanded gradient checks: broader gate fails

The [expanded CPU experiment](experiments/fluidlab_gradient_002/README.md)
completed five cases with a protocol saved before execution: three finite-difference
step sizes per case, five repeated forward evaluations and three repeated AD
evaluations at the base condition. Four cases pass, including both eight-step
vertical cases. Rotation has only one informative passing step size; the larger
probe has excessive one-sided asymmetry and the smallest is noise dominated.
This is insufficient validation, not proof of a derivative bug.

The broader gate fails, so no terminal-objective test or further optimization was
run. All tests still concern a four/eight-step partial loss. Base loss variation is
0.00011826 and AD variation 0.00595093; those observed ranges do not bound every
other condition. Independent recomputation passes 170 arithmetic/consistency checks.
Next: per-condition repeat measurements and rotational sensitivity diagnostics,
then a separately fixed verification protocol before terminal and longer-horizon
tests. Existing paper evidence, scalar/RDF approval states and ontologies are unchanged.

## Local rollout, gradient and bounded optimization checks

The [local validation experiment](experiments/fluidlab_validation_001/README.md)
completed two 100-step CPU rollouts from the config initial pose, at zero and small
tilt controls. States/losses stayed finite and all 40,604 active particles and their
mass ledger were retained. These are short native-unit development checks, not
pouring success or physical validation.

One last-step vertical action derivative of a four-step partial objective agreed
with two central differences within about 1.29% and 0.34%. After the preset gate
passed, three one-parameter sign-gradient updates reduced that partial loss by
about 0.43%. This excludes the full terminal attraction objective and is not the
published Adam optimization. GPT-6 Astra's advisory review supports this scope.

Six scalar records are exported separately as pending local_simulation evidence at
`/workspace/makf-rdf-runs/local-fluidlab-validation-001/` (226 quads). Native unit
uncertainty and partial context remain explicit; paper claims/values were unchanged.
Forty-seven targeted ingestion/quantitative tests pass, including four new cases;
50/50 resources and the exported artifact hashes verify. Next: repeat/noise checks,
broader finite-difference/contact/horizon tests, then the full task objective.

## Executed FluidLab forward smoke

The [native-unit smoke test](experiments/fluidlab_smoke_001/README.md) now passes
in isolated Docker with Python 3.7.17, Taichi 1.1.0 and CPU PyTorch. Taichi's GPU
request fell back to Arch.x64; this is not GPU validation. Patched/headless
Pouring-v0 initialized 40,604 particles on a 64³ grid, took two zero-action steps
with finite states/rewards and unchanged active particle mass, and replayed the
first step after reset within 1e-5 tolerance (observed difference 1.19e-7).

The runtime patch only fixes renderer keyword forwarding and defers the optional
SDF-generator import; pinned precomputed glass data were used. Historical dependency
and OS-library startup issues are recorded in attempt logs. No integration equations,
timestep or material values were changed. Original source hashes and runtime patch,
image and dependency identities are archived. All 50 bundled resources remain valid.

This establishes a specific CPU forward-smoke capability, not sustained pouring,
gradient correctness, optimization success, SI calibration or paper-result matching.
Next: longer baseline/tilt checks, gradient checks, then a bounded optimization
pilot and qualified local-simulation ingestion. Existing paper/RDF flags remain
archival; the executed runtime evidence is stored separately.

## FluidLab prerequisites investigation

The [prerequisites report](experiments/fluidlab_prerequisites_001/README.md) now
links the official repository through a public author Code Release response and
pins a candidate native-unit reproduction profile with 22 hashed source snapshots.
Its config/seed/optimizer settings and timestep arithmetic pass offline checks.
A static launcher/constructor mismatch around `renderer_type` was found; an
unexecuted patch proposal applies and parses. GPT-6 Astra's advisory review supports
all six scoped investigation conclusions; it is not runtime/scientific validation.

The inspected sources did not identify an exact published checkpoint/result match
or physical reference scales. Direct OpenReview forum/PDF retrieval returned 403;
public search metadata was usable. Published-result and SI eligibility remain
unresolved. Native-unit execution does not require SI calibration, but needs a
tested compatible runtime/backend; this was not run. No paper values, E1/RDF
approval states, application validators or ontology files were changed.

Checks: 22 pinned file hashes, configuration values, static interface/patch checks
pass; 50/50 bundled resource hashes remain valid. The next practical increment is
an isolated native-unit smoke run with commit/patch/environment provenance.

## Quantitative RDF and FluidLab code audit

`makf export-quantitative-rdf` preserves scalar evidence, exact numeric text,
decimal values, source artifacts, issues and computed checks in a named RDF graph.
Scalar validation, JSON/RDF reconstruction and SHACL run before saving a bundle.
The ten-quantity paper snapshot has 441 quads; a separately code-annotated snapshot
has 525 quads. Both remain pending and blocked for execution/comparison.

The [FluidLab audit](experiments/fluidlab_code_audit_001/README.md) inspects two
pinned revisions, including a pre-arXiv commit. It identifies dt=2e-4 versus the
paper's stated 1e-4, different density defaults, and an observation budget of 500.
Exact experiment provenance and physical unit scales are unresolved. GPT-6 Astra's
advisory review flagged an unsupported ordering comparison, which was removed
while preserving the original review input. Paper quantities were unchanged.

Validation: **238 offline tests passed**, including 13 quantitative-RDF checks;
**50/50 resources verified**. An installed wheel exported the fixture outside the
checkout. Original ontologies and scalar evidence records remain unchanged.


## Quantitative scalar evidence milestone

The [quantitative evidence 0.1 contract](QUANTITATIVE_EVIDENCE.md) is implemented
with a packaged JSON Schema, a self-contained FluidLab fixture, a Decimal-based
validator and `makf validate-quantitative`. The four annex records become ten
source-backed scalar quantities. Storage passes with six unresolved-unit issues,
material-model ambiguity, incomplete context and a computed timestep conflict.
Original values are preserved. Comparison is blocked for this fixture; execution
is unsupported in this archival version. No quantitative RDF promotion is claimed.

Thirty quantitative regression checks pass, covering exact evidence, units,
dimensions, counts, conversions, signed values, precision and false eligibility
fields. The package has 48/48 verified resources. An installed wheel loaded the
schema/fixture and validated the ten quantities outside the checkout. The saved
report is `docs/experiments/corpus_expansion_001/quantitative-validation.json`.

## Current-model live validation

[Live E1 0.2 validation](experiments/e1_v02_validation_001/README.md) used API-listed
GPT-6.1 Sol and GPT-6 Astra. Both reviewed 12 fixed assistant-annotated controls
twice: 48/48 expected accept/reject decisions, with zero observed false acceptances
or rejections. Fresh GPT-6.1 extraction yielded three SoftGym and three FluidLab
claims; GPT-6 Astra selected all six and their RDF exports passed SHACL. They remain
provisional in separate new snapshots, with unresolved mappings preserved.

This is development calibration, not an independent held-out/domain evaluation.
Eight bounded calls were made, with no revision loop. The next quantitative
evidence milestone is saved in [QUANTITATIVE_SIMULATION_PLAN.md](QUANTITATIVE_SIMULATION_PLAN.md):
units/status, model context, exact evidence, derived values and explicit issues,
using the four FluidLab annex records as the acceptance fixtures.

## E1 0.2 reporting semantics

No background extraction/review/test tasks were running before this increment.
[E1 0.2](E1_V02_MIGRATION.md) adds benchmark definitions, task objectives and reported
observations, with matching source/status checks in E1 and SHACL. Extraction prompt
v4 and review prompt v3 distinguish these meanings and permit candid unresolved
mappings. Three assistant-authored migration proposals export successfully as
pending RDF records in `/workspace/makf-rdf-runs/semantic-v02-proposals/`.
The original model-selected collection remains at two claims; these proposals have
no carried-over model or human approval. Quantitative simulation semantics and live
review reliability still need work.

Validation: **195 offline tests passed**, **46/46 resources verified**, bundled
pouring/grasping doctor checks passed. The new pending export contains 168 quads
and three claims; it is separate from the model-selected research collection.

## Saved system direction

The agreed proposed path is saved in [SYSTEM_ROADMAP.md](SYSTEM_ROADMAP.md).
A [future RDF graph illustration](design/FINAL_RDF_GRAPH.md) shows the intended
claim/evidence/hypothesis structure; it is a design artifact, not implemented E3.

## Research corpus expansion

The [research/simulation pilot](experiments/corpus_expansion_001/README.md) adds
SoftGym and FluidLab: six exact source passages and four published simulation-setting
records. Eight bounded GPT-5.4 extraction/review/revision calls retained one new
SoftGym candidate. FluidLab candidates remain held; its settings are preserved in a
separate annex with unit, material-model and timing questions.

The local RDF collection now contains two provisional claims from two papers,
127 quads, and explicit source/review boundaries. It is saved at
`/workspace/makf-rdf-runs/research-expansion-001/`. This is published simulation
evidence, not newly executed simulations. Three new offline corpus checks pass;
46/46 resources remain valid. Semantic labels for benchmark definitions and reported
observations, plus inconsistent model-review treatment of `needs_mapping`, are
concrete blockers to reliable bulk expansion.

## RDF publication contract milestone

The next increment is now implemented: [local RDF export](RDF_PUBLICATION.md) via
`makf export-rdf` and a Python API, with a configurable data namespace, E1 checks,
expanded packaged SHACL, and new output bundles completed by an atomic manifest
marker. Optional model-selection status is bound to the original reviewed batch
and unchanged subset; otherwise records are pending. Human promotion is unavailable.
The selected PourIt! candidate was exported to
`/workspace/makf-rdf-runs/pourit-001/dataset.trig` with SHACL conformance. Its mapping
gap and provisional status are preserved. The paragraphs below record the preceding
design-fixture milestone.

Validation of the exporter increment: **185 offline tests passed**, including 42
publication checks; **46/46 resources verified**. An installed wheel exported the
grasping example successfully outside the checkout. Real-candidate contract/query
checks returned one provisional result and zero human-approved results. The original
44 resources, E1 contract and ontology files remain unchanged.

The [draft 0.1 contract](design/publication-v0.1/CONTRACT.md) now defines E1 field
mapping, stable versioned identifiers, source/candidate graph boundaries, provisional
review states and unresolved mappings. A worked RDF fixture preserves the real
selected PourIt! candidate: 61 quads, one provisional claim, two components and
exact evidence. It references ontology classes without asserting physical events.

Initial SHACL validation passes, alongside 19 mutation checks (one valid variant,
18 invalid variants rejected), deterministic rebuild and scoped SPARQL checks:
one provisional result and zero human-approved results. See the saved
[validation summary](design/publication-v0.1/validation-summary.json).
This is an executable design fixture, not a production exporter or full E3 gate.
E1, model prompts and original ontologies remain unchanged by this milestone.
Proposed label meanings still need domain review and independent evaluation.

## Quality review workflow

An optional [review and bounded revision workflow](QUALITY_REVIEW.md) now checks
evidence, scope and mappings separately. Review failures leave the batch unselected;
an explicit subset option records passing and withheld IDs without editing output.
GPT-5.4 experiment 014 retained one candidate with complete evidence and conservative
mapping; two were withheld. Review reliability is improved on a small calibrated
control set, but inconsistent epistemic judgments and broader validation remain
open. Final validation: 143 offline tests passed and 44/44 bundled resources verified. See the report for earlier false approvals/rejections and limitations.

## Latest candidate review

The [three-candidate review](experiments/e23_pouring/REVIEW.md) now includes
agent-proposed E1-compatible revisions, exact evidence annotations and regression
checks. The revisions cover all three annotated claims; human/domain review remains
pending. A fresh GPT-4.1 run (010) passed E1 but failed all three annotated coverage
checks and repeated scope/mapping errors. Prompt changes have not established
reliable scientific extraction. Run 009 exposed a strict-schema restriction on
multiline enum values; transport v2 now decodes evidence IDs to exact source text.
Prompt version is now v3. Validation: 125 offline tests passed and 44/44 resources verified. Historical results below describe earlier runs.

## Completed capabilities

| Stage | Verified capability | Remaining boundary |
| --- | --- | --- |
| P1.1 | Ontology inventory and provenance | Inventory is precomputed |
| P1.2/P1.3 | Pouring frame, generic MAKF refactor and grasping smoke test | Formal ontology review remains |
| E1 | LinkML-subset contract, local schema and semantic checks | Official LinkML tooling still unverified |
| E2.1 | Typed requests and provider interface | No automated document ingestion |
| E2.2 | Deterministic ontology-guided prompt; v2 clarifies components, graph endpoints and epistemic scope | Prompt compliance and grounding quality need broader evaluation |
| E2.3 | Fixture/OpenAI transports; authenticated live strict-output requests | Mini-model runs remain unreliable on graph semantics |
| E2.4 | Original-source validation, audit records, whole-batch quarantine, useful schema-error locations | No repair loop or source-to-claim entailment judge |
| E2.5 | Genuine PourIt! live feasibility pilot; three mechanically accepted provisional candidates | Scientific acceptance and broader evaluation remain pending |

The environment has Python 3.12, editable dev/openai dependencies and secure
MAKF_OPENAI_API_KEY configuration for api.openai.com. No secret is stored in Git.

## Live experiments and corrections

Artifacts remain outside the checkout at `/workspace/makf-live-runs/pourit-20261024-NNN`.
Every run retains its own prompt, transport request, report and raw response;
rejected responses were never edited or promoted. Runs are exploratory debugging,
not a controlled model benchmark (prompts changed between some runs).

| Run | Model | Result / diagnosis |
| --- | --- | --- |
| 001 | gpt-4.1-mini-2025-04-14 | HTTP 401 before publication applied |
| 002 | same mini snapshot | Quarantined: empty component arrays; also incorrect offsets |
| 003 | same mini snapshot | Quarantined: normalized whitespace in quotations |
| 004 | same mini snapshot | Null offsets enforced; quotations still normalized |
| 005 | same mini snapshot | Exact-source-line quotation enum fixed copying; hypothesis graph incomplete |
| 006 | same mini snapshot | Quarantined: prefixed/nonexistent component endpoints |
| 007 | same mini snapshot | Quarantined: predicate domain mismatch |
| 008 | gpt-4.1-2025-04-14 | Three provisional candidates; local mechanical validation PASS |

The final two runs used the same provider-neutral prompt instructions, apart from
batch identity; one successful larger-model run does not establish reliability.
Run 008 used 8,058 input and 1,234 output tokens. It returned strategy descriptions
and a conditional principle across procedural, causal, observational and deviation
perspectives; it did not validate extraction of a complete hypothesis graph.

Changes leave canonical E1 and original ontologies unchanged. The OpenAI transport
now constrains quotes to verbatim nonempty source lines and offsets to null;
other providers can still submit verified E1 offsets. Local attribution, exact
quote, grounding, domain/range and epistemic checks remain strict. This line-enum
approach is for bounded excerpts: large inputs need chunking/schema-budget work.

Validation: 113 offline tests passed; all 44 bundled resources verified; doctor and
both bundled action examples passed. Tests include empty-component diagnostics,
incorrect offsets, verbatim multiline quotation choices and mocked SDK transport.

## Scientific review of run 008

All three candidates remain provisional, not accepted scientific knowledge.

- Candidate 1 cites the initial strategy/failure line but omits the following line
  needed for its transparent-bottleneck explanation. Calling the method a
  stereotype generalizes beyond the single reported comparison. Mapping the
  estimation mechanism to aicor:PouringTemplate needs expert review.
- Candidate 2 captures the feedback strategy, but its cited line ends before the
  size-estimation comparison is complete. Include the next source line to cover
  the entire claim and retain the paper's experimental scope.
- Candidate 3 cites only the mask/feedback fragment, not the spillage outcome.
  "Mask of the liquid" adds specificity not established by this excerpt, and a
  conditional principle may overstate a particular AFA failure report.

No candidates were published to an ontology or graph. Exact quotation does not
prove that a quotation supports the whole statement.

## Pending work in order

1. Strengthen full-claim evidence coverage and experimental-scope qualification;
   evaluate against reviewed positive/negative examples before further live runs.
2. Evaluate ontology mappings and complete hypothesis graphs, including candidate
   links, applicability conditions, effects and strategy constraints. Establish
   repeatability on multiple passages and the grasping profile.
3. Compare OntoGPT against the same sources and acceptance checks; not yet run.
4. Add scientific pilot evaluation records and metrics. E2 as a whole is not
   complete merely because a live batch passes structural checks.
5. E3: a configurable local exporter, content-bound model selection and expanded
   SHACL checks are implemented. Authenticated human promotion, a graph-store
   transaction policy and TigerGraph integration remain pending. Continue the
   ontology and independent evaluation work before production promotion.
6. Resolve official DUL imports, formal OWL-DL checking and AICOR/CRAM-AICOR shared
   ontology IRI risks through a separate ontology review. Official LinkML validation
   and automated source ingestion remain outstanding.

Reusable setup instructions were saved during onboarding. These code changes are
local working-tree edits; no commit, push or new environment publication was made.
