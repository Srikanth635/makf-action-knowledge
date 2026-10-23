# P1.2 — Multiperspective Stereotypical Pouring Action Frame

**Status:** draft ontology design v0.1.0, 23 October 2026. **No world model or execution instances.**

## 0. Deliverables

| File | Purpose |
|---|---|
| `pouring-frame.ttl` | OWL 2 TBox extending AICOR/CRAM terminology with a unified, generic pouring frame and conditional hypothesis categories |
| `dul-alignment.ttl` | Small, **directional** bridge from selected AICOR concepts to the real DUL ontology |
| `COMPETENCY_QUESTIONS.md` | Query requirements and acceptance criteria across perspectives |
| `query_frame.py` | Executable RDFLib exploration of the *declared* axioms, without claiming OWL inference |
| `validate_frame.py` | Reproducible structural checks against uploaded ontology source |

**Source of truth:** `/mnt/data/cram-aicor-ontology.ttl` is the **expanded working ontology**. The base `/mnt/data/aicor-ontology.ttl` is a comparative source, **not a second owl:imports target**, because both use `http://aicor.knowledge/l2-ontology.owl` as their ontology IRI. Neither source file is changed here.

## 1. Requirement and boundary

Define reusable **stereotypical, generalized and hypothetical knowledge** about pouring, prior to contextualization. The frame describes:

- its action-category identity;
- agent, source, destination, substance and telic roles;
- intended effect, physical causal template and generic state transitions;
- candidate scripts and phase-dependency descriptions;
- alternative generalized strategies;
- expected perceptual cues;
- conditional, not-yet-validated acting hypotheses;
- possible deviations and abstract applicability assumptions.

It does **not** describe any named robot, specific bottle, actual liquid quantity, concrete scene, action execution, observed event, NEEM record or measured force. No such individuals are created. The file is TBox-only (OWL classes and properties with restrictions; no `owl:NamedIndividual`).

**Caution:** OWL existential restrictions assert the existence of suitable (possibly anonymous) fillers *when a class has an instance*. Here those fillers are modeling **knowledge descriptions**, except where the imported CRAM ontology itself provides broader class semantics. No concrete task or execution individuals are declared. Do not interpret `aicor:Pouring` as `dul:Action`/`dul:Event` merely because of its English label: its source superclass chain ends in `aicor:GeneralizedActionPlan`.

## 2. Perspective model

```text
paf:PouringKnowledgeFrame ⊑ paf:ActionKnowledgeFrame ⊑ dul:Description
  ├─ hasActionCategory        ∃ aicor:Pouring
  ├─ hasRolePerspective       ∃ paf:PouringRolePerspective
  ├─ hasIntentionalPerspective∃ aicor:PouringIntention
  ├─ hasCausalPerspective     ∃ aicor:PouringTemplate
  ├─ hasTemporalPerspective   ∃ paf:PouringScript
  ├─ hasProceduralPerspective ∃ paf:PouringStrategySpace
  ├─ hasObservationalPerspective ∃ paf:PouringObservationPerspective
  ├─ hasHypothesisPerspective∃ paf:PouringHypothesisSpace
  ├─ hasDeviationPerspective ∃ paf:PouringDeviationPerspective
  └─ hasApplicabilityPerspective ∃ paf:PouringApplicabilityModel  [cross-cutting]
```

Eight perspectives plus cross-cutting applicability. Properties express **typed links between abstract descriptions**. The frame intentionally does *not* subclass `aicor:ManipulationFrame`: the latter entails a `ManipulationProblemClass`, which entails a `RWMSFamily`. Reusing that superclass here would make the ostensibly world-model-independent frame inherit a world-family dependency. The semantic relationship is documented with `rdfs:seeAlso` instead.

### Role perspective

`paf:PouringRolePerspective ⊑ dul:Description` defines roles using **official DUL's** `dul:definesRole`: existing `aicor:AgentRole`, `SourceRole`, `SubstanceRole`, `GoalRole`, plus new `paf:DestinationRole`. The existing `GoalRole` is not automatically a destination container. The new `DestinationRole` describes a functional *role*, **not** any physical object. Source filler assignment belongs to later contextualization.

