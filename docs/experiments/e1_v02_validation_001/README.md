# E1 0.2 live validation with current GPT models

The API model list was checked on 2026-10-24. This pilot requested and received
`gpt-6.1-sol` for extraction and `gpt-6-astra` for cross-model review. Both models
also reviewed an identical fixed calibration set twice. Discovery metadata is in
[available-models.json](available-models.json); model/request IDs, usage, prompt
versions and decisions are retained in the report artifacts.

## Frozen protocol

[controls.json](controls.json) and [expected.json](expected.json) were prepared
before live review: six supported candidates and six adversarial candidates.
Positives cover E1 0.2 benchmark definitions, task objectives, reported observations,
and an honestly unmapped strategy. Negatives cover incomplete citations,
unsupported universal claims, unrelated grounded mappings, an opposite objective,
unquoted component details and an invented causal conclusion.

An initial offline preflight correctly rejected an unavailable ontology-class
mapping. Before any live review, that control was changed to an offered but
semantically inappropriate strategy class, so the test exercises review rather than
merely the offered-vocabulary gate. The initial artifact is retained outside the
checkout; the final input/expectation hashes are recorded in config.json.
No labels or prompts were tuned after observing live results.

Every final control passed the existing mechanical pipeline. The negative examples
are deliberately faulty claims, not scientific additions. Two repetitions per model
use the same inputs, rubric and expectation labels. Expected labels are authored by
the assistant, not independently adjudicated domain experts. This is development
calibration on known sources, not a held-out accuracy benchmark.

A case passes only when evidence_complete, scope_supported and mapping_supported
are all true. The small-pilot criterion was no false acceptance/rejection; complete
coverage is also required. The mixed batch returning changes_required is correct:
it contains deliberately invalid candidates.

## Results

| Reviewer | Runs | Decisions | False acceptances | False rejections |
| --- | ---: | ---: | ---: | ---: |
| GPT-6.1 Sol | 2 | 24 | 0 | 0 |
| GPT-6 Astra | 2 | 24 | 0 | 0 |

All supported unmapped descriptions passed; all flawed controls failed. Repeat
accept/reject decisions were consistent on this set. [metrics.json](metrics.json)
and [summary.json](summary.json) retain counts and individual rationales.

Fresh GPT-6.1 Sol extraction used the unchanged six saved SoftGym/FluidLab passages,
E1 0.2, extraction prompt v4 and advisory review v3. GPT-6 Astra reviewed the fresh
candidates without a revision loop:

| Source | Extracted | Model-selected | Kinds |
| --- | ---: | ---: | --- |
| SoftGym | 3 | 3 | task_objective; two benchmark_definition |
| FluidLab | 3 | 3 | task_objective; benchmark_definition; reported_observation |

The descriptions distinguish task goals, control/reward/loss definitions and
source-scoped optimizer comparisons. Exact quotations, source metadata and mapping
notes are retained. All six passed E1 and RDF SHACL checks and remain provisional.
Many components deliberately remain needs_mapping. No human approval or new physics
measurement is inferred from a model-review pass.

Eight model calls were made: four calibration reviews, two extractions and two
cross-model reviews. There were no revision/retry calls. Usage: 63,487 input tokens,
9,809 completion tokens (73,296 total). No cost estimate is invented.

## Artifacts and limits

Raw prompts, transport requests, responses, reports and RDF bundles are retained at
`/workspace/makf-live-runs/e1-v02-validation-001/testing-002/`:

- `fresh-softgym/rdf/`: three newly model-selected claims.
- `fresh-fluidlab/rdf/`: three newly model-selected claims.
- Per-model repetition folders: complete control review audits.

Portable copies of fresh candidates, extraction reports, review reports and selection
manifests are in this directory. These exports are new snapshots; the older two-claim
research collection and the separate three pending migration proposals are preserved.
The six new claims have not been deduplicated or merged into the older collection.

This is encouraging evidence for the revised labels and mapping policy, not proof
of general model quality. The papers and controls were already used in development;
no expert-held-out pouring/grasping evaluation or statistical reliability estimate
is claimed. Changes since the earlier pilot include both model and contract/prompt
changes, so the retention difference is not a controlled causal model comparison.
The reviewer saw the provided passages, not the full papers or conflicting material
parameter tables. A source-attributed non-Newtonian description therefore does not
resolve the known material-model issue in the numerical annex.

The next quantitative step is specified in [QUANTITATIVE_SIMULATION_PLAN.md](../../QUANTITATIVE_SIMULATION_PLAN.md).
Use the four annex records as fixtures, representing unknown units and contradictory
settings explicitly before unit conversion or executable simulation configuration.

Offline verification: 28 relevant reporting/review/corpus regression tests passed,
46/46 resources verified, frozen control hashes and complete case coverage checked,
and both exported RDF bundles passed artifact-hash and parsing checks. No application
code or schema changes were needed for this experiment.

## Reproduce

These commands make paid live requests and require the optional openai/rdf extras:

```bash
.venv/bin/python docs/experiments/e1_v02_validation_001/run_validation.py \
  --out-dir /tmp/makf-e1-v02-new-validation \
  --extract-model gpt-6.1-sol --review-model gpt-6-astra
```

Use a new output directory. Recheck the API model list before a future evaluation;
current aliases and access can change. The script preserves failed responses and
never changes expected labels or retries until a pass.
