# Roadmap toward the intended MAKF knowledge system

Saved 2026-10-24 from the proposed path discussed with the user. This is a plan,
not a claim that the listed future capabilities already exist.

## Intended outcome

Scientific literature → traceable extraction → reviewed knowledge descriptions →
validated RDF knowledge graph → evidence-backed retrieval and hypothesis support.

Represent generalized robotic action knowledge: strategies, conditions, roles,
phase patterns, observations, deviations and hypotheses. Preserve source evidence,
applicability, modality, derivation and review status. Keep the system independent
of a particular robot, scene or physical execution. Use DUL, AICOR/CRAM–AICOR,
MAKF and action-specific frames; no SOMA. Consumers may later connect retrieved
knowledge to their own world models through an explicit separate interface.

## Current baseline

- Modular ontology vocabulary and tentative DUL alignment exist; formal foundation
  and import checks remain incomplete.
- E1 provides the LinkML-subset contract and local structural/semantic validation.
- E2 provides OpenAI extraction, provenance artifacts, optional model review,
  one revision and explicit selection with withheld-candidate records.
- The latest selected live record is provisional and includes an unmapped
  comparative-effect description. A model review is not human/scientific approval.
- Extracted knowledge is JSON with [optional local RDF export](RDF_PUBLICATION.md),
  E1/SHACL validation and content-bound provisional review metadata. A real selected
  candidate has been exported. Production promotion, a graph database, TigerGraph
  and GraphRAG remain pending; export does not establish scientific acceptance.
- OntoGPT has not been installed, integrated or evaluated in this project.
- Current validation record: 185 offline tests and 46 bundled resources passed;
  installed-wheel RDF export also passed.
  Existing coding changes are local and uncommitted.

## Implementation sequence

| Step | Work | Completion criterion |
| --- | --- | --- |
| 1. Stabilize meanings and baseline | Define proposed_strategy, reported observations, conditional principles and hypotheses; clarify the difference between source support, scientific support and review approval. Resolve inconsistent reviewer interpretations. Review and checkpoint current changes. | Versioned definitions with positive/negative examples and consistent decisions; a reproducible code baseline. |
| 2. Validate ontology foundations | Resolve AICOR/CRAM–AICOR's shared ontology IRI, official DUL imports and questionable restrictions. Run formal OWL consistency checks and official LinkML validation. Preserve original files unless changes are explicitly authorized. | A versioned, reproducible ontology/schema baseline and documented remaining limitations. |
| 3. Build independent evaluation | Select new scientific passages containing strategies, conditions, failures, hypotheses and unsupported claims. Obtain domain-reviewed annotations; include pouring and grasping. Separate development and held-out sets. | Held-out measures of false acceptance/rejection, exact and complete evidence coverage, mapping correctness, abstention and retained coverage; acceptance thresholds agreed before final evaluation. |
| 4. Compare extraction backends | Implement an optional OntoGPT adapter and compare it with the OpenAI pipeline on identical sources and checks. Measure quality, cost, latency and abstention. | An evidence-based backend decision; both remain behind the provider interface and canonical E1 checks. |
| 5. Reproducible document ingestion | Add bibliographic metadata, section-aware passage extraction, stable passage IDs, hashes, offsets and document-version tracking. Preserve original text and extraction artifacts. | Every candidate traces to an exact passage and ingestion version without manual preparation. |
| 6. E3 JSON-to-RDF publication | Define claim/component/provenance mappings, stable IRIs, review states and named-graph boundaries. Implement an exporter and SHACL validation. Never turn provisional hypotheses into unconditional laws. | A small reviewed dataset exports repeatably to RDF, passes validation and preserves all evidence/status fields. |
| 7. Knowledge curation | Handle duplicate claims, cross-paper support, differing conditions, contradictions, updates and review decisions. Keep generated hypotheses distinct from source claims. | Multi-paper knowledge retains provenance and disagreement; every merge or status change is auditable. |
| 8. Retrieval and graph integration | Establish canonical RDF/SPARQL queries, then design a TigerGraph projection and GraphRAG retrieval layer. Preserve identifiers, conditions, provenance and epistemic status across representations. | Queries return relevant knowledge with evidence and qualifications; projection does not lose semantics or become an unaudited second source of truth. |
| 9. Validate the final application | Test end-to-end questions about action strategies, applicability, failures and hypotheses. Assess grounded answers, citations, omissions and unsupported inference. | Answers cite retrieved records and distinguish source claims, reviewed knowledge and generated hypotheses; limits are exposed to consumers. |

## Work order and first milestone

Start with step 1 and the design of step 3 while preparing step 2. Steps 2 and 3
can progress in parallel where independent. Use the evaluation set for step 4;
prototype ingestion afterward without losing passage fidelity. Resolve the
publication contract and foundation issues before treating step 6 as production
ready. Steps 7–9 depend on a validated RDF representation.

The first milestone is consistent candidate semantics plus an independent
scientific evaluation set—not another isolated successful model response. Exact
thresholds require domain review rather than invented accuracy targets.

Publication progress: draft 0.1 now has a configurable local exporter, expanded
SHACL checks and a contract test against the 61-quad real-candidate fixture. Review
decisions are bound to the exact reviewed content. This completes an initial step 6
increment, not production promotion. Label definitions still require domain review;
the independent evaluation set and ontology foundation work remain open.

A [research corpus pilot](experiments/corpus_expansion_001/README.md) now adds
SoftGym/FluidLab sources and a published-simulation settings annex. One new SoftGym
claim joins PourIt! in a 127-quad collection; FluidLab's candidate claims are held.
Before bulk ingestion, clarify benchmark definitions, task objectives and reported
observations, and resolve the reviewer's inconsistent treatment of unmapped
components. Quantitative simulation evidence also needs explicit units and model
provenance. These development passages are not a held-out evaluation set.

