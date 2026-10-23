# MAKF Codex Cloud handoff

## Objective
Provide ontology-guided extraction of **generalized, stereotypical and hypothetical** knowledge about robotic action from scientific literature. Start with **pouring**. Keep the knowledge base robot-, scene-, world-model- and physical-execution-independent. Unlike world facts, knowledge-description individuals are allowed and useful.

## Conceptual architecture
Foundational DUL (+ optional PROV-O, OWL-Time, SOSA/SSN, QUDT) -> AICOR -> expanded CRAM–AICOR -> MAKF general action perspectives -> pouring and grasping (action-specific) -> LinkML E1 candidate extraction -> validation -> future RDF action description graph -> future TigerGraph GraphRAG. No SOMA.

## Implemented
- P1.1: traceable pouring ontology inventory, CSVs and descriptive report.
- P1.2: initial pouring multiperspective frame.
- P1.3: refactored MAKF core, pouring specialized module, grasping smoke-test, local ontology catalog and DUL alignment draft.
- E1: LinkML extraction contract, offline schema compiler, pouring/grasping action profiles, example candidates, structural/semantic validation and CLI.
- Reproducible Python installable package, offline `pytest` checks, installed-wheel data resources; see README.

## Existing source layout
`src/makf_knowledge/` houses CLI, vocabulary guidance, OWL inspection, validation and schema support. `src/makf_knowledge/resources/ontology/` stores original and active TTL modules. `resources/profiles/` contain action-specific extractions. `historical_sources/` and `docs/` preserve prior work. `tests/` is the offline test suite.

## Open architectural risks
- Base AICOR and CRAM–AICOR claim the same ontology IRI; currently expanded file is active. Refactor versioned imports only after dedicated ontology review.
- DUL import is unresolved locally; tentative alignment is not proven OWL-DL consistent.
- Class restrictions do not encode temporal scripts, defeasible hypotheses, or evidence semantics on their own.
- No source-to-claim semantic entailment judge, source ingestion, live model provider, fully populated RDF, SHACL, or graph DB adapter exists yet.
- Some existing restrictions force grasping and tilting as pouring subactions: assess whether this is overly restrictive for alternative strategies.

## Next milestone: E2
Build an optional LLM-backed extractor that accepts a **user-supplied** paper excerpt with source identity, assembles MAKF + action-profile guidance, generates candidate E1 JSON in schema-constrained form, runs deterministic validation, and outputs provisional candidates with traceable spans. Include an offline mock provider, rejecting tests, and a clean API for later OntoGPT comparison. Never silently upgrade unverified candidates into established facts. See `docs/E2_DEVELOPMENT_PLAN.md`.

## Validation recipe
`bash scripts/setup_codex.sh && .venv/bin/python -m pytest -q && .venv/bin/python verify_resources.py && .venv/bin/makf doctor`

## Current status
The package is source-available and tested locally. Codex Cloud deployment and live E2 extraction are not part of this commit. Keep experiments optional, with no provider key in the repository.
