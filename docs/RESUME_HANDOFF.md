# Resume here — checkpoint dated 2026-10-25

This is the continuation entry point after the user's weekly usage pause. The
checkpoint is intended for `origin/main` in `Srikanth635/makf-action-knowledge`.
Read this file, [current progress](CURRENT_PROGRESS.md), and
[system roadmap](SYSTEM_ROADMAP.md) before doing new work. Historical experiment
reports describe their own dates; later results do not rewrite earlier failures.

## Final objective

Build a reusable, ontology-guided system that extracts generalized, stereotypical
and hypothetical robotic action knowledge from research and qualified simulation
evidence. Start with pouring, retain grasping as a transfer smoke test, and keep
knowledge descriptions independent of particular robots, scenes and physical
episodes. Preserve exact evidence, conditions, uncertainty, disagreement and
provenance from sources through extraction, review, RDF and grounded retrieval.

The semantic direction is DUL alignment → active CRAM–AICOR/AICOR vocabulary →
generic MAKF perspectives → action frames → E1 extraction → validated provisional
claims and quantitative evidence → RDF snapshots → future curation/query/GraphRAG.
This is a conceptual dependency summary; see the roadmap for actual import risks.
No SOMA. Do not modify the original AICOR/CRAM–AICOR ontologies casually. Their shared
ontology IRI and unresolved official DUL import remain architectural review items.

## Achieved

| Area | Implemented and demonstrated | Remaining boundary |
| --- | --- | --- |
| Ontologies and extraction contract | P1.1–P1.3, pouring/grasping profiles, E1 0.2, local validators | Official LinkML tooling, foundation/import review and formal OWL-DL validation |
| Live extraction | Optional OpenAI transport, exact source anchors, request-bound validation and quarantine | Scientific support and ontology mappings need wider independent evaluation |
| Model review | Content-bound advisory selection and limited revision; GPT-6.1 Sol/GPT-6 Astra calibration | Small development controls are not held-out/domain validation or human approval |
| Research expansion | PourIt!, SoftGym and FluidLab passages, extraction/review records | Bulk automated ingestion, deduplication and cross-source contradiction policy |
| RDF | Local named-graph exports, SHACL and source-fidelity checks, preserved provisional status | Authenticated human promotion, graph-store publication, TigerGraph/GraphRAG |
| Quantitative evidence | Scalar schema, exact numeric/unit/source checks, derived timing checks, RDF export | Broad unit mappings, calibrated comparisons, vector/time-series semantics and execution eligibility |
| FluidLab provenance | Official-source linkage, pinned commit/config, paper/code discrepancies recorded | Exact paper-result matching and physical reference scales |
| Native execution | Isolated CPU smoke, short forward/gradient experiments, archived scripts/results | GPU behavior, long-horizon/task success and physical validation |

**OntoGPT has not been used or benchmarked yet.** It is a planned optional adapter,
to be compared on the same sources and acceptance criteria, not assumed to improve
quality. TigerGraph and production GraphRAG are also not implemented.

Live scientific checks followed the user's preference for current GPT models;
actual returned IDs and reviews are archived. Availability and quality must be
checked again when work resumes. An LLM assessment is advisory, not scientific
approval. No API call is needed to verify this checkpoint.

## Exact simulation stopping point

The latest report is [verification 004](experiments/fluidlab_verification_004/README.md).
It completed **177 forward evaluations and 34 reverse passes**, including the
separately declared observer correction. All five cases pass the saved development
gate at two fresh perturbation sizes each. The largest median AD/finite-difference
discrepancy is about **1.78%**, below the strict max-style 5%/0.01 engineering limit,
without an added noise allowance. This does not establish exact gradients.

The earlier-action eight-step residual remains about **0.45–0.47%** beyond observed
repeat envelopes. A fresh-process control shifts median AD by only about **0.00356%**;
it does not explain that residual. Exported reset hashes agree, but hidden-state
equivalence is unproven. Ranges are empirical observations, not confidence bounds.

A shadow observer originally used the local memory index, which is reused every
20 substeps. Its masks failed validation. Original records remain intact. A saved
amendment changed recording to global substep indices; only observer/reference
blocks were rerun. Corrected masks and synthetic zero-norm/indexing controls pass.
No zero/<=EPS/invalid normalization norm was observed in six corrected shadow
probes. These recompute inputs, not native compiled intermediates; they do not
establish backward or general contact safety.

