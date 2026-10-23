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
- E2.1/E2.2: typed source/request and provider interfaces, deterministic prompt/schema construction, bounded profile-selected context, and offline `makf prompt` CLI. See [interface and results](E2_PROMPT_INTERFACE.md).
- E2.3: optional OpenAI structured-output adapter, fixture transport, strict parsing, original-source validation and local run artifacts/quarantine. See [provider interface](E2_PROVIDER_INTERFACE.md).
- Reproducible Python installable package, offline `pytest` checks, installed-wheel data resources; see README.

## Existing source layout
`src/makf_knowledge/` houses CLI, vocabulary guidance, OWL inspection, validation and schema support. `src/makf_knowledge/resources/ontology/` stores original and active TTL modules. `resources/profiles/` contain action-specific extractions. `historical_sources/` and `docs/` preserve prior work. `tests/` is the offline test suite.

## Open architectural risks
- Base AICOR and CRAM–AICOR claim the same ontology IRI; currently expanded file is active. Refactor versioned imports only after dedicated ontology review.
- DUL import is unresolved locally; tentative alignment is not proven OWL-DL consistent.
- Class restrictions do not encode temporal scripts, defeasible hypotheses, or evidence semantics on their own.
- No source-to-claim entailment judge, automated source ingestion, fully populated RDF, SHACL, or graph DB adapter exists yet. The OpenAI adapter has passed offline tests; live API/schema compatibility and scientific extraction are still unverified.
- Some existing restrictions force grasping and tilting as pouring subactions: assess whether this is overly restrictive for alternative strategies.

## Next milestone: E2
Supply OpenAI credentials through environment settings, then run the prepared
[PourIt! pilot](experiments/e23_pouring/README.md). Review raw output, exact anchors,
epistemic status, scientific support, and whether claims generalize beyond the
reported experiment. Only after that live experiment evaluate OntoGPT as an
alternative, using the same passage and acceptance checks. The runner currently
accepts or quarantines an entire batch and has no model-driven repair loop. Never
silently upgrade unverified candidates into established facts.

## Validation recipe
`bash scripts/setup_codex.sh && .venv/bin/python -m pytest -q && .venv/bin/python verify_resources.py && .venv/bin/makf doctor`

## Current status
The package and OpenAI adapter are tested locally. A live command was attempted
but stopped before network IO because no credential was configured. Keep
experiments optional, with no provider key in the repository.
