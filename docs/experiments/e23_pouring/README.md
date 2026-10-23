# PourIt! scientific extraction pilot

**Status: prepared, not executed live.** The OpenAI command below was attempted
but exited before any API call: `Set MAKF_OPENAI_API_KEY securely before using OpenAI`.
Both supported credential variables were absent, and the saved environment secret
requirement had no value binding. A separate unauthenticated API connectivity probe
was blocked by the existing network allowlist. There are **zero live model responses
or extracted candidates** to evaluate. Offline fixture results are not substituted.

## Genuine source

Haitao Lin, Yanwei Fu, Xiangyang Xue (2023), *PourIt!: Weakly-supervised Liquid
Perception from a Single Image for Visual Closed-Loop Robotic Pouring*, ICCV 2023,
pp. 241–251. [arXiv identity](https://arxiv.org/abs/2307.11299),
[authors' code and citation](https://github.com/hetolin/PourIt).

The actual excerpt was retrieved from the author's preprint PDF, pinned to a
[specific website-repository commit](https://raw.githubusercontent.com/hetolin/hetolin.github.io/eea048d3a8401d00a5e946c3f42bdab046a6d620/PourIt/resources/images/arXiv_pre.pdf).
The paper title/authors were checked in the downloaded PDF. Its section 4.3,
“Results and Analysis,” on PDF page 8 contains the selected 108-word passage about
pose/size estimation, feedback-based pouring-point adjustment, and spilling due to
incorrect visual feedback. This is an author-hosted preprint; it has not been
asserted byte-identical to the final proceedings PDF.

[source.txt](source.txt) is an exact contiguous slice of default `pdftotext` output.
Line breaks and extractor artifacts (including `container-tocontainer`) are
preserved. Quotation offsets refer to this supplied text, not PDF byte positions.
[provenance.json](provenance.json) records authorship, locator, retrieval URL/commit,
retrieval time, PDF and passage hashes, extraction tool version and `synthetic_demo=false`.
The full PDF is not added to the repository. No DOI was guessed.

## Bounded run

Install `.[dev,openai]` and securely bind `MAKF_OPENAI_API_KEY` to
`api.openai.com` in environment settings. Save the network/credential settings;
draft saving alone does not apply them. The source is already local, so this pilot
needs only the OpenAI destination at execution time.

From the repository root:

```bash
.venv/bin/makf extract \
  --provider openai --model gpt-4.1-mini-2025-04-14 --profile pouring \
  --text-file docs/experiments/e23_pouring/source.txt \
  --source-id lin-etal-2023-pourit-author-preprint \
  --source-title 'PourIt!: Weakly-supervised Liquid Perception from a Single Image for Visual Closed-Loop Robotic Pouring' \
  --source-uri https://arxiv.org/abs/2307.11299 \
  --locator 'Author-hosted preprint, section 4.3 Results and Analysis, PDF page 8' \
  --passage-id results-analysis-strategies --batch-id e23-pourit-pilot-001 \
  --max-output-tokens 6000 --out-dir /tmp/makf-e23-live-pourit-001
```

Do not pass `--synthetic-demo`: this is a genuine source. Use a new run directory
and batch ID for any additional trial. The model choice is explicit and bounded;
account access to this snapshot has not been verified. One call, all packaged
pouring perspectives, at most three requested candidates, no automatic retries.
Preserve failed attempts and adjust only after diagnosing a concrete issue.

## Review after the live result

Record the returned model, request ID, usage, raw response, validation result and
candidate count. For each candidate inspect:

1. Exact quotes, document/passages and any character spans.
2. Whether it describes a reusable strategy, observation, causal possibility,
   applicability condition or deviation, instead of a particular scene or robot.
3. Whether distinct perspectives are supported by the text rather than merely
   enumerated; unsupported perspectives may be absent.
4. Whether modality, derivation and evidence labels preserve the paper's limited
   experimental context. “Less influenced” must not become an unconditional law.
5. Whether a proposed idea is kept separate from what the source actually asserts.

A provisional batch is only a mechanically validated candidate set. Abstention
or quarantine is a valid experimental outcome but not successful extraction.
One short passage is a feasibility pilot, not a benchmark of extraction accuracy.

**OntoGPT evaluation is deferred until this live experiment has actually run.**
No alternative-backend comparison has been performed yet.
