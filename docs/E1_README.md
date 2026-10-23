# E1 — MAKF ontology-guided extraction contract

**Status:** E1 development baseline, 2026-10-23. The contract and its local structural/semantic tests are implemented; LLM extraction is **not** implemented (E2).

## Objective

Extract provisional **generalized, stereotypical, conditional and hypothetical knowledge ABOUT action types**, preserving multiple perspectives (intentional, causal, temporal, procedural, observational, epistemic, role, applicability, deviation), provenance and uncertainty.

**Out of scope:** scene graphs, actual robot configurations, physical container instances, action execution episodes, NEEM event data, trajectory planning, extracting actual numerical dynamics, or directly asserting unverified causal facts as true. Sample knowledge components are *abstract descriptions*.

## What has been built

| Artifact | Purpose |
|---|---|
| `schema/makf_extraction.linkml.yaml` | Canonical, action-independent LinkML **extraction contract**; classes, required slots, enums and provenance fields |
| `schema/makf_extraction.schema.json` | JSON Schema derived offline from the supported subset of the LinkML contract |
| `profiles/pouring.yaml` | Pouring-specific action/frame identity and ontology term focus |
| `profiles/grasping-smoke.yaml` | Second-action reuse test, **not** a full grasping ontology |
| `profiles/*_guidance.json` | Machine-readable contexts built from actual ontology classes, superclasses, existential restrictions and MAKF predicates |
| `examples/*.json` | Artificial, *synthetic* illustration only; **not sourced from any research paper** |
| `tools/schema_to_jsonschema.py` | Deterministic conversion from the supported LinkML subset to standard JSON Schema |
| `tools/validate.py` | Closed-world JSON validation, local OWL term grounding, RDFS subclass-path checks, source anchor checks, hypothesis and provenance checks |
| `tools/build_guidance.py` | Action profile → relevant ontology vocabulary, without loading all OWL into an LLM prompt |
| `tests/test_contract.py` | Positive and negative test suite |
| `ontology/` | Read-only copies of the P1.3 MAKF/pouring/grasping/DUL bridge modules and original expanded CRAM–AICOR TTL for reproducible offline term checks |

## Architecture

```text
Source paper passages       Existing OWL ontologies (AICOR / CRAM / MAKF / pouring)
         |                                        |
         |                         Action-specific vocabulary profile
         |                                        |
         +---------->  LinkML extraction contract <+
                                  |
                        E2: structured LLM output (future)
                                  |
                        E1: structural validation
                                  |
                       E1: ontology/link validation
                                  |
                      E1: source-anchor verification
                                  |
                 PROVISIONAL action knowledge candidates
                                  |
               E3: RDF knowledge descriptions + SHACL (future)
                                  |
                      TigerGraph projection (future)
```

## Example abstraction

One *candidate* (NOT a physical occurrence):

- `action_class`: `aicor:Pouring`
- `frame_class`: `paf:PouringKnowledgeFrame`
- abstract hypothesis node grounded to `paf:OrientationInducedEffluxHypothesis`
- `makf:hasApplicabilityCondition` → abstract `paf:OutflowEnabledCondition` component
- `makf:predictsPossibleEffect` → abstract `paf:FlowOnsetPredictionPattern` component
- epistemic status: `hypothesis`; modality: `possible`
- exact source passage and source support role, if supplied

In E1 these are **JSON knowledge candidates**, not automatically inserted RDF or asserted physical causal edges. The named ontology terms refer to OWL **classes** used to type possible descriptions; component IDs such as `hypothesis` are local aliases in a candidate, not physical individuals.

## Terminology and epistemic policy

Each candidate **must** include:

- **Perspective(s)** (action-neutral MAKF categories)
- **Knowledge kind** (definition, stereotype, conditional principle, strategy, hypothesis, script, observation, deviation)
- **Modality** (necessary/typical/conditional/possible/speculative)
- **Epistemic status** (definition/stereotype/conditional principle/hypothesis/proposed strategy)
- **Derivation mode** (`source_explicit`, `source_paraphrase`, `llm_inference`, `llm_proposal`)
- **Evidence status** (`source_anchored`, `not_assessed`, `corroborated`, `contradicted`, `unsupported`)
- **Grounding status** for each knowledge component (`grounded` or `needs_mapping`)
- **Provenance** (document, passage, verbatim quote, support role, optional offsets)

These axes are **not interchangeable**: citing a scientific paper does not prove a hypothesis; exact quote matching is not semantic entailment; a model's confidence is not scientific truth. `source_anchored` means an anchored quotation exists, not that the content was empirically verified. A new LLM hypothesis must remain epistemically tentative even if inspired by a source paragraph. The `corroborated` flag requires independent review in addition to the mechanical multiple-source check.

## Validation policy

The validator **rejects** unknown fields such as `robot_id` or `scene_id`, unknown ontology classes, wrong declared MAKF predicate domain/range, missing mandatory metadata, broken component references, source quotations that are absent from their cited passage, incorrect supplied offsets, and hypothesis nodes lacking structural applicability/effect relationships.

The validator **does not guarantee** that free-text content is world-agnostic or true. Nor does it prove that a quotation semantically entails an extracted paraphrase, that two documents are truly independent, or that all imported OWL axioms are consistent. A semantic support evaluation and human/domain review, when possible, remain necessary before promoting provisional candidates.

## Run offline

From the package directory:

```bash
python -m pip install -r requirements.txt
python tools/schema_to_jsonschema.py
python tools/build_guidance.py --profile profiles/pouring.yaml --out profiles/pouring_guidance.json
python tools/validate.py examples/pouring_hypothesis.json --profile profiles/pouring.yaml
python tools/validate.py examples/grasping_hypothesis.json --profile profiles/grasping-smoke.yaml
python -m pytest -q tests/test_contract.py
```

The **official LinkML CLI** is not installed in this build environment (package installation was unavailable due to blocked network). Thus **the canonical YAML has not yet been checked with LinkML's own metamodel/linter**. Our offline JSON Schema compiler implements only the subset used in this E1 contract. On a machine with LinkML installed, perform an additional LinkML schema validation/lint/generation comparison before E2. This distinction is deliberate.

The official DUL import is declared through the P1.3 alignment but not locally resolved; no complete OWL DL satisfiability/consistency check has been claimed.

## How to use for E2

1. Choose an action profile (`pouring.yaml`).
2. Extract a **real** passage from a paper and keep its exact text and locator.
3. Present the schema, profile and selectively generated ontology guidance to the LLM.
4. Ask the LLM for a provisional `ExtractionBatch` JSON; allow abstention if the passage contains no useful action knowledge.
5. Run the offline validator; reject invalid candidates without auto-adding vocabulary.
6. Run a separate source–claim entailment/verification step (not in E1), and keep unsupported/inferred claims tentative.
7. In E3, generate RDF description individuals, not physical action or world-model instances; use PROV-O for provenance and SHACL for graph validation.

**Do not** insert the E1 example fixtures into TigerGraph as scientific knowledge; they were invented solely for tests.

## Ontology alignment constraints

This package uses the **expanded CRAM–AICOR source only** under its shared ontology IRI (`http://aicor.knowledge/l2-ontology.owl`), avoiding simultaneous ambiguous imports of the original AICOR file. `https://w3id.org/aicor/...` namespaces are provisional logical IRIs, not claims of registered public hosting. Only locally declared OWL classes and MAKF object properties are accepted by default; unmapped concepts are explicitly marked `needs_mapping` rather than silently generating new class names.

SOMA is intentionally excluded.
