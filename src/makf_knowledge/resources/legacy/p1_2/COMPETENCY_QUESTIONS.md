# Competency questions for P1.2 — generic pouring stereotype

**Scope:** answers from ontology/schema alone, with no robot-world model. The expected answer is **what the frame asserts as structural knowledge**, never whether a specific execution will succeed.

| ID | Competency question | Frame path or assertion | Acceptance criterion |
|---|---|---|---|
| CQ-01 | Which dimensions of knowledge are associated with the pouring stereotype? | `PouringKnowledgeFrame` restrictions on `has*Perspective` | All 8 descriptive perspectives and cross-cutting applicability are discoverable |
| CQ-02 | What generic participant roles should a pouring description distinguish? | `PouringRolePerspective` → `dul:definesRole` → Source, Substance, Agent, Destination, Goal roles | Finds *role types*, never concrete physical fillers |
| CQ-03 | How is a pouring goal represented? | `hasIntentionalPerspective` → `aicor:PouringIntention` → `hasTelos` → `PouringTelos` | Connects generalized intention to terminal-state characterization |
| CQ-04 | Which causal event/state pattern is expected? | `hasCausalPerspective` → `PouringTemplate` → `hasFDEvent`, `hasFDState`, `hasTerminalState` | Retrieves efflux onset, flow, accumulation as template parts; does not assert actual events |
| CQ-05 | What generic phases and optional orderings are described? | `PouringScript`, `FlowControlledPouringScript`, `InitiationBeforeTerminationPattern` | Describes potential initiation-before-termination without inferring a universal total order |
| CQ-06 | Which alternative ways of pouring can be hypothesized? | `PouringStrategySpace` → `PouringStrategy` subclasses | Finds orientation mediated / feedback regulated / rapid orientation change as candidate strategy families |
| CQ-07 | Which conditions and predicted effects characterize a candidate hypothesis? | `PouringActingHypothesis` and example subclasses | Finds both applicability and predicted effect as *reified descriptions*, not established facts |
| CQ-08 | What could signal the initiation/termination of flow? | `PouringObservationPerspective` → `PouringObservationPattern` subclasses | Finds generic expected cues; no sensor/observation activity is asserted |
| CQ-09 | Which possible deviations should be considered? | `PouringDeviationPerspective` → `PouringDeviationPattern` subclasses | Finds no-flow / uncontrolled outflow / missed destination as possible patterns |
| CQ-10 | Is this model independent of an instantiated world and robot? | Declared schema graph, absence of individuals, no obligatory `aicor:ManipulationFrame` inheritance | No named robots, instances, scenes, actual measurements or episodes; hypotheses not automatically evidence-verified |
| CQ-11 | Can DUL understand the frame as a description and its roles as roles? | `owl:imports` and `dul-alignment.ttl` | Selective subclass mappings resolve to official DUL IRIs; no event/category equivalence asserted |

## Example manual walkthrough: CQ-07

Question: *Under what assumptions might rapid orientation change lead to undesirable outflow during pouring?*

Expected graph/schema steps:

1. Find subclass `paf:RapidTiltOutflowRiskHypothesis` under `paf:PouringStrategyHypothesis`.
2. Read its `paf:concernsStrategy some paf:RapidOrientationChangeStrategy` restriction.
3. Read `paf:hasApplicabilityCondition some paf:FlowSensitivityCondition`.
4. Read `paf:predictsPossibleEffect some paf:UncontrolledOutflowPredictionPattern`.
5. Report this as **hypothetical conditional knowledge**. The structural axiom does not prove occurrence probability, physical safety or applicability to a concrete container.

Notice that this requires no robot, no vessel-specific geometry and no world-state data.
