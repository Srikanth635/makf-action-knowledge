# Multiperspective Action Knowledge Framework — P1.2 refactor / P1.3 extraction

**Status:** tested modular OWL/Turtle draft, 23 October 2026; **not yet OWL 2 DL certified**.

**Objective:** describe generalized, stereotypical, and hypothetical knowledge about types of robotic actions from complementary perspectives. **Not** a robot, physical scene, world state, measured test case, or actual action event. This is a TBox-focused repository of OWL *descriptions*, not a populated world model. The `grasping-smoke.ttl` file is a minimal second-action architecture test, **not** a full grasping ontology.

## 1. Architecture

```text
Foundational layer:
  official DUL (owl:imports declared; external content NOT bundled)
              │
  AICOR Core   │   [same ontology IRI as expanded CRAM-AICOR]
              └────────────┐
                           ▼
  CRAM–AICOR (working source, unchanged) + selective DUL alignment
                           │
                           ▼
  MAKF core (18 classes, 31 object properties)
                           │
                  ┌────────┴─────────┐
                  ▼                  ▼
  Pouring action frame       Grasping smoke frame
  (37 classes)              (17 classes; proof of reuse)
```

The diagram shows **module dependencies**, not ontology subclasses. The bridge imports the CRAM–AICOR working source and DUL; MAKF imports the bridge; action frames import MAKF. Only the expanded CRAM–AICOR ontology is used under `http://aicor.knowledge/l2-ontology.owl`; the base file is retained separately for comparison. **Neither source was altered.**

Complementary foundational sources such as PROV-O (epistemic provenance), OWL-Time (event-time grounding), SOSA/SSN (actual observations), and QUDT (quantities) are **planned but not yet imported**. Do **not** introduce them indiscriminately into the generic TBox. **SOMA is excluded.**

## 2. Deliverables

| File | Role |
|---|---|
| `ontologies/dul-alignment.ttl` | Selective one-way AICOR→DUL subclass mappings; avoids event/category equivalence |
| `ontologies/makf-core.ttl` | Reusable action knowledge frame, ten composition links, phase/strategy/hypothesis/observation/deviation patterns |
| `ontologies/pouring-frame.ttl` | P1.2 content specialized to pouring using MAKF; no generic property redeclarations |
| `ontologies/grasping-smoke.ttl` | Independent action-specific test of the same ten MAKF composition relationships |
| `config/catalog-v001.xml` | Local ontology mapping, with CRAM–AICOR selected as the only mapping for the shared ontology IRI |
| `reports/migration_map.csv` | Every P1.2 class and object property (69 symbols) mapped to new location / IRI |
| `reports/REFACTOR_DECISIONS.md` | Traceable changes, semantic caveats and future consistency review |
| `reports/COMPETENCY_TESTS.md` | Perspective-level coverage and structural acceptance tests |
| `tests/validate_modules.py` | Reproducible structural validation with no live network dependency |
| `tools/query_frames.py` | Exploration of *declared* schema restrictions, not implied world knowledge |
| `legacy/` | Unmodified previous P1.2 OWL versions for diff/migration |
| `sources/` | Unmodified user-supplied AICOR and CRAM–AICOR source files |

## 3. Reuse pattern

**MAKF is action-neutral.** It names no specific action and defines reusable descriptions:

- `makf:ActionKnowledgeFrame`: action-category knowledge frame, subclass of `dul:Description`
- `makf:RolePerspective`, `makf:TemporalPerspective`, `makf:StrategyPerspective`, `makf:HypothesisPerspective`, `makf:ObservationPerspective`, `makf:DeviationPerspective`, `makf:ApplicabilityPerspective` (plus intentional/causal links to AICOR)
- `makf:PhasePattern`, `makf:PossiblePhasePrecedence` (phase *descriptions*, not OWL-Time event intervals)
- `makf:GeneralizedStrategy` (subclass of `dul:Plan`; intentionally does **not** impose AICOR `GeneralizedActionPlan` restrictions on all actions)
- `makf:ActingHypothesis` (subclass of generic `aicor:Hypothesis`, not evidence-bound `aicor:ManipulationHypothesis`)
- `makf:ApplicabilityCondition`, `makf:PredictedEffectPattern`, `makf:ObservationPattern`, `makf:DeviationPattern`

