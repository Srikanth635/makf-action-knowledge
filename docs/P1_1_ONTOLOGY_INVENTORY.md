# Pouring stereotypical-action ontology inventory
**Version:** 1.0 (source-file analysis, 23 October 2026)  
**Scope:** AICOR + CRAM–AICOR, with *proposed* foundation mappings to DUL, PROV-O, OWL-Time, SOSA/SSN, and QUDT. **SOMA intentionally excluded.**  
**Status:** descriptive inventory and design analysis, **not** a new OWL module and **not** a consistency proof.

## 1. Source identity and methodology

| Input | Named OWL classes | Object properties | Datatype properties | RDF triples | Ontology IRI |
|---|---:|---:|---:|---:|---|
| `aicor-ontology.ttl` | 709 | 578 | 84 | 7,940 | `http://aicor.knowledge/l2-ontology.owl` |
| `cram-aicor-ontology.ttl` | 1017 | 811 | 155 | 11,596 | `http://aicor.knowledge/l2-ontology.owl` |

- CRAM–AICOR adds **308 named classes** and **304 named properties** beyond AICOR, using the same namespace and ontology IRI. These are structural differences in the uploaded files, not proof of a clean import/module hierarchy.
- **17 shared named classes** have changed directly asserted class axioms in CRAM–AICOR; see `shared_class_axiom_changes.csv`.
- **Zero `owl:imports` declarations** in both source files. Alignment to external foundational ontologies does not yet exist as an explicit ontology import.
- Both include **local classes named `dul_Description`, `dul_Event`, etc. in the AICOR namespace**. They are NOT the official `dul:Description` or `dul:Event` IRIs. Do not treat them as formally imported DUL concepts without explicit, audited alignments.
- SHA-256 for each source file is recorded in `inventory_stats.json` for reproducibility.
- Method: RDFLib Turtle parsing; count *named* OWL class declarations; for each class, extract direct `rdfs:subClassOf`, `owl:Restriction`, `owl:equivalentClass`, `owl:disjointWith`. Direct-only: no OWL DL materialization or external imports.
- The eight perspectives below are **analyst tags for navigation**, not classes asserted as such in either ontology. Terms can appear under multiple perspectives.

## 2. Summary of the actual pouring core

CRAM–AICOR defines (direct axioms summarized faithfully):
```text
Pouring ⊑ Transferring
Pouring ⊑ ∃hasSubaction.Grasping
Pouring ⊑ ∃hasSubaction.Tilting
Pouring ⊑ ∃hasIntentionalStructure.PouringIntention
Pouring ⊑ ∃hasCausalStructure.PouringTemplate

PouringIntention ⊑ IntentionalStructure
PouringIntention ⊑ ∃hasParticipantRole.AgentRole
PouringIntention ⊑ ∃hasParticipantRole.SourceRole
PouringIntention ⊑ ∃hasParticipantRole.SubstanceRole
PouringIntention ⊑ ∃hasParticipantRole.GoalRole
PouringIntention ⊑ ∃hasTelos.PouringTelos
PouringTelos ⊑ ∃definedOverState.AccumulatedState

PouringTemplate ⊑ ForceDynamicTemplate
PouringTemplate ⊑ ∃hasFDEvent.EffluxOnsetEvent
PouringTemplate ⊑ ∃hasFDState.FlowingState
PouringTemplate ⊑ ∃hasTerminalState.AccumulatedState
PouringTemplate ⊑ ∃realizesIntention.PouringIntention
PouringTemplate ⊑ ∃hasPhase.PouringPhase
PouringPhase ⊑ MotionPhase
PouringPhase ⊑ ∃hasPhaseGoal.EffluxOnsetEvent
```
**Note:** the four role axioms are separate existential restrictions. They do not assert exactly four distinct role fillers, do not guarantee a destination container, and impose no temporal order.

The nominal `Pouring` class is a **subclass of `Transferring` → `SubstanceManipulation` → `ManipulationActionCategory` → `GeneralizedActionPlan`**. Therefore, in this model it sits in a plan/category taxonomy, not unambiguously in an execution-event taxonomy. Distinguish `Pouring` as action type/plan from any future `PouringExecution` / action occurrence before alignment to DUL or PROV-O.

Base AICOR has `ActionRelatedPour`, but **no declaration linking it to the CRAM–AICOR `Pouring` class**. Add a mapping only after semantic review.

## 3. Inventory by perspective (existing classes only)

Every `aicor:` entry below is a named class declared in the uploaded files. **Origin**: AICOR = present in base file, CRAM+ = added in CRAM–AICOR. Restriction text is a selected **direct** axiom, not an inferred fact.

