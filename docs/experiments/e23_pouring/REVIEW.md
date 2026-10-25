# Review of the three provisional PourIt! candidates

This is a Codex-agent review against the supplied excerpt, not a human/domain
expert approval or independent verification of the paper's results. Original
generation artifacts remain untouched. The proposed revisions are explicitly
agent-authored and are not presented as a successful live model extraction.

## Candidate decisions

| Original | Decision | Proposed correction |
| --- | --- | --- |
| pourit-008-cand1 | Revise evidence, scope and mapping | Cite both initial-point strategy and bottleneck failure sentences. Limit the statement to the reported comparison. Keep the abstract strategy; remove the unsupported mapping of an estimation mechanism to aicor:PouringTemplate. |
| pourit-008-cand2 | Revise evidence and scope | Cite the complete feedback/size-estimation comparison. Describe the authors' method under the reported evaluation conditions; do not infer general superiority. |
| pourit-008-cand3 | Revise evidence, scope and unsupported detail | Cite the complete AFA failure explanation through the spillage outcome. Remove "mask of the liquid" because this excerpt does not specify the mask's referent. Represent the reported strategy and limitation, not an established conditional principle. |

All proposed candidates use `strategy_description`, `proposed_strategy`,
`conditional`, `source_paraphrase` and `source_anchored`. These labels describe
qualified method descriptions, not new LLM hypotheses or empirical corroboration.
`makf:GeneralizedStrategy` is used for the abstract strategies (its asserted parent
is DUL Plan); this does not certify their effectiveness or resolve DUL imports.
The source's lack of detailed experimental conditions is preserved, not filled in.

## Reproducible records

- `review-original-008.json`: snapshot of the original live batch, with its original
  generation metadata.
- `review-annotations.json`: source/original artifact hashes, issue labels,
  exact required evidence spans and mapping rationale. These are development
  annotations selected by the agent and require human review.
- `review-proposed.json`: separate E1-compatible proposed revisions, labeled
  `agent_authored_review_revision`. Offsets were computed from exact local source
  slices, not guessed by a model.
- `review-live-010.json`: new unedited live batch using prompt v3 and transport v2.
- `review-results.json`: coverage and agent review dispositions for all three sets.

Run from the repository root:

```bash
.venv/bin/makf validate docs/experiments/e23_pouring/review-proposed.json --profile pouring
.venv/bin/python -m pytest -q tests/test_review.py
```

`makf_knowledge.review.evidence_coverage` checks assertions against supplied
reviewer-selected evidence spans. It rejects absent/ambiguous quotes, bad offsets,
wrong attribution and context-only support; multiple exact lines may jointly
cover a span. It does not infer required spans or decide entailment, truth, scope
or mapping quality. Re-annotate if the claim changes. This optional review helper
does not silently change the canonical E1 acceptance contract.

## Live validation and limitations

| Set | E1 mechanical validation | Annotated coverage | Scientific disposition |
| --- | --- | --- | --- |
| Original run 008 | 3 candidates pass | 0/3 pass | Changes required |
| Agent-proposed revisions | 3 candidates pass | 3/3 pass | Human/domain review pending |
| Fresh live run 010 | 3 candidates pass | 0/3 pass | Changes required |

Run 009 failed before generation: OpenAI rejected newline-containing quote enum
values in the strict response schema (HTTP 400, `response_format`). A one-token
schema probe confirmed the same error and produced no model output.

Transport `openai-strict-v2` now offers evidence IDs with a caller-derived catalogue
of exact full passages and individual lines. After wire-schema validation, each
ID is resolved to its exact source text before E1 validation. Raw model text is
retained, and the catalogue is saved in the transport request. This is explicit
transport decoding, with no model-output repair or quote normalization. Unknown
IDs and incorrect document attribution are rejected. Prompt v3 asks for complete
clause coverage, qualified scope and conservative grounding.

Run 010 used `gpt-4.1-2025-04-14`, 8,488 input tokens and 1,265 output tokens. It
still selected incomplete line evidence rather than complete available passages.
Candidate 1 retains a conditional-principle label and an overly strong reliability
requirement; candidate 2 still maps a causal mechanism to PouringTemplate;
candidate 3 again adds "liquid mask" and generalizes the AFA finding. These are
recorded failures, not successful scientific extraction. Raw artifacts are at
`/workspace/makf-live-runs/pourit-20261024-010/`.

Next: have a domain reviewer assess the proposed revisions and the annotations;
then evaluate a separate, explicitly audited claim-review stage or constrained
claim/evidence representation. Test on held-out passages before claiming improved
generalization. These three examples were used to develop the changes and are
not a benchmark of extraction accuracy. OntoGPT comparison remains pending.

## Follow-up

The [quality workflow evaluation](../../QUALITY_REVIEW.md) records the separate model review, one-revision experiments, control-set failures and eventual one-candidate selection. This earlier review remains a historical record.
