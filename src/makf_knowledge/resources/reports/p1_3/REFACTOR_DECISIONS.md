# P1.2 → MAKF extraction: decisions and limitations

## What was moved

P1.2 had **39 classes + 30 properties** in a pouring namespace. The refactor moved the two generic classes `ActionKnowledgeFrame` and `PossiblePhasePrecedence`, and **all 30 generic/composition properties**, into MAKF (29 retained their local names; `characterizesFlowState` generalized to `characterizesExpectedState`). The pouring module retains **37 pouring-specific classes** and **no locally declared object property**. MAKF has **18 generic classes and 31 object properties**, with one new umbrella relationship `hasPerspective`. The four new generic conceptual categories of phase, hypothesis, strategy and effect are instantiated only as OWL *class restrictions*, never concrete action occurrences.

See `migration_map.csv` for the complete, machine-readable 69-term mapping. When migrating third-party queries or a KG, replace old `paf:` generic property IRIs with their `makf:` counterparts. The new module does **not** declare deprecated alias properties: accidentally loading v0.1 and v0.2 together would risk different semantics and redundant ranges/domains. Do not merge them indiscriminately.

## What was refactored in place

- `paf:PouringKnowledgeFrame` now subclasses `makf:ActionKnowledgeFrame` and uses `makf:` composition properties.
- `paf:PouringRolePerspective` uses MAKF's role-perspective type and the existing DUL `definesRole` pattern.
- `paf:PouringScript` uses a generic temporal perspective and phase-pattern links, while pouring-specific flow-onset and termination phase patterns remain local.
- `paf:PouringStrategySpace`, `paf:PouringStrategy`, and candidate strategies use generic `StrategyPerspective`, `GeneralizedStrategy` and relations.
- The old hypothesis classes now specialize `makf:ActingHypothesis`, `makf:StrategyHypothesis` or `makf:CausalHypothesis` and use `makf:predictsPossibleEffect`.
- Observational, deviation and applicability spaces specialize analogous MAKF description patterns.

## Deliberate conservatism

1. **Event vs description:** `aicor:Pouring` is a generalized action category under `aicor:GeneralizedActionPlan`, not mapped to `dul:Action`. No frame is mapped to an actual `dul:Event` or `dul:Situation`.
2. **AICOR evidence-bound hypothesis:** `aicor:ManipulationHypothesis` requires `EvidenceSet` and conceptual robot-world family. MAKF uses only `aicor:Hypothesis` so speculative knowledge is not forced to cite a real episode.
3. **AICOR manipulation frame:** avoids subclassing `aicor:ManipulationFrame` because that class brings in a `ManipulationProblemClass` / `RWMSFamily` dependency. `rdfs:seeAlso` documents the conceptual relationship.
4. **Strategy:** generic `makf:GeneralizedStrategy ⊑ dul:Plan`. Only *pouring's* `PouringStrategy` also specializes existing `aicor:GeneralizedActionPlan`. This keeps MAKF action-independent, though pouring still inherits some AICOR *conceptual* `Contextualization` restrictions. These are not instantiated robot-world facts.
5. **No blanket upper ontology mapping:** AICOR's local `dul_*` names are not the official DUL entities. Only eight conservative subclass links are added; no `owl:equivalentClass` or unsound event mapping.
6. **No default-logic conflation:** RDF/OWL `someValuesFrom` means an existential structural restriction on class instances; it does not mean a *typical* probability, a physical cause, an ordering over real timestamps, or a verified prediction.
7. **Open-world:** not finding a failure pattern is not proof that an action is safe.

## Remaining conceptual tension in pre-existing source

CRAM–AICOR's **original** `aicor:Pouring` already entails `aicor:hasSubaction some aicor:Grasping` and `... some aicor:Tilting`. A purely generic pouring stereotype might instead allow *non-grasping* ways of pouring. The new pouring frame does **not** force `GraspPreparationPhasePattern` into every pouring script, but the upstream action-category class still has a mandatory existential grasping subaction. This cannot be resolved without a **separate reviewed change to the source ontology**. Treat it as a modeling issue, not a solved issue.

Likewise, a stereotypical source/destination relation does not imply a real material container or that a robot possesses any grasp configuration. World-model independence means *no concrete world individuals*, not the total absence of all physical-domain concepts.

## Import concerns

- Both AICOR sources share a logical ontology IRI; only expanded CRAM–AICOR is mapped as the one active dependency.
- The pinned official DUL axioms are not available in this package; tests do NOT prove OWL DL consistency against DUL.
- w3id.org IRIs used in development are placeholders until the team chooses and registers persistent identifiers.
- No SOMA imports or concepts.

## Follow-on technical work (not silently implemented)

1. Load actual official DUL, verify its digest/ontology IRI/version, resolve imports, and run a DL reasoner over the full closure.
2. Revisit `aicor:Pouring` mandatory grasp/tilt axioms and the local DUL event aliases; evaluate satisfiability.
3. Define how optional/typical/possible/necessary patterns are annotated (e.g., a dedicated modal profile or rules engine rather than pretending OWL class restrictions provide defaults).
4. Introduce carefully curated **knowledge-description individuals** only if necessary for graph retrieval. These are not physical-world instances; model them separately from executions.
5. Formalize a substantial grasping frame and demonstrate actual ontology-guided competency-question retrieval against both actions.