### 01 Action taxonomy and roles

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:ActionRelatedPour` | AICOR | — |  |
| `aicor:Pouring` | CRAM+ | aicor:Transferring | aicor:hasCausalStructure some aicor:PouringTemplate; aicor:hasIntentionalStructure some aicor:PouringIntention; aicor:hasSubaction some aicor:Grasping; … |
| `aicor:Transferring` | CRAM+ | aicor:SubstanceManipulation |  |
| `aicor:SubstanceManipulation` | CRAM+ | aicor:ManipulationActionCategory | aicor:effectDimension hasValue substance |
| `aicor:ManipulationActionCategory` | CRAM+ | aicor:GeneralizedActionPlan | aicor:hasCausalStructure some aicor:ForceDynamicTemplate; aicor:hasIntentionalStructure some aicor:IntentionalStructure |
| `aicor:PrimitiveAction` | CRAM+ | aicor:ManipulationActionCategory |  |
| `aicor:Grasping` | CRAM+ | aicor:PrimitiveAction |  |
| `aicor:Tilting` | CRAM+ | aicor:PrimitiveAction |  |
| `aicor:Lifting` | CRAM+ | aicor:PrimitiveAction |  |
| `aicor:Container` | CRAM+ | aicor:PhysicalIndividual | aicor:contains some aicor:Substance |
| `aicor:Vessel` | CRAM+ | aicor:Representation |  |
| `aicor:PhysicalIndividual` | CRAM+ | aicor:MaterialEntity | aicor:matterKind hasValue individual |
| `aicor:Substance` | CRAM+ | aicor:MaterialEntity | aicor:matterKind hasValue substance |
| `aicor:MaterialEntity` | CRAM+ | aicor:dul_PhysicalObject |  |
| `aicor:ParticipantRole` | CRAM+ | — |  |
| `aicor:SourceRole` | CRAM+ | aicor:ParticipantRole |  |
| `aicor:SubstanceRole` | CRAM+ | aicor:ParticipantRole |  |
| `aicor:AgentRole` | CRAM+ | aicor:ParticipantRole |  |
| `aicor:GoalRole` | CRAM+ | aicor:ParticipantRole |  |
| `aicor:InstrumentRole` | CRAM+ | aicor:ParticipantRole |  |
| `aicor:RoleSlot` | AICOR | aicor:dul_Concept | aicor:physicallyTypedBy some aicor:MaterialProperty |
| `aicor:RoleBinding` | AICOR | aicor:dul_Description | aicor:bindsFiller some aicor:dul_PhysicalObject; aicor:bindsSlot some aicor:RoleSlot |
| `aicor:RoleAssignmentLayer` | AICOR | — |  |
| `aicor:ManipulationFrame` | AICOR | aicor:dul_Description | aicor:frameOf some aicor:ManipulationProblemClass; aicor:hasFrameElement some aicor:RoleSlot |
| `aicor:ManipulationProblemClass` | AICOR | aicor:AbstractEntity, aicor:MetaLevelEntity, aicor:dul_Description | aicor:constrainsRung some aicor:SubstrateRung; aicor:generates some aicor:ProblemDomain; aicor:hasCriticSet some aicor:Critic; … |


### 02 Intentional / goal

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:IntentionalStructure` | CRAM+ | aicor:Representation | aicor:hasParticipantRole some aicor:ParticipantRole; aicor:hasTelos some aicor:Telos |
| `aicor:PouringIntention` | CRAM+ | aicor:IntentionalStructure | aicor:hasParticipantRole some aicor:AgentRole; aicor:hasParticipantRole some aicor:GoalRole; aicor:hasParticipantRole some aicor:SourceRole; … |
| `aicor:PouringTelos` | CRAM+ | aicor:Telos | aicor:definedOverState some aicor:AccumulatedState |
| `aicor:Telos` | CRAM+ | aicor:Representation | aicor:definedOverState some aicor:ForceDynamicState |
| `aicor:Goal` | AICOR | aicor:dul_Description | aicor:goalScope some aicor:Phase |
| `aicor:AchievementGoal` | AICOR | aicor:Goal | aicor:hasConditionType some aicor:EventType |
| `aicor:MaintenanceGoal` | AICOR | aicor:Goal | aicor:hasConditionType some aicor:FluentType |
| `aicor:PreventionGoal` | AICOR | aicor:Goal | aicor:hasConditionType some aicor:FluentType |
| `aicor:GoalClause` | CRAM+ | aicor:dul_Description | aicor:checkedAgainst some aicor:WorldStateRepresentation |
| `aicor:Task` | AICOR | aicor:Representation, aicor:dul_Description | aicor:hasStatus some aicor:Fluent |
| `aicor:TaskReading` | AICOR | aicor:dul_Description |  |
| `aicor:TaskRequest` | AICOR | aicor:dul_InformationObject |  |
| `aicor:Intention` | CRAM+ | aicor:Representation, aicor:dul_Description |  |