The next semantic increment is implemented as [E1 0.2](E1_V02_MIGRATION.md):
benchmark definitions, task objectives and reported observations have explicit
source/status rules. Review instructions now explicitly permit candid unmapped
components. Three migration proposals are exported separately as pending; they
do not increase the model-selected collection or establish improved live accuracy.
Next, calibrate the changed review policy and define quantitative evidence with
units/model provenance before scaling literature ingestion.

The [current-model calibration](experiments/e1_v02_validation_001/README.md) now
passes its small fixed control set: GPT-6.1 Sol/GPT-6 Astra made 48/48 expected
decisions over two repeats each, and six freshly extracted paper claims passed
cross-model review and RDF validation. Independent domain/held-out evaluation
remains open. Proceed with the [quantitative evidence contract](QUANTITATIVE_SIMULATION_PLAN.md)
using unknown-unit and conflicting-setting fixtures before broader ingestion.

The [quantitative archival contract](QUANTITATIVE_EVIDENCE.md) now implements the
first milestone: four FluidLab records represented as ten scalar quantities, strict
source/numeric/unit checks, explicit issues and conservative eligibility flags.
Next are structured cross-study comparison context, broader verified unit mappings,
quantitative RDF and source/code resolution before executable configurations.

## Representative final queries

- Which pouring strategies reduce dependence on object-size estimation, according
  to which papers and under which stated conditions?
- Which failure descriptions qualify those strategies, and are apparently
  conflicting claims actually about different conditions?
- Which hypotheses remain untested, and what observations could test them?
- Which knowledge patterns transfer to grasping, and which mappings remain open?

See [RDF design illustration](design/FINAL_RDF_GRAPH.md) for a proposed graph shape,
and [quality evaluation](QUALITY_REVIEW.md) for current extraction limitations.


## Quantitative RDF increment, 2026-10-25

Quantitative snapshots and SHACL/source-fidelity checks are implemented. A
[versioned FluidLab code audit](experiments/fluidlab_code_audit_001/README.md)
records timing/density discrepancies without changing reported values. Explicit
curated E1 claim links, physical reference scales, exact experiment provenance and
cross-study comparison policies remain open before simulation execution.

The [prerequisites investigation](experiments/fluidlab_prerequisites_001/README.md)
now establishes official-repository provenance and a pinned candidate config, plus
a parse-checked renderer keyword compatibility patch. Exact paper-result matching
and physical reference scales remain unverified. Distinguish a new native-unit run
from paper replication and SI calibration: the former needs a verified runtime,
while the latter two need additional experimental/calibration evidence.

The [first native-unit smoke](experiments/fluidlab_smoke_001/README.md) now passes
on CPU: 40,604 particles, two forward steps plus reset replay, finite states and
retained active particle mass. Runtime patches/dependencies are recorded. Proceed
to longer controlled rollouts and finite-difference gradient checks before an
optimization pilot. This does not resolve physical scales or paper-result provenance.

The [local validation pilot](experiments/fluidlab_validation_001/README.md) now
completes two 100-step forward cases, a narrow four-step directional derivative
check and three accepted local descent proposals (about 0.43% partial-loss reduction).
Six provisional local-simulation quantities have been exported with native units.
This is not full-task optimization or gradient correctness generally. Measure repeat
noise, test more epsilon/direction/contact/horizon cases, then validate the terminal
objective before larger optimizer or task-performance claims.

The [expanded gradient experiment](experiments/fluidlab_gradient_002/README.md)
now completes five control/pose/horizon cases with a saved protocol. Four pass;
rotation lacks two adjacent informative, stable checks, so the broader gate fails.
Terminal tests and further optimization remain blocked. Next measure noise per
condition and diagnose rotational sensitivity/cancellation; use a new predeclared
verification protocol afterward. Preserve this result rather than loosening its
criteria. The partial-objective results do not establish successful pouring,
contact-gradient correctness or validity of the original terminal objective.

The [per-condition repeat diagnostics](experiments/fluidlab_noise_003/README.md)
now complete 164 forward evaluations and 15 reverse passes. Repeated rotational
probes at intermediate scales agree with median AD within about 0.47%; finer probes
are insufficiently separated from observed variation. Baseline variation depends
on the condition and exported resets match. This is calibration, not a replacement
pass for the prior failed gate. Next fix a fresh verification protocol with local
noise measurements and represented controls before shortened terminal and extended
objective checks. No numerical physics changes or scientific promotion are justified
by these diagnostics alone.

GPT-6 Astra's advisory review and source follow-up retain a separate earlier-action
eight-step discrepancy and a possible friction normalization denominator hazard.
Neither is a demonstrated simulation defect. Instrument relevant branches and
compare fresh-process resets before interpreting new verification results; avoid
assigning residual discrepancies solely to observed repeat noise.

[Fresh verification 004](experiments/fluidlab_verification_004/README.md) now passes
its saved development gate for all five cases, with median derivative discrepancies
at most about 1.78%. Fresh-process controls pass. A recording bug in the shadow
observer was corrected with a saved, separately rerun amendment; original numerical
results/criteria and historical failed gates remain intact. No zero denominator was
observed in the corrected shadow probes, but native backward/contact safety and the
earlier-action residual remain unresolved. Next separately test recomputed-target
and frozen-target shortened terminal objectives, with explicit target/rank/scale
provenance, before optimization or full-horizon claims.
