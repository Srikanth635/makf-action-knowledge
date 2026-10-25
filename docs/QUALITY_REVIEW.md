# Optional extraction quality review

The extraction CLI can now run a separate model assessment of evidence coverage,
claim scope and component mappings. This supplements E1's mechanical validation;
it is an advisory model judgment and still requires human/domain review.

Add these options to the documented `makf extract` command:

```bash
--model gpt-5.4-2026-03-05 \
--review-model gpt-5.4-2026-03-05 \
--revise-once --select-reviewed \
--max-output-tokens 12000 --timeout 180
```

Use a fresh output directory. Both models are explicit choices; GPT-5.4 access was
verified in this environment. Without `--review-model`, existing extraction
behavior remains unchanged. Review adds one API call. `--revise-once` permits one
additional generation and one second review, at most four calls including initial
extraction. There are no automatic API retries or unbounded revision loops.

Each reviewer must assess every candidate exactly once with nonempty rationale.
Missing, duplicated or foreign candidate IDs, malformed reviews, provider failures
and failed mechanical validation cannot yield a selected batch. A review is bound
to the exact batch hash. Revision preserves retained candidate IDs and records
omissions. A rejected revision never falls back to an earlier rejected batch.

## Artifacts and selection

The original run stays at the output root. `quality-review/` retains the review
prompt, raw response, request and report. A revision has its own `revision/`
directory, raw generation, E1 result, parent-batch hash and nested quality review.
The review response includes provider/model IDs, usage and all three checks.

`workflow.json` records the selected relative run path, status and omissions.
Whole-batch review is the default. With `--select-reviewed`, candidates passing
all three checks can be copied unchanged into a separate `selection/` directory;
the selection manifest lists every selected and withheld ID and binds the source
batch and review hashes. No candidate is rewritten by selection. Empty selections
do not create a candidates file. E1 mechanical validation still accepts or rejects
each generated batch as a whole; this explicit subset step happens afterward.

Statuses `quality_passed_provisional` and `model_reviewed_subset` mean model-review
outcomes, not scientific acceptance. A partial selection is explicit in CLI output
and the manifest. Review failure returns nonzero unless a subset was explicitly
requested and contains passing candidates. Abstention selects no candidates.

## Development evidence on 2026-10-24

Raw experiments remain under `/workspace/makf-live-runs/`. The known bad run 010
was reused as the initial batch in experiments 011–014; it was not regenerated.

| Experiment | Result |
| --- | --- |
| 011, GPT-4.1 reviewer/reviser | Improved citations but falsely approved remaining mask/scope/mapping issues. Do not use this as scientific acceptance. |
| 012, GPT-5.4, review v1 | Two revised candidates passed reviewer checks; the AFA candidate failed; whole batch withheld. |
| Synthetic controls 001 | Detected three deliberately bad examples, but rejected the positive example over metadata semantics. |
| 013, GPT-5.4, review v2 | Two revised candidates passed; AFA still failed; whole batch withheld. |
| Synthetic controls 002, review v2 | Accepted the positive example; rejected incomplete citations, universal claims and unsupported causal mapping in three negative examples. |
| 014, GPT-5.4, review v2 | One revised candidate passed all checks; two withheld. Explicit subsequent subset selection retained that one unchanged candidate. |

The synthetic controls were used during reviewer calibration, so 4/4 on that tiny
set is not an independent accuracy estimate. Model reviews are stochastic, and
the generator and reviewer used the same model in separate calls; their errors
may be correlated. The reviewer remains inconsistent about `proposed_strategy`
labels: in run 014 it treats the label as restricted to the source authors' own
method despite contrary review guidance. This may be a false rejection of the
first candidate. Human review must resolve that semantic ambiguity.

The selected candidate in run 014 describes the authors' pose-feedback method,
qualifies the comparison as a source report, quotes the complete passage, and
leaves the comparative-effect component `needs_mapping`. Its annotated evidence
coverage and E1 checks pass. That is a concrete improvement over the original
three incomplete citations; it is not evidence that all extraction errors are
fixed. No ontology or graph was populated.

See [saved evaluation](experiments/e23_pouring/quality-evaluation.json) for model
assessments, IDs, usage and selection hashes, and [selected candidate](experiments/e23_pouring/quality-selected.json).
The original three candidate revisions and development annotations remain separate.

Next validation should use new scientific passages and domain-reviewed labels,
including negative examples and abstention, to measure false acceptance, false
rejection and retained coverage before adopting this as a default workflow.

Validation of the final implementation: 143 offline tests passed; 44/44 bundled resources verified; the selected candidate passed E1 and annotated evidence coverage. Tests cover malformed/missing/duplicate reviews, each failure dimension, the call limit, preserved originals, rejected revisions, explicit omissions, selection hash binding and CLI client cleanup.