### 03 Causal / force-dynamic

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:ForceDynamicTemplate` | CRAM+ | aicor:MotionPlan, aicor:ProbabilisticHybridActionModel | aicor:atlasOf some aicor:ActionManifold; aicor:hasFDEvent some aicor:ForceDynamicEvent; aicor:hasFDState some aicor:ForceDynamicState; … |
| `aicor:PouringTemplate` | CRAM+ | aicor:ForceDynamicTemplate | aicor:hasFDEvent some aicor:EffluxOnsetEvent; aicor:hasFDState some aicor:FlowingState; aicor:hasPhase some aicor:PouringPhase; … |
| `aicor:ForceDynamicSchema` | AICOR | aicor:AbstractEntity, aicor:dul_Description | aicor:appliesTo some aicor:ManipulationEpisode; aicor:definesConditionOn some aicor:ForceDynamicEvent; aicor:hasRoleSlot some aicor:RoleSlot; … |
| `aicor:ForceDynamicDependency` | AICOR | aicor:dul_Description | aicor:posteriorSchema some aicor:ForceDynamicSchema; aicor:priorSchema some aicor:ForceDynamicSchema; aicor:satisfiedByEvent some aicor:ForceDynamicEvent |
| `aicor:ForceDynamicEvent` | AICOR | aicor:Representation, aicor:dul_Event | aicor:betweenRoleFillers some aicor:RoleSlot; aicor:hasForceProfile some aicor:ForceProfile; aicor:involvesContact some aicor:PhysicalContact; … |
| `aicor:ForceDynamicEventType` | AICOR | aicor:EventType |  |
| `aicor:EffluxOnsetEvent` | CRAM+ | aicor:ForceDynamicEvent |  |
| `aicor:ForceDynamicState` | CRAM+ | aicor:DiscreteMode |  |
| `aicor:ContainedState` | CRAM+ | aicor:ForceDynamicState |  |
| `aicor:FlowingState` | CRAM+ | aicor:ForceDynamicState |  |
| `aicor:AccumulatedState` | CRAM+ | aicor:ForceDynamicState |  |
| `aicor:GraspedState` | CRAM+ | aicor:ForceDynamicState |  |
| `aicor:PhysicalContact` | AICOR | — |  |
| `aicor:ForceProfile` | AICOR | — |  |
| `aicor:ForceCorridor` | AICOR | aicor:dul_Region | aicor:corridorOf some aicor:BodyWorldSystem; aicor:lowerEdge some aicor:SlipEventType; aicor:upperEdge some aicor:RuptureEventType |
| `aicor:SlipEventType` | AICOR | aicor:ForceDynamicEventType | aicor:crossingIs some aicor:Recoverable |
| `aicor:RuptureEventType` | AICOR | aicor:ForceDynamicEventType | aicor:crossingIs some aicor:Irreversible |
| `aicor:PhysicalProcess` | CRAM+ | aicor:dul_Process |  |
| `aicor:BodyDynamics` | AICOR | — |  |
| `aicor:BodyWorldSystem` | AICOR | aicor:CaseLevelEntity, aicor:PhysicalEntity, aicor:dul_PhysicalObject | aicor:boundaryTaskRelative hasValue true; aicor:hasCoupling some aicor:ForceInteraction; aicor:hasDeclaredBoundary some aicor:DeclaredBoundary; … |
| `aicor:HybridBodyWorldState` | AICOR | aicor:dul_Quality | aicor:evolvesBy some aicor:ModeIndexedDynamics; aicor:hasContinuousState exact 1 aicor:ContinuousState; aicor:hasDiscreteMode exact 1 aicor:DiscreteModeStructure |
| `aicor:ForceClosure` | AICOR | aicor:CouplingType | aicor:characteristicFailure some _:anonymous; aicor:governedBy hasValue frictionCone |


### 04 Temporal / process script

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:MotionPhase` | CRAM+ | aicor:Representation, aicor:dul_Description | aicor:hasGoal some aicor:ForceDynamicEvent; aicor:hasPhaseGoal some aicor:ForceDynamicEvent |
| `aicor:PouringPhase` | CRAM+ | aicor:MotionPhase | aicor:hasPhaseGoal some aicor:EffluxOnsetEvent |
| `aicor:Phase` | AICOR | aicor:AbstractEntity |  |
| `aicor:ManipulationPhase` | CRAM+ | aicor:Representation, aicor:dul_Description |  |
| `aicor:EventType` | AICOR | aicor:AbstractEntity, aicor:ReifiedTemporalEntity, aicor:dul_Description | aicor:homogeneous hasValue false; aicor:occursOver some aicor:TimeInterval |
| `aicor:StateTransitionLink` | AICOR | aicor:RealizationLink | aicor:producesEffect some aicor:TaskRelativeEffect |
| `aicor:DiscreteMode` | CRAM+ | aicor:Representation, aicor:dul_Description |  |
| `aicor:MotionStatechart` | CRAM+ | aicor:ConstraintBasedControl, aicor:Representation | aicor:composedOf some aicor:MotionTask; aicor:controlledBy some aicor:ModelPredictiveControl; aicor:executes some aicor:MotionPlan; … |
| `aicor:LifecycleEvent` | AICOR | — |  |
| `aicor:MotionPlan` | CRAM+ | aicor:ControlProgram, aicor:Program, aicor:Representation | aicor:hasMotionPhase some aicor:ForceDynamicEvent; aicor:hasPart some aicor:MotionPhase; aicor:parameterizedBy some aicor:MotionDesignator; … |
| `aicor:TaskNetwork` | CRAM+ | aicor:Representation, aicor:dul_Description | aicor:hasTask some aicor:Task; aicor:hasTopTask some aicor:Task |
| `aicor:ControlSequence` | AICOR | — |  |
| `aicor:ContinuousFlow` | CRAM+ | aicor:Representation, aicor:dul_Description |  |


