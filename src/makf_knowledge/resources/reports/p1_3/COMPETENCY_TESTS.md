# Action-agnostic competency questions and smoke test

This test checks whether a single abstract **multiperspective action knowledge framework** is reusable across two action *types* without mentioning an actual scene or robot.

| Question | Pouring source | Grasping source | Test expectation |
|---|---|---|---|
| Which generalized action is described? | `aicor:Pouring` | `aicor:Grasping` | `makf:hasActionCategory some ...` |
| Which participant role patterns apply? | Agent, Source, Substance, Destination, Goal | Agent, Patient | `makf:hasRolePerspective` / `dul:definesRole` |
| What is intended? | `aicor:PouringIntention` | Generic `GraspingIntentionPattern` | `makf:hasIntentionalPerspective` |
| What causal template is referenced? | `aicor:PouringTemplate` | `GraspingCausalTemplate` | `makf:hasCausalPerspective` |
| Which script structures could exist? | Initiation, termination phase patterns | Contact establishment pattern | `makf:hasTemporalPerspective` |
| What hypothetical strategies could be available? | Orientation mediated / feedback regulated | Contact guided | `makf:containsStrategy` |
| Which conditions could matter? | Outflow enabled / flow sensitivity | Contact conditions | `makf:hasApplicabilityCondition` |
| What effects could be predicted? | Flow onset / uncontrolled outflow | Stable coupling | `makf:predictsPossibleEffect` *inside hypothesis* |
| What observation cues are stereotypical? | Flow onset / termination | Contact cue | `makf:hasExpectedCue` |
| What deviations could be expected? | No flow / outflow / destination miss | Slip pattern | `makf:hasDeviationPattern` |

**Automated checks** (`tests/validate_modules.py`): all ten composition restrictions exist for both action frames; every MAKF reference is declared in the reusable core; migration map has 69/69 P1.2 symbols; no named physical-world individuals or event-class mappings; graph source vocabularies resolve. The new core contains no term with `Pouring` or `Grasping` in its IRI, name, label or comment.

**Interpretation:** passing this test shows architectural generality and preservation of explicit schema links. It does **not** show that an LLM/GraphRAG can yet retrieve the right knowledge, that external DUL axioms are logically consistent with AICOR, or that any described action is feasible.

Run `python tools/query_frames.py` to view the declared class restrictions. It is intentionally neither a DL reasoner nor an event simulator.
