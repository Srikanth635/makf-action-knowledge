# E2 implementation plan — minimal viable ontology-guided extraction

**Do not jump directly into TigerGraph or construct a particular world model.**

## Acceptance criteria
1. `makf extract --profile pouring --text-file ... --source-id ...` (or equivalent documented API/CLI) produces E1-shaped provisional candidates from passages provided by the user. The default offline test suite must not call live services.
2. A reusable provider protocol/adapter separates the prompt + schema, provider IO, JSON parsing, and semantic validation. Implement one structured-output provider as optional dependency and an offline fixture provider. Do not require OntoGPT initially; document integration as later comparison.
3. Profiles and ontology context come from packaged resources rather than hard-coded pouring terms. Grasping demonstrates reuse.
4. Evidence `quote` is an exact contiguous substring of the supplied source and claims cite document/span. Candidates lacking exact quoted evidence are rejected or clearly flagged.
5. Preserve three distinct statuses: knowledge type (definition/stereotype/principle/hypothesis), derivation type (explicit/paraphrased/LLM-derived/LLM-proposed), evidence status (unassessed/source-supported/contradicted/etc.). Do not claim truth from schema validity.
6. Define a quarantine/candidate state; do not add unverified hypotheses as unconditional ontology axioms.
7. At least one positive and five adversarial negative tests; all core tests pass offline. Add model prompt-injection resistance tests treating paper text as untrusted content.
8. Documentation includes an example using a **clearly synthetic text sample** and steps for an authenticated real model provider; no placeholder citations disguised as scientific evidence.

## Sequence
- E2.1: inspect E1 schema / profiles / validator and define extract interface — implemented
- E2.2: implement prompt builder with small per-perspective ontology context — implemented
- E2.3: offline fixture transport and optional OpenAI structured-output adapter — implemented, offline-tested
- E2.4: validate candidates, save report and quarantine failures — minimal batch-level runner implemented
- E2.5: run a scientific pilot — prepared genuine PourIt! excerpt; live run blocked on credentials; evaluate OntoGPT only after that run

E2.1/E2.2 design, synthetic usage, tests and remaining boundaries are documented in
[E2_PROMPT_INTERFACE.md](E2_PROMPT_INTERFACE.md). The acceptance criteria above cover
the whole E2 milestone. The [provider interface](E2_PROVIDER_INTERFACE.md) now
implements transport and quarantine; [live pilot status](experiments/e23_pouring/README.md)
remains separate from offline test success.
E1 requires a nonempty candidate batch, so prompt responses may alternatively be
an explicit abstention object. The E1 schema and its validator are unchanged.

## Boundaries
No robot-specific physical parameters, grasp trajectories, ROS interfaces, NEEM episodes, implicit DUL imports, or claims of empirical truth. Do not modify original user-provided ontologies.