### 05 Procedural / action policy

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:GeneralizedActionPlan` | CRAM+ | aicor:ManipulationControlProgram, aicor:Program, aicor:Representation | aicor:contextualizedBy some aicor:Contextualization; aicor:embeds some aicor:ActionDesignator; aicor:expandsInto some aicor:MotionPlan; … |
| `aicor:StructuredReactivePlan` | CRAM+ | aicor:Plan, aicor:Representation, aicor:dul_Description | aicor:executesInto some aicor:TaskNetwork; aicor:hasCodeTree exact 1 aicor:CodeTree; aicor:interpretedBy some aicor:PlanInterpreter; … |
| `aicor:Plan` | CRAM+ | aicor:ControlProgram, aicor:Program | aicor:canBeReasonedAbout hasValue true; aicor:isManipulableAtRuntime hasValue true; aicor:manipulatedAtRuntimeBy some aicor:PlanTransformation; … |
| `aicor:PlanInterpreter` | CRAM+ | aicor:ComputationalProcess, aicor:dul_Description |  |
| `aicor:PlanExecutive` | CRAM+ | aicor:ComputationalProcess, aicor:ExecutiveComponent, aicor:dul_Description | aicor:achieves some aicor:Transferability; aicor:executesPlan some aicor:GeneralizedActionPlan |
| `aicor:Contextualization` | CRAM+ | aicor:ComputationalProcess, aicor:ProposalToCommitmentPipeline | aicor:hasStep some aicor:ContextualizationStep; aicor:instantiates some aicor:GeneralizedActionPlan; aicor:produces some aicor:MotionPlan; … |
| `aicor:ContextualizationStep` | CRAM+ | aicor:ComputationalProcess, aicor:dul_Description |  |
| `aicor:ActionDesignator` | AICOR | aicor:AttributiveDesignator, aicor:CRAMDesignator, aicor:Representation | aicor:hasPart some aicor:DesignatorConstraintSet; aicor:references some aicor:ActionEventType; aicor:resolvesTo some aicor:EntityDesignator; … |
| `aicor:CRAMDesignator` | CRAM+ | aicor:Designator, aicor:Representation | aicor:boundTo max 1 aicor:DesignatorReferent; aicor:hasPart some aicor:DesignatorConstraintSet; aicor:hasResolution some aicor:DesignatorResolution; … |
| `aicor:MotionDesignator` | CRAM+ | aicor:CRAMDesignator, aicor:Representation | aicor:resolvesTo some aicor:BodyMotion |
| `aicor:DesignatorConstraintSet` | CRAM+ | aicor:Representation, aicor:dul_Description | aicor:hasPart some aicor:DesignatorParameter |
| `aicor:DesignatorParameter` | CRAM+ | aicor:Representation, aicor:dul_Description |  |
| `aicor:ForceDynamicTemplate` | CRAM+ | aicor:MotionPlan, aicor:ProbabilisticHybridActionModel | aicor:atlasOf some aicor:ActionManifold; aicor:hasFDEvent some aicor:ForceDynamicEvent; aicor:hasFDState some aicor:ForceDynamicState; … |
| `aicor:Affordance` | CRAM+ | aicor:ActionRelatedConcept, aicor:Representation | aicor:affordsAction some aicor:ActionEventType; aicor:conditionedOn some aicor:BeliefState; aicor:isContextConditioned hasValue true; … |
| `aicor:ConstraintSet` | AICOR | aicor:dul_Description |  |
| `aicor:BodyWorldConstraint` | AICOR | aicor:AbstractEntity, aicor:dul_Description | aicor:constrains some aicor:BodyWorldSystem; aicor:unlocks some aicor:Theorem |
| `aicor:StabilityCondition` | CRAM+ | aicor:Representation | aicor:preferredConfiguration some aicor:BodyWorldConfiguration |
| `aicor:MotionPlan` | CRAM+ | aicor:ControlProgram, aicor:Program, aicor:Representation | aicor:hasMotionPhase some aicor:ForceDynamicEvent; aicor:hasPart some aicor:MotionPhase; aicor:parameterizedBy some aicor:MotionDesignator; … |
| `aicor:ProcessMonitor` | AICOR | aicor:AbstractEntity, aicor:dul_Description | aicor:checks some _:anonymous; aicor:monitorFor some aicor:BodyWorldProcessMicrotheory; aicor:operationalizes some aicor:Expectation; … |


### 06 Predictive / perceptual

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:ExpectedObservation` | AICOR | aicor:dul_InformationObject | aicor:generatedBy some aicor:DigitalBodyWorldSystem |
| `aicor:Expectation` | AICOR | — |  |
| `aicor:ProcessMonitoringExpectation` | AICOR | aicor:ExpectedObservation | aicor:monitorsPhaseOf some aicor:ForceDynamicSchema |
| `aicor:BindingConfirmationExpectation` | AICOR | aicor:ExpectedObservation | aicor:confirmsBindingIn some aicor:RoleAssignmentLayer |
| `aicor:Observation` | AICOR | aicor:AbstractEntity, aicor:dul_InformationObject |  |
| `aicor:ObservationEvent` | CRAM+ | aicor:EventType |  |
| `aicor:ObservationModel` | CRAM+ | aicor:dul_Description | aicor:conditionedOnState some aicor:HybridBodyWorldState; aicor:producesObservation some aicor:Observation |
| `aicor:ObservationChannelModel` | AICOR | aicor:dul_Description |  |
| `aicor:Percept` | AICOR | — |  |
| `aicor:Perception` | AICOR | — |  |
| `aicor:ProcessMonitor` | AICOR | aicor:AbstractEntity, aicor:dul_Description | aicor:checks some _:anonymous; aicor:monitorFor some aicor:BodyWorldProcessMicrotheory; aicor:operationalizes some aicor:Expectation; … |
| `aicor:ObservationToPerceptService` | AICOR | — |  |
| `aicor:ExecutablePrediction` | AICOR | aicor:dul_InformationObject | aicor:answersQuery some aicor:WhatIfQuery; aicor:appliesToCoupling some aicor:CouplingType; aicor:isModelQuantity hasValue true; … |
| `aicor:CausalPrediction` | AICOR | aicor:CognitiveCapability | aicor:hasPrecondition some aicor:Grounding |
| `aicor:OutcomePrediction` | CRAM+ | aicor:Prospection | aicor:produces some aicor:BayesianRisk |
| `aicor:Prediction` | AICOR | — |  |
| `aicor:ProspectiveBelief` | CRAM+ | aicor:dul_InformationObject | aicor:aboutFutureExecutionOf some aicor:ActionDesignator; aicor:computedBy some aicor:Projection |
| `aicor:BeliefState` | AICOR | aicor:Representation | aicor:hasAmbiguity hasValue true; aicor:hasInaccuracy hasValue true; aicor:hasPart some aicor:StateEstimate; … |


