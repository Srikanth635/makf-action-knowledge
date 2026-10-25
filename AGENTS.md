# Project guidance for Codex

When resuming the saved 2026-10-25 checkpoint, read `docs/RESUME_HANDOFF.md` first.
It records the latest stopping point, recovery commands and ordered next steps.

## Mission
Build a reusable, world-model-agnostic knowledge system for generalized, stereotypical, and hypothetical robotic actions. The core semantic stack is AICOR, CRAM–AICOR, MAKF, and action-specific frames (currently pouring, grasping smoke test). **No SOMA**. DUL is the intended foundational ontology; PROV-O, OWL-Time, SOSA/SSN and QUDT are optional complementary references.

## Current implementation
- P1.1 ontology inventory, P1.2 pouring frame, P1.3 generic MAKF refactor and grasping smoke test, E1 LinkML extraction contract and offline validators: complete.
  E1 0.2 adds source-reporting categories with compatible old enum values; read
  `docs/E1_V02_MIGRATION.md` before migrating historical records.
- E2.1/E2.2 request/provider interfaces and deterministic offline prompt builder: complete; see `docs/E2_PROMPT_INTERFACE.md`.
- E2.3 OpenAI/fixture transports and a request-bound validation/quarantine runner: implemented. Live API access is verified and a three-candidate GPT-4.1 batch passed mechanical validation; scientific acceptance remains pending. Read `docs/CURRENT_PROGRESS.md` and `docs/experiments/e23_pouring/README.md`.
- Initial E3 local RDF export and expanded SHACL checks are implemented behind the
  optional `rdf` extra; see `docs/RDF_PUBLICATION.md`. Exports remain provisional.
  Human promotion, graph-store publication, TigerGraph and full OWL DL checking
  remain unimplemented. The publication vocabulary is still draft 0.1.
- Quantitative scalar evidence 0.1 has a packaged schema/FluidLab fixture and offline
  validator; see `docs/QUANTITATIVE_EVIDENCE.md`. Storage validity does not establish
  scientific comparison or execution eligibility. Quantitative RDF snapshots and
  SHACL/fidelity checks are implemented; code-audit findings remain provisional.
- Read `README.md`, `docs/CODEX_HANDOFF.md`, and `docs/E2_DEVELOPMENT_PLAN.md` before altering ontology modules or extraction behavior.

## Non-negotiable modeling rules
1. Represent **knowledge descriptions** and **action hypotheses**, not concrete robots, scenes, world states, task episodes, or physical pouring events.
2. Keep action-independent vocabulary in MAKF and specialized vocabulary in the pouring/grasping modules; preserve source IRIs.
3. Do not mutate the original `aicor-ontology.ttl` or `cram-aicor-ontology.ttl` files without explicit user approval. Both original ontologies declare the same IRI; CRAM–AICOR is the active local import target. Do not load both as distinct OWL ontologies without addressing this.
4. A hypothesis is not an asserted physical law. Preserve applicability conditions, modality, epistemic status, derivation status, provenance and exact citations to source passages. An LLM's new idea must not be attributed to a source.
5. Never fabricate source quotations or unknown ontology relationships. Prefer abstention/validation failure.
6. Do not claim official DUL imports, full OWL-DL reasoning, live LLM extraction, RDF population, or TigerGraph integration work until verified with tests.
7. Original user-provided ontologies have no blanket redistribution license; do not publish this repository without user permission. Never commit keys or credentials.

## Development commands
```bash
bash scripts/setup_codex.sh
.venv/bin/python -m pytest -q
.venv/bin/python verify_resources.py
.venv/bin/makf doctor
.venv/bin/makf validate pouring --profile pouring
.venv/bin/makf validate grasping --profile grasping
```
For existing active environment use `python -m pytest -q` and `makf doctor`.

## Coding expectations
- Python >=3.10, `src/` package layout, offline-first deterministic behavior, type hints for new code where practical.
- Preserve tests; add positive and negative tests for extraction changes. Avoid breaking package resource loading from installed wheels.
- Implement E2 behind optional dependencies and model-provider adapters, never requiring API keys for the default test suite.
- For live scientific validation, follow the user's preference for current GPT
  models: inspect API availability and record actual returned model IDs. The latest
  pilot used GPT-6.1 Sol and GPT-6 Astra; do not assume aliases establish quality.
- Do not send private document text or ontology content to an LLM unless a user has deliberately configured a model/provider.
- Keep E1 JSON and LinkML contract compatibility or document migrations with tests.
- Make bounded, reviewable commits, and explain validation results and outstanding limitations.