All current derivative tests use four/eight-step partial MILK displacement loss,
excluding the original terminal attraction at step 999. **No terminal test or new
optimizer run was executed in verification 004.** The earlier pilot's three accepted
sign-gradient proposals reduced a four-step partial loss about 0.43%; they were
not full-task or published Adam optimization. Paper replication, SI calibration,
successful pouring and scientific promotion remain unverified.

## Next work, in order

1. Read [terminal audit](experiments/fluidlab_verification_004/terminal-audit.json).
   Native backward holds NumPy-derived target position, selected ranks/membership
   and attraction scale constant. Finite differences that recompute those fields
   include different dependencies. A target's position can move even when its ID
   stays the same; the helper runs in backward too.
2. Save a bounded protocol before any shortened-terminal run. Define and label
   recomputed-target and explicitly frozen-target diagnostics separately. Record
   target ID/position, membership/ranks, scale, actual controls and loss precision
   for every perturbation. A frozen diagnostic must keep fields fixed through both
   forward and backward. Do not silently change the original objective or equations.
3. Evaluate repeatability and derivatives for each diagnostic, preserving failures.
   Keep the earlier-action residual open; use per-component loss, precision and
   validated branch diagnostics rather than attributing it solely to repeat noise.
4. After suitable checks, extend horizons toward the original objective. Define
   task-level useful-transfer/spillage metrics and forward baselines before larger
   optimization or controller-quality claims; evaluate fresh conditions afterward.
5. Extend quantitative semantics only for supported evidence. Derivatives/generic
   losses currently remain raw artifacts; do not force them into unsupported scalar
   quantity kinds or treat archival validity as execution/comparison readiness.
6. Resume the broader knowledge-system roadmap: held-out/domain extraction review,
   OntoGPT comparison, reproducible document ingestion, curation/contradictions,
   reviewed RDF retrieval, then graph integration and grounded end-to-end questions.

There is no pending approval or model/background job to resume. Read saved reports
before rerunning expensive experiments. Do not relax prior gates or replace
historical measurements to obtain a pass.

## Recover on a new environment

From a clone of the pushed main branch:

```bash
bash scripts/setup_codex.sh
.venv/bin/python -m pip install -e '.[openai,rdf]'
.venv/bin/python -m pytest -q
.venv/bin/python scripts/restore_checkpoint.py --verify-only
.venv/bin/python scripts/restore_checkpoint.py --out-dir /workspace
.venv/bin/python docs/experiments/fluidlab_verification_004/analyze_verification.py
```

`restore_checkpoint.py` checks hashes and restores preserved external outputs to
the original `makf-*-runs`/audit paths beneath the chosen parent. It refuses to
overwrite differing content. Choose another parent if those paths already contain
different work. Original absolute paths in historical JSON are provenance, not a
reason to edit that JSON. [Checkpoint inventory](checkpoints/2026-10-25/README.md)
maps every preserved external file to its portable repository copy.

The API key stays outside Git. Configure `MAKF_OPENAI_API_KEY` securely in the new
environment only when live calls are needed; never paste it into source or commits.
Offline tests, RDF validation and saved-report analysis need no key.

The old simulation runtime is separate from the Python 3.10+ application package:
Python 3.7.17, Taichi 1.1.0, CPU, pinned FluidLab commit
`7295eb6ed7ee92b2be471fd30b432238577f28ce`. Do not try to run it inside the app venv.
Use [runtime reconstruction](experiments/fluidlab_smoke_001/README.md), including
`prepare_source.py`, Dockerfile, source hashes, dependency pins and runtime patch.
Managed environments must follow the cloud runtime skill's proxy/CA instructions;
the Dockerfile expects a trusted CA build secret named `ca`. Docker image layers
and downloaded upstream meshes are rebuilt, not stored in Git. Record a new image
identity after rebuilding; do not claim the historical image ID without checking.
Copy the desired experiment harnesses from `docs/experiments/` into the prepared
source mount and use fresh output directories and headless `matrix` hostnames.

## Final checkpoint validation

Full offline suite: **242 passed**. Bundled resources: **50/50 verified**. `makf
doctor` passes pouring/grasping structural examples. Existing RDFLib deprecation
warnings remain. Latest simulation workers and offline artifact/gate checks pass;
their limits are recorded above. This checkpoint adds portable recovery records,
not a new scientific result. No simulator or paid LLM run is needed for this save.

Suggested first prompt after the usage reset:

> Read AGENTS.md and docs/RESUME_HANDOFF.md. Verify the checkpoint, then continue
> from verification 004 with a predeclared shortened-terminal protocol that keeps
> recomputed-target and frozen-target modes distinct. Preserve the unresolved
> earlier-action residual and all prior experiment records.