### Intentional and causal perspectives

Reuse `aicor:PouringIntention`, `aicor:PouringTelos`, `aicor:PouringTemplate`, `aicor:EffluxOnsetEvent`, `aicor:FlowingState` and `aicor:AccumulatedState` **as already defined in CRAM–AICOR**. The module does not overwrite their axioms. The imported template itself currently has existential restrictions regarding efflux onset, flow state, accumulated terminal state, phase and intention. Those are descriptive structural constraints; they do **not** imply a physical pouring event happened.

### Temporal perspective

`paf:PouringScript ⊑ dul:Plan` requires generic initiation and termination *phase patterns*, but does not assert total order. `paf:FlowControlledPouringScript` optionally specializes it by admitting a `paf:InitiationBeforeTerminationPattern` description. This pattern has an *earlier phase-pattern* and a *later phase-pattern*; it is **not** `time:before` between actual time intervals. `paf:GraspPreparationPhasePattern` is modeled as an *optional* candidate; the generic script does not require it.

### Procedural perspective

`paf:PouringStrategySpace` represents abstract alternatives. `paf:PouringStrategy ⊑ aicor:GeneralizedActionPlan, dul:Plan` reuses the existing generalized plan taxonomy and preserves underspecification. Candidate subtypes include `OrientationMediatedPouringStrategy`, `FeedbackRegulatedPouringStrategy` and `RapidOrientationChangeStrategy`. These are possible *ways of acting*, not endorsed control policies.

**Note:** the existing `aicor:GeneralizedActionPlan` contains axioms involving future `Contextualization`, `MotionPlan` and `ActionDesignator`; those are abstract CRAM conceptual dependencies, not a commitment to any robot or scene. Should complete independence from even these conceptual dependencies be required, an alternative design would link a DUL-only strategy description to `aicor:GeneralizedActionPlan` by `rdfs:seeAlso` rather than subclassing. That is a conscious design trade-off to review.

### Predictive, epistemic and deviation perspectives

`paf:PouringActingHypothesis ⊑ aicor:Hypothesis` requires a generic applicability condition and predicted-effect **description**. More specific hypotheses can concern a strategy or causal template. They do not state that a causal event occurs. In particular, we **do not** make them subclass `aicor:ManipulationHypothesis`, because that class already entails an `EvidenceSet` whose constraints lead to evidence-bearing execution traces. A future alignment can be added for *tested* hypotheses.

Example **unverified classes**:

| Hypothesis class | Conditional aspect | Predicted pattern | Status |
|---|---|---|---|
| `OrientationInducedEffluxHypothesis` | `OutflowEnabledCondition` | `FlowOnsetPredictionPattern` | Hypothesis, not physical law |
| `RapidTiltOutflowRiskHypothesis` | `FlowSensitivityCondition`; `RapidOrientationChangeStrategy` | `UncontrolledOutflowPredictionPattern` | Hypothesis, not verified safety fact |

`PouringObservationPattern` and `PouringDeviationPattern` are **descriptions**; they are not `sosa:Observation`, actual fault episodes, `dul:Event` or execution traces.

## 3. DUL integration

`pouring-frame.ttl` explicitly imports the official ontology IRI:

`http://www.ontologydesignpatterns.org/ont/dul/DUL.owl`

It also imports `dul-alignment.ttl` via its logical ontology IRI. The bridge provides only directional `rdfs:subClassOf` axioms:

| Local AICOR IRI | DUL target | Type |
|---|---|---|
| `aicor:dul_Description` | `dul:Description` | subclass, **not equivalence** |
| `aicor:dul_Concept` | `dul:Concept` | subclass, **not equivalence** |
| `aicor:dul_InformationObject` | `dul:InformationObject` | subclass, **not equivalence** |
| `aicor:dul_Region` | `dul:Region` | subclass, **not equivalence** |
| `aicor:ManipulationFrame` | `dul:Description` | subclass |
| `aicor:RoleSlot` | `dul:Concept` | subclass |
| `aicor:ParticipantRole` | `dul:Role` | subclass |
| `aicor:ConstraintSet` | `dul:Description` | subclass |

