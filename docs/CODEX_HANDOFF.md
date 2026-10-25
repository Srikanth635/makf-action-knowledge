# MAKF Codex Cloud handoff

**Resume checkpoint, 2026-10-25:** start with
[RESUME_HANDOFF.md](RESUME_HANDOFF.md) for current achievements, unresolved issues,
portable artifacts and the next terminal-loss diagnostic. The current stopping
point is FluidLab verification 004, not the historical E2-only milestone below.

## Objective
Provide ontology-guided extraction of **generalized, stereotypical and hypothetical** knowledge about robotic action from scientific literature. Start with **pouring**. Keep the knowledge base robot-, scene-, world-model- and physical-execution-independent. Unlike world facts, knowledge-description individuals are allowed and useful.

## Conceptual architecture
Foundational DUL (+ optional PROV-O, OWL-Time, SOSA/SSN, QUDT) -> AICOR -> expanded CRAM–AICOR -> MAKF general action perspectives -> pouring and grasping (action-specific) -> LinkML E1 candidate extraction -> validation -> future RDF action description graph -> future TigerGraph GraphRAG. No SOMA.

## Implemented
- P1.1: traceable pouring ontology inventory, CSVs and descriptive report.
- P1.2: initial pouring multiperspective frame.
- P1.3: refactored MAKF core, pouring specialized module, grasping smoke-test, local ontology catalog and DUL alignment draft.
- E1: LinkML extraction contract, offline schema compiler, pouring/grasping action profiles, example candidates, structural/semantic validation and CLI.
  E1 is now 0.2 with source benchmark definitions, task objectives and reported
  observations; see [migration and semantics](E1_V02_MIGRATION.md). Old enum values
  remain valid. Prompt/review versions are v4/v3; the small current-model calibration
  is recorded in `experiments/e1_v02_validation_001`, with independent review open.
- E2.1/E2.2: typed source/request and provider interfaces, deterministic prompt/schema construction, bounded profile-selected context, and offline `makf prompt` CLI. See [interface and results](E2_PROMPT_INTERFACE.md).
- E2.3: optional OpenAI structured-output adapter, fixture transport, strict parsing, original-source validation and local run artifacts/quarantine. See [provider interface](E2_PROVIDER_INTERFACE.md).
- Initial E3: configurable local RDF export, E1/local-ontology checks, expanded
  packaged SHACL and content-bound advisory model selection. Install the `rdf`
  extra; see [export interface](RDF_PUBLICATION.md). Human promotion is unavailable.
- Reproducible Python installable package, offline `pytest` checks, installed-wheel data resources; see README.
- Quantitative evidence 0.1: strict scalar JSON contract, exact source/hash checks,
  bounded unit conversions, timing-conflict checks and separate storage/comparison/
  execution flags. Use `makf validate-quantitative fluidlab`; see
  [contract](QUANTITATIVE_EVIDENCE.md). Quantitative RDF snapshots and SHACL/fidelity
  checks are implemented. The versioned FluidLab audit preserves paper/code
  differences; native CPU execution and short gradient development checks now run.
  Exact paper-result matching, calibrated physical units and task validation remain open.

## Existing source layout
`src/makf_knowledge/` houses CLI, vocabulary guidance, OWL inspection, validation and schema support. `src/makf_knowledge/resources/ontology/` stores original and active TTL modules. `resources/profiles/` contain action-specific extractions. `historical_sources/` and `docs/` preserve prior work. `tests/` is the offline test suite.

## Open architectural risks
- Base AICOR and CRAM–AICOR claim the same ontology IRI; currently expanded file is active. Refactor versioned imports only after dedicated ontology review.
- DUL import is unresolved locally; tentative alignment is not proven OWL-DL consistent.
- Class restrictions do not encode temporal scripts, defeasible hypotheses, or evidence semantics on their own.
- Optional advisory model review exists, but reliable source-to-claim entailment remains unproven. Local provisional RDF/SHACL export is implemented; automated ingestion, authenticated human promotion and a graph DB adapter remain pending. The publication contract is still draft 0.1. See docs/CURRENT_PROGRESS.md for validation outcomes and remaining scientific review.
- Some existing restrictions force grasping and tilting as pouring subactions: assess whether this is overly restrictive for alternative strategies.

## Historical E2 continuation context
OpenAI credentials and network access are configured and verified. Continue reviewing the
[PourIt! pilot](experiments/e23_pouring/README.md). Review raw output, exact anchors,
epistemic status, scientific support, and whether claims generalize beyond the
reported experiment. Only after that live experiment evaluate OntoGPT as an
alternative, using the same passage and acceptance checks. The base runner accepts or quarantines an entire batch. An optional separate model
review, one explicit revision and audited subset selection are now available; see
[quality review](QUALITY_REVIEW.md). Never
silently upgrade unverified candidates into established facts.

## Validation recipe
`bash scripts/setup_codex.sh && .venv/bin/python -m pytest -q && .venv/bin/python verify_resources.py && .venv/bin/makf doctor`

## Current status
See [resume handoff](RESUME_HANDOFF.md) and [current progress](CURRENT_PROGRESS.md)
for the latest state and remaining work. Credentials stay securely outside Git.
