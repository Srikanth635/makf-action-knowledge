# E1 0.2: source definitions and reported findings

E1 0.2 adds explicit categories for research material that could not be represented
faithfully as a strategy or general principle. The schema identifier is now
`https://w3id.org/aicor/extraction-contract/v0.2`; the extraction prompt is v4 and
advisory review prompt is v3. Original ontology files are unchanged.

| knowledge_kind | Required epistemic_status | Meaning |
| --- | --- | --- |
| benchmark_definition | definition | A source-defined benchmark interface, setup or reward metric, scoped to that benchmark |
| task_objective | definition | What the reported task seeks to achieve; this does not assert a method or success |
| reported_observation | reported_observation | A finding/comparison attributed to the source and its evaluated conditions, without treating it as a general law |

All three require `source_explicit` or `source_paraphrase`. The new epistemic status
is exclusive to `knowledge_kind=reported_observation`. Existing evidence, exact
quote, profile and local-ontology checks still apply. These labels establish neither
scientific acceptance nor independent corroboration. LLM-generated hypotheses and
proposals must retain their existing hypothetical/unassessed representation.

A benchmark reward is not automatically an observation expectation. An objective
is not automatically a strategy. A reported comparison is not automatically a
conditional principle. For example, SoftGym's statement that PourWater reward is
the fraction reaching the target cup is a benchmark definition. FluidLab's goal of
pouring the light liquid while retaining the heavy liquid is a task objective.
Its reported optimizer comparison is a reported observation under that evaluation.

`generic_description` with `needs_mapping`, no ontology class and a candid note is
valid when no suitable domain class is offered. The revised review instructions
explicitly distinguish missing mappings from unsupported evidence or scope. They
also clarify the new label pairs in initial review and revision prompts. This is
a review-policy correction; live model reliability has not been re-established by
these offline checks.

## Compatibility and migration

- Existing E1 0.1 JSON batches remain readable; old enum values are retained.
- A 0.1-only reader will reject the new values. Upgrade readers before generating
  0.2 records. Batch/profile IDs and the existing CURIE namespace are unchanged.
- The LinkML subset and generated JSON Schema were updated together. The three
  changed resource hashes (LinkML, JSON Schema, packaged SHACL) are intentionally
  refreshed in `RESOURCE_SHA256.json`; ontology hashes remain unchanged.
- Packaged RDF shapes accept the new categories and enforce the same status/source
  constraints. The draft publication record namespace remains 0.1: this change adds
  supported literal values without changing record/property IRIs. Export manifests
  retain resource hashes so the exact validation baseline is auditable.
- Historical model responses, review records and selections are not rewritten.
  Relabeling a candidate creates a new content-bound claim identity; prior review
  decisions cannot be carried onto that changed record.

The [three migration proposals](experiments/corpus_expansion_001/semantic-v02-proposals.json)
are explicitly assistant-authored source paraphrases, not a new live extraction or
human-approved dataset. They retain exact source evidence and leave missing mappings
open. Their local RDF export at
`/workspace/makf-rdf-runs/semantic-v02-proposals/` has three **pending** claims and
passes E1 and SHACL validation. It is separate from the two model-selected claims
in the previous research collection. Approval counts have not increased.

Offline regression checks cover all three categories, incorrect status combinations,
generated ideas falsely labeled as source reports, pending RDF export and invalid
RDF status escalation. The full existing suite checks compatibility with previous
pouring/grasping, extraction, review and publication behavior.

Verified result: 195 offline tests passed, 46/46 resource hashes verified, doctor
passed for both action profiles. The proposal export contains 168 quads and three
pending claims. RDFLib emitted deprecation warnings during the suite; no checks failed.

## Next boundary

Quantitative simulation evidence still needs a separate schema for values, units,
material/model assumptions, simulator/version, configuration and source artifacts.
The FluidLab annex has unresolved units and timestep/material descriptions. These
new labels do not make those settings executable or resolve their scientific
meaning. After the quantitative contract and live-review calibration, expand the
literature corpus using independent annotations and held-out evaluation.