This is a **selective first-pass alignment**, not a blanket mapping of all 14 local `dul_*` classes. `aicor:dul_Event`, `aicor:dul_Action`, `aicor:dul_Process` and other occurrence-oriented aliases remain unaligned until a DL semantic audit: notably `aicor:ForceDynamicEvent` is both `aicor:Representation` and `aicor:dul_Event`. Mapping all such classes straight to official event classes can create conceptual category errors and potentially unsatisfiable intersections.

Because `owl:imports` is a semantic directive, **RDFLib parsing does not automatically resolve imports**. In Protégé or a reasoning pipeline, configure an ontology catalog/local import map:

- `http://aicor.knowledge/l2-ontology.owl` → `cram-aicor-ontology.ttl` (and **not** both source files)
- `https://w3id.org/aicor/pouring-frame/dul-alignment` → `dul-alignment.ttl`
- `http://www.ontologydesignpatterns.org/ont/dul/DUL.owl` → a pinned official DUL distribution

The draft `https://w3id.org/aicor/pouring-frame*` IRIs are **provisional identifiers and not claimed to be registered/resolvable**; replace/register them prior to publication. Do not rely on live fetch of these draft import IRIs.

DUL reference: https://www.ontologydesignpatterns.org/ont/dul/DUL.owl . This project intentionally does **not** import SOMA.

## 4. Reasoning and queries: what is entailed and what is not

**Available from declared structure:** class hierarchy; typed role perspectives; required *abstract* perspective links; possible phase patterns, strategies and hypothetical predictions, as schema knowledge. A semantic retriever can inspect OWL restrictions to answer the competency questions.

**Not established:** truth of a hypothesized physical effect; causal necessity; likelihood; safety; total temporal order; satisfaction of a condition in a scene; actual robot capabilities; existence of a named physical event.

Do not encode a physical hypothesis as `paf:RapidTiltStrategy rdfs:subClassOf [ owl:onProperty paf:causes ; owl:someValuesFrom :Spillage ]`, because OWL could then be read as asserting a general causal necessity. Here `predictsPossibleEffect` is located **on an explicit hypothesis description**. Do not confuse open-world OWL restrictions with SHACL data-quality constraints or closed-world validity.

## 5. Source integrity, validation and next decisions

Validation provided by `validate_frame.py` checks parseability, use of real source classes, property/restriction shape, no named world individuals, expected imports, controlled bridging, and separation of occurrence types. This is **not** a replacement for an OWL 2 DL reasoner. A final Protégé/HermiT or ROBOT/ELK review with the *actual* official DUL OWL document and the complete CRAM ontology is required before promoting this module to a stable ontology release.

Deliberate open questions:

1. Whether strategies should inherit all of `aicor:GeneralizedActionPlan`'s existing restrictions or instead use looser `dul:Plan` plus an explicit conceptual mapping.
2. Whether some currently named `aicor:ForceDynamicEvent` categories should be refactored into **event-type descriptions**, since their present `Representation ∩ dul_Event` conceptualization blurs levels.
3. Whether and how to formally distinguish **typical**, **possible**, **necessary**, and **exceptional** patterns (OWL alone does not provide defeasible/default reasoning).
4. How a future curated **schema-level knowledge graph of frame descriptions** should represent competing hypotheses while remaining independent of real-world individuals.
5. Whether additional AICOR local DUL aliases can be safely aligned after full DL satisfiability checking.

**Next step:** P1.3 could populate *generic action-description individuals* (not world events) in an ontology knowledge-graph layer for GraphRAG, or further refine this TBox with validation shapes and modal qualifiers. This P1.2 package does **not** create those individuals.