A specific action contributes subclasses and `owl:someValuesFrom` restrictions to specialize this vocabulary. The generic `hasActionCategory` property ranges over **descriptions**; action-specific existential restrictions constrain it to a generalized AICOR action category such as `aicor:Pouring` or `aicor:Grasping`, never to `dul:Action` (a physical action occurrence). `hasPerspective` and its subproperties retrieve action descriptions, not scene facts.

**Pouring** reuses the existing `aicor:Pouring`, `PouringIntention`, `PouringTemplate`, phase/state knowledge, generic plan semantics, and role classes. It defines only pouring-specific structures and candidate hypotheses.

**Grasping** proves reuse of the *same* core restrictions with `aicor:Grasping`, a generic intention, force-dynamic template, role pattern, contact phases, and a **conditional** contact-stability hypothesis. These are schema declarations, **not** a validated physical grasp model.

## 4. Why hypothesized effects do not become facts

`makf:predictsPossibleEffect` links a **reified hypothesis description** to an effect **pattern**, and `makf:hasApplicabilityCondition` links the hypothesis to *abstract* conditions. No ontology imports or asserts a particular robot, bottle, execution, actual observed flow, grip force or scene. In OWL, an existential restriction creates a logical requirement for *instances* of a class (potentially anonymous fillers), but **it does not prove that the described physical effect occurred**.

Do not treat these restrictions as temporal ordering constraints over actual events, physical necessity, universal causal rules, probabilities, tested evidence, or approved safety claims. More expressive defeasible reasoning or evidence evaluation may be built on top later.

## 5. Running validation

From the package root, with Python and RDFLib installed:

```bash
python tests/validate_modules.py
python tools/query_frames.py
```

The validator tests Turtle parseability, imports/catalog topology, source symbol references, no newly named physical individuals, perspective links across pouring and grasping, hypothesis restrictions, and completeness of the migration map. It produces `reports/validation_summary.json`.

**It does not resolve the official DUL import, infer the full imported OWL axioms, run a description logic reasoner, or establish satisfiability/consistency.** The official DUL document is not bundled: a verified pinned distribution must be obtained before complete reasoning tests. The import IRI was verified against published DUL documentation, including `dul:Description`, `dul:Plan`, `dul:definesRole`; no claim is made that online dereferencing works locally.

## 6. Import/version policy (current limitation)

The two user-provided sources declare **the same** ontology IRI, so importing both simultaneously is ambiguous. `config/catalog-v001.xml` directs that IRI to CRAM–AICOR as the complete working source; the original AICOR remains archival/reference only. Long-term, the owners should make **distinct ontology IRIs and explicit module imports** if they intend a real AICOR-core→CRAM-extension dependency (requires a careful, reviewed upstream refactor; not performed here).

The `https://w3id.org/aicor/...` names are **provisional logical IRIs** and are not represented as publicly registered. The catalog maps them to local files. It intentionally does not give DUL a fake local implementation. If you obtain the official DUL OWL file, pin it in `external/DUL.owl`, add a local mapping for the official ontology IRI, then run the imported closure through Protégé/HermiT (or ROBOT with a suitable reasoner). An actual consistency check is a release gate, not a task satisfied by RDFLib.

## 7. Scope check

**Already delivered:** a general reusable core; pouring refactor; independent grasping architecture test; local catalog; complete vocabulary migration map; structural test harness and provenance docs.

**Not delivered:** curated abstract description individuals (ABox of **knowledge objects**), formally resolved DUL imported closure, full OWL DL reasoner audit, default/nonmonotonic semantics, robotic world model integration, execution planning, or GraphRAG indexing and evaluation.