### 07 Epistemic / justification

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:Hypothesis` | AICOR | aicor:AbstractEntity, aicor:EpistemicObject |  |
| `aicor:ManipulationHypothesis` | AICOR | aicor:Hypothesis, aicor:MetaLevelEntity | aicor:evaluatedBy some aicor:EvidenceSet; aicor:rangesOverFamily some aicor:RWMSFamily |
| `aicor:CompetenceHypothesis` | AICOR | aicor:ManipulationHypothesis | aicor:predictsCompetence some aicor:CompetenceClaim |
| `aicor:MonotonicityHypothesis` | AICOR | aicor:CompetenceHypothesis | aicor:assessedOver some aicor:ProblemDomain; aicor:predictsDegreeTrend some aicor:CompetenceDegree |
| `aicor:TransferHypothesis` | AICOR | aicor:CompetenceHypothesis | aicor:predictsTransferTo some aicor:TaskEnvironmentEmbodimentClass |
| `aicor:EvidenceSet` | AICOR | aicor:MetaLevelEntity | aicor:evidenceDerivedFrom some aicor:EvidenceBearingTrace |
| `aicor:EvidenceBearingTrace` | AICOR | aicor:CaseLevelEntity, aicor:dul_InformationObject | aicor:interprets some aicor:Recording; aicor:isCriticRelative hasValue true; aicor:isRawLog hasValue false; … |
| `aicor:EvidenceRequirement` | AICOR | — |  |
| `aicor:EvidentialSufficiency` | AICOR | — |  |
| `aicor:CompetenceQuestion` | AICOR | aicor:dul_Description | aicor:answeredBy some aicor:CognitiveCapability; aicor:raisedBy some aicor:ManipulationProblemClass |
| `aicor:CompetenceClaim` | AICOR | aicor:MetaLevelEntity, aicor:ScopedClaim, aicor:dul_Description | aicor:assertsStandard some aicor:GlobalStandard; aicor:atDegree some aicor:CompetenceDegree; aicor:claimScope hasValue competence; … |
| `aicor:FeasibilityAssessment` | AICOR | — |  |
| `aicor:SafetyAssessment` | AICOR | — |  |
| `aicor:ScopeCondition` | AICOR | aicor:dul_Description |  |
| `aicor:CausalAdmissibility` | AICOR | aicor:AbstractEntity, aicor:dul_Description |  |


### 08 Failures / variation / memory

| Existing class | Origin | Direct superclass(es), excluding `owl:Thing` | Direct restriction(s) (selected) |
|---|---|---|---|
| `aicor:FailureReason` | AICOR | — |  |
| `aicor:FailureDescription` | CRAM+ | aicor:dul_Description | aicor:hasFailedTask max 1 aicor:Task; aicor:hasFailureId max 1 aicor:FailureId; aicor:hasSeverity max 1 aicor:FailureSeverity |
| `aicor:PreventionViolation` | AICOR | aicor:FailureReason |  |
| `aicor:PhysicalDeviation` | AICOR | — |  |
| `aicor:FailureSignature` | AICOR | aicor:AbstractEntity, aicor:dul_Description | aicor:bridges some _:anonymous; aicor:detectedBy some aicor:ProcessMonitor; aicor:enumeratedBy some aicor:BodyWorldProcessMicrotheory; … |
| `aicor:SafetyCritic` | CRAM+ | aicor:Critic | aicor:criticDimension hasValue safety |
| `aicor:Critic` | AICOR | aicor:ComputationalProcess | aicor:yieldsVerdict some aicor:Verdict |
| `aicor:Transferability` | CRAM+ | aicor:dul_Description | aicor:achievedBy some aicor:Contextualization; aicor:assertedBy some aicor:CompetenceClaim; aicor:requiresLimitedReprogramming hasValue true; … |
| `aicor:NEEM` | CRAM+ | aicor:Narrative, aicor:Representation, aicor:dul_InformationObject | aicor:derivedFrom some aicor:EvidenceBearingTrace; aicor:derivedFrom some aicor:Recording; aicor:drives some aicor:LearningLoop; … |
| `aicor:Recording` | AICOR | aicor:dul_InformationObject | aicor:isAbout some aicor:ManipulationEpisode; aicor:isPartial hasValue true |
| `aicor:ManipulationEpisode` | AICOR | aicor:AbstractEntity, aicor:CaseLevelEntity, aicor:dul_Situation | aicor:conformsToScope max 1 aicor:TaskEnvironmentEmbodimentClass; aicor:hasCommitmentRecord exact 1 aicor:CommitmentRecord; aicor:hasLifecycleEvents some aicor:LifecycleEvent; … |
| `aicor:ActualCourse` | CRAM+ | aicor:Representation, aicor:dul_Description |  |
| `aicor:LearningLoop` | CRAM+ | aicor:ComputationalProcess, aicor:dul_Description | aicor:drives some aicor:GenerativeModel; aicor:hasPart some aicor:ModelLearning; aicor:hasPart some aicor:PlanLearning; … |
| `aicor:PlanLearning` | CRAM+ | aicor:ComputationalProcess, aicor:dul_Description |  |
| `aicor:OpenContainerState` | AICOR | aicor:ContainerClosureState |  |
| `aicor:ClosedContainerState` | AICOR | aicor:ContainerClosureState |  |


## 4. Property inventory for the focused classes

The file `focused_properties.csv` gives every property referenced by a direct OWL restriction on the selected classes, including declared type and any explicit RDFS domain/range. The table here highlights relations that implement the principal perspective links.
| Relation (AICOR namespace) | Base? | Focused class restrictions using it | Explicit domain/range? |
|---|---|---|---|
| `hasSubaction` | CRAM+ | Pouring | no |
| `hasIntentionalStructure` | CRAM+ | ManipulationActionCategory, Pouring | no |
| `hasCausalStructure` | CRAM+ | ManipulationActionCategory, Pouring | no |
| `hasParticipantRole` | CRAM+ | IntentionalStructure, PouringIntention | no |
| `hasTelos` | CRAM+ | IntentionalStructure, PouringIntention | no |
| `definedOverState` | CRAM+ | PouringTelos, Telos | no |
| `hasFDEvent` | CRAM+ | ForceDynamicTemplate, PouringTemplate | no |
| `hasFDState` | CRAM+ | ForceDynamicTemplate, PouringTemplate | no |
| `hasTerminalState` | CRAM+ | PouringTemplate | no |
| `realizesIntention` | CRAM+ | ForceDynamicTemplate, PouringTemplate | no |
| `hasPhase` | CRAM+ | PouringTemplate | no |
| `hasPhaseGoal` | CRAM+ | MotionPhase, PouringPhase | no |
| `frameOf` | yes | ManipulationFrame | no |
| `hasFrameElement` | yes | ManipulationFrame | no |
| `bindsSlot` | yes | RoleBinding | no |
| `bindsFiller` | yes | RoleBinding | no |
| `hasRoleSlot` | yes | ForceDynamicSchema | no |
| `contextualizedBy` | CRAM+ | GeneralizedActionPlan | no |
| `instantiates` | yes | Contextualization | no |
| `expandsInto` | CRAM+ | GeneralizedActionPlan | no |
| `embeds` | CRAM+ | GeneralizedActionPlan | no |
| `hasPart` | yes | ActionDesignator, BeliefState, CRAMDesignator, DesignatorConstraintSet, GeneralizedActionPlan, LearningLoop, MotionPlan | no |
| `hasExpectedObservation` | yes | — | no |
| `monitorsPhaseOf` | yes | ProcessMonitoringExpectation | no |
| `hasPrecondition` | yes | CausalPrediction | no |
| `conditionedOn` | yes | Affordance | no |
| `predictsSuccess` | CRAM+ | — | no |
| `evidenceDerivedFrom` | yes | EvidenceSet | no |
| `evaluatedBy` | yes | ManipulationHypothesis | no |
| `evidenceBaseFor` | yes | — | no |
| `confirmsHypothesis` | yes | — | no |
| `refutesHypothesis` | yes | — | no |
| `testsHypothesis` | yes | — | no |
| `rangesOverFamily` | yes | ManipulationHypothesis | no |
| `hasTrace` | yes | ManipulationEpisode | no |
| `hasCriticSet` | yes | ManipulationProblemClass | no |

## 5. Proposed foundational alignment (NOT asserted in uploads)

Mappings are concept candidates and modeling patterns, **not** `owl:equivalentClass` axioms or verified subsumptions. Proposed external vocabularies are distinct from locally declared `aicor:dul_*` placeholders. SOMA is intentionally out of scope.
| Perspective / purpose | Internal AICOR or CRAM–AICOR elements | Foundation vocabulary | Proposed pattern / caution |
|---|---|---|---|
| Action stereotype / frames | `ManipulationFrame`, `RoleSlot`, `Pouring` | DUL (`dul:Description`, `dul:Concept`, `dul:Role`, `dul:Plan`, `dul:Task`) | Use Description–Situation (DnS): a description defines task/participant roles; do not equate plan description to observed execution. |
| Situations and actual enactments | `ManipulationEpisode`, `ForceDynamicEvent`, `ActualCourse` | DUL (`dul:Situation`, `dul:Event`, `dul:Action`) | Design a separate class for a contextual pouring episode; align only after review of event vs description semantics. |
| Goal and intentional structure | `PouringIntention`, `PouringTelos`, `GoalRole` | DUL (`dul:Plan`, `dul:Goal`, `dul:Role`) | Goal/plan pattern; represent purpose and expected effects as descriptions rather than guaranteed occurrences. |
| Generalized plan, steps | `GeneralizedActionPlan`, `ActionDesignator`, `MotionPhase` | DUL Plan/Task; optional P-Plan (if verified) | Represent schematic alternatives and conditional transitions; an existential subaction restriction is NOT sequence. |
| Phase ordering and overlap | `PouringPhase`, `EffluxOnsetEvent`, `FlowingState` | OWL-Time (`time:Interval`, `time:Instant`, `time:before`, `time:intervalOverlaps`) | Use temporal relation objects for stereotypical ordering; avoid timestamps in action-type ontology. |
| Evidence and epistemic status | `Hypothesis`, `EvidenceSet`, `EvidenceBearingTrace` | PROV-O (`prov:Entity`, `prov:wasDerivedFrom`, `prov:wasAttributedTo`) | Treat hypotheses and source evidence as identifiable information entities; provenance does not itself express truth. |
| Actual versus expected observations | `ExpectedObservation`, `Observation`, `ProcessMonitor` | SOSA/SSN (`sosa:Observation`, `sosa:ObservableProperty`, `sosa:FeatureOfInterest`) | Separate *expectation description* from *actual observation act*; bridge only when episodes are later recorded. |
| Physical quality kinds (non-situated) | `ForceProfile`, `Geometry`, `MaterialProperty`, `ForceCorridor` | DUL (`dul:Quality`, `dul:Region`); QUDT (`qudt:QuantityKind`, `qudt:QuantityValue`) | Define kinds of parameters and valid ranges conceptually; actual measurements and units are world/episode data. |
| General-to-episode evidence | `GeneralizedActionPlan`, `NEEM`, `Recording` | PROV-O (`prov:Activity`, `prov:used`, `prov:wasGeneratedBy`) | Keep plan artifacts and event/record traces separate; derive stereotypes by analysis, not by asserting universal success. |

## 6. Coverage and gaps for generalized pouring knowledge

| Perspective | Already explicit | Not yet encoded sufficiently / needs inspection | Initial priority |
|---|---|---|---|
| Action identity / frame | `Pouring` + role restrictions + `ManipulationFrame` | No direct `Pouring`↔`ManipulationFrame` axiom; destination role is only a generic `GoalRole`; `ActionRelatedPour` remains unlinked. | High |
| Intentional | `PouringIntention` / `PouringTelos` / `AccumulatedState` | Goal variants (precise dosing, maximal flow, no-spill, etc.) and conflicting purposes not explicitly tied to Pouring. | Medium |
| Causal | Efflux, flow, accumulation in `PouringTemplate` | Causal triggers, intervening physical assumptions, counterfactual alternatives and explanation links remain sparse. | High |
| Temporal | Phase and phase-goal concepts | No formal ordering from grasp to tilt to efflux; no onset/continuation/termination script graph. | High |
| Procedural | Underdetermined generalized plans and designators | No concrete pouring plan variant or branch-conditioned procedural structure asserted at class/individual level. | High |
| Perceptual | `ExpectedObservation`, monitors, observation models | No mapping from pouring phase to discriminating expected observations or observable event signatures. | High |
| Predictive/hypothesis | Hypothesis and prediction classes | No explicit named pouring-specific hypotheses with antecedent, consequent, alternatives, uncertainty, and test design. | High |
| Epistemic | Evidence and trace concepts | No directly asserted provenance/epistemic-status graph of stereotypical pouring claims. | High |
| Failure/deviation | General failure ontology + safety critic | No pouring-specific failure taxonomy or recovery conditions explicitly connected to `Pouring`. | Medium |
| Foundational interoperability | 14 locally prefixed `dul_*` class names | No real DUL imports or audited bridging axioms; avoid automatic equivalence. | High |
| Knowledge vs world state | `BeliefState`, `Container`, `NEEM` provided | Guard against mixing action-type stereotypes with an execution episode, measurement, or current world-state instance. | High |

## 7. Competency questions for the inventory (action-type level only)

| CQ | Stereotypical competency question | Existing anchors | Inventory verdict |
|---|---|---|---|
| CQ1 | What participant roles define stereotypical pouring? | `PouringIntention` + role restrictions | Partly answerable |
| CQ2 | Which intentional goal and terminal state characterize pouring? | `PouringIntention` → `PouringTelos` → `AccumulatedState` | Directly answerable |
| CQ3 | Which causally relevant events and states characterize pouring? | `PouringTemplate` → efflux / flow / accumulation | Directly answerable as structural links |
| CQ4 | What is the expected temporal ordering, overlap or concurrency of the phases? | `PouringPhase`, `Grasping`, `Tilting` | Not encoded |
| CQ5 | What alternative generalized strategies could achieve pouring, and when? | `GeneralizedActionPlan`, `Contextualization`, `ActionDesignator` | Only meta-schema |
| CQ6 | Which preconditions enable efflux, and what counterfactuals interrupt it? | `ForceDynamicTemplate`, `BodyWorldConstraint`, `Hypothesis` | Not encoded as pouring-specific claims |
| CQ7 | What observations distinguish flow onset, steady flow and termination? | `ExpectedObservation`, `ProcessMonitoringExpectation` | Not encoded as pouring-specific links |
| CQ8 | Which effects or failure modes are anticipated and how are they monitored? | `SafetyCritic`, `FailureReason`, `ProcessMonitor` | Only generic support |
| CQ9 | What evidence supports, conflicts with, or qualifies a pouring hypothesis? | `EvidenceSet`, `NEEM`, `EvidenceBearingTrace` | Generic graph schema only |
| CQ10 | What action knowledge can be reused independently of robot/scene parameters? | `GeneralizedActionPlan`, `ManipulationFrame`, `ManipulationHypothesis` | Partly answerable |

## 8. Structural caveats and recommended next artifact

1. **The same ontology IRI appears in both files**. Do not import or merge them as independent versioned ontologies without reconciliation.
2. **`aicor:dul_*` names are local substitutes**, not external DUL imports: mapping should be audited explicitly, particularly classes mixing abstract descriptions and physical events.
3. **`Pouring` is classified through a generalized-plan hierarchy**, while `ForceDynamicEvent` is also classified as `Representation` and a local `dul_Event`: it is essential to separate types of actions, event schemas and action occurrences before establishing foundational equivalences.
4. **Four role existentials do not yield a complete frame**: they neither bind distinct role fillers to entities nor guarantee a destination physical container.
5. **OWL existential restrictions are not defaults, actual execution traces, temporal precedence, or causal implication rules**. Use explicit stereotype/hypothesis patterns and named source/epistemic annotations in the next step.
6. The files contain **zero `rdfs:comment` assertions**; the CRAM–AICOR graph contains **zero explicit `rdfs:domain` statements** and 94 explicit `rdfs:range` statements. Enrich documentation and validation in a separate module; do not change the original uploads at this stage.
7. This report inventories **directly asserted** vocabulary and axioms; it did not run a DL consistency/satisfiability reasoner and did not inspect external source ontologies by importing them into the merged graph.

**Recommended next artifact:** a separate `pouring-stereotype.ttl` module designed against this inventory, with explicit DUL-based frame patterns, distinct schematic descriptions and execution-event types, conditional hypotheses, temporal constraints, expected observations, and provenance. Create mappings as *proposals* first; validate with an OWL reasoner and SHACL before committing them.

## 9. References for candidate external ontologies

- DUL: http://www.ontologydesignpatterns.org/ont/dul/DUL.owl
- PROV-O: https://www.w3.org/TR/prov-o/
- OWL-Time: https://www.w3.org/TR/owl-time/
- SOSA/SSN: https://www.w3.org/TR/vocab-ssn-2023/
- QUDT: https://www.qudt.org/
- CRAM reference paper: https://link.springer.com/article/10.1007/s13218-026-00917-z

**Machine-readable companion artifacts:** `focused_classes.csv`, `focused_properties.csv`, `all_classes.csv`, `all_properties.csv`, `class_axioms.csv`, `shared_class_axiom_changes.csv`, `foundational_crosswalk_candidates.csv`, `inventory_stats.json`.
