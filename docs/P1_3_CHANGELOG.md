# Changelog — MAKF modularization (2026-10-23)

## Refactor of P1.2 (v0.1) to P1.3 modular draft (v0.2)

- Extracted reusable MAKF core (18 classes, 31 object properties; action-neutral).
- Moved all 30 previous pouring-defined object properties to MAKF, generalizing `characterizesFlowState` to `characterizesExpectedState`.
- Moved previous `ActionKnowledgeFrame` and `PossiblePhasePrecedence` class IRIs to MAKF.
- Kept 37 pouring-specific classes with the same IRIs, rewriting restrictions to use MAKF properties and types.
- Created a separate bridge IRI for DUL-AICOR mapping; kept conservative, directional mappings and changed pouring's import to MAKF.
- Wrote a minimal grasping action-frame demonstration that reuses exactly the same 10 aspect predicates.
- Added an OASIS XML catalog with a single CRAM–AICOR mapping for the two source files' shared logical IRI.
- Added a complete 69-symbol P1.2 migration table, validation script, simple retrieval script, competency coverage, and source digests.
- Preserved original source files and full P1.2 ontology snapshots unchanged.

### Known unresolved items

- Official DUL OWL content has not been resolved locally and full DL reasoner testing has not been performed.
- Original CRAM–AICOR `Pouring` requires `hasSubaction some Grasping` and `... some Tilting`, which may restrict genuinely optional strategy semantics; not modified.
- The draft logical IRIs are not declared publicly resolvable.
- No world-model data, named physical events, or empirical validation is included.
