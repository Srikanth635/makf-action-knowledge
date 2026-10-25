# E2.3: OpenAI transport and end-to-end runner

`OpenAIProvider` implements the existing `generate(prompt) -> str` protocol using
Chat Completions with strict Structured Outputs. `FixtureProvider` returns an
explicitly supplied offline response. `extract(request, provider)` separates IO,
JSON parsing, request-bound checks, E1 semantic validation, and artifact persistence.
The OpenAI adapter is implemented and has been exercised live; see [current progress](CURRENT_PROGRESS.md) for outcomes.
See the [prepared PourIt! pilot and blocker](experiments/e23_pouring/README.md).

## Install and configure

```bash
python -m pip install -e '.[dev,openai]'
```

The SDK is an optional extra (`openai>=2,<3`). Core imports, prompt construction,
E1 validation and fixture transport do not import the SDK or need credentials.
The implementation was exercised with OpenAI SDK 2.54.0. A separate integration
test uses that SDK with a mocked HTTP transport; this is not a live API test.

Configure `MAKF_OPENAI_API_KEY` securely in environment settings, bound to
`api.openai.com`. Standard local setups may use `OPENAI_API_KEY` as a fallback;
this cloud platform reserves that prefix, so the cloud binding uses the MAKF name.
`--api-key-env` accepts a variable **name**, never a key value. Keys are never
written to prompts, logs, reports, CLI arguments or the repository.

The endpoint is fixed to `https://api.openai.com/v1`; ambient `OPENAI_BASE_URL`
cannot redirect source text or authentication. TLS uses the system trust store
with certificate and hostname verification. Proxy-backed placeholders are passed
normally to this allowed HTTPS destination, not interpreted as raw secrets.

## API and execution

```python
from makf_knowledge import OpenAIProvider, extract

# request is an ExtractionRequest built with known source metadata and exact text.
provider = OpenAIProvider("gpt-4.1-mini-2025-04-14", max_output_tokens=6000, timeout=60)
try:
    result = extract(request, provider)
    result.save("/tmp/makf-new-run")  # requires a new directory
finally:
    provider.close()
```

The model is explicit; the example snapshot is a proposed pilot choice, not a
claim that account access to it has been verified. One request is made with
`store=False`, a 60-second default timeout, and no automatic retries. Output tokens
are bounded (default 6000, permitted 1–16000). The transport instructions request
at most three justified candidates for this pilot. No tools, retrieval, automatic
repair calls, ontology updates, or graph publication are performed.

The [pilot record](experiments/e23_pouring/README.md) includes a complete
`makf extract --provider openai --model ...` command. Source arguments match
`makf prompt`; `--out-dir` is required and must not already exist. A successful
command can mean either provisional candidates or explicit abstention, so inspect
the reported status. Invalid output and provider failures exit nonzero.

For offline transport use `FixtureProvider(raw_response)` or
`--provider fixture --fixture-file response.json`; no model is selected. Fixture
reports explicitly record `engine=offline_fixture` and `live=false`. The new tests
use synthetic examples with classes present in the compact prompt context. Fixture
success demonstrates the software pipeline, not model extraction ability.

## Transport schema versus canonical E1

OpenAI strict output expects an object root and requires every property to be
listed as required. The adapter therefore requests `{"result": <batch-or-abstention>}`
and makes optional E1 fields nullable. E1's `oneOf` becomes a nested `anyOf`.
Unsupported/portable constraints (length, date format, document-array `const`) are
enforced locally against the unchanged original request-bound schema; scalar
constants become enum singletons in the wire schema. Epistemic enum values are
preserved. A provider cannot bypass local original-source checks by changing its
copy of the source records.

After strict wire-schema validation, the parser removes only null-valued optional
fields, then validates the normalized E1 response. It never changes non-null values,
repairs quotes, guesses offsets, removes unexpected fields or coerces statuses.
Duplicate JSON keys, non-finite numbers, Markdown wrappers, trailing material,
refusals, filtered responses and token-truncated output are not accepted as batches.
Model-authored `extraction_run` data is rejected; actual engine/model/prompt version
and time are recorded by the caller after validation.

In addition to E1 checks, the runner rejects grounded classes/properties absent
from the offered prompt context, corroboration inferred from extraction alone,
generated ideas labeled as source assertions, whitespace-only quotes and offsets
beyond a passage. Generated ideas require `context_only` source roles and
`not_assessed` evidence status. E1's required hypothesis condition/effect/strategy
relations, modality checks and exact quotations remain enforced.

## Reports and quarantine

Run directories are created with owner-only directory permissions. They contain
source text and model output and should be treated as research records.

| Artifact | Meaning |
|---|---|
| `prompt.json` | Canonical prompt, source digest, and request-bound response schema |
| `transport-request.json` | Actual OpenAI message/schema/model/token request, without authentication |
| `response.txt` | Exact returned model text for provisional or abstained results |
| `quarantined-response.txt` | Exact invalid output; no repaired substitute |
| `report.json` | Status, hashes, model/response/request IDs, usage, validation and errors |
| `candidates.json` | E1 batch only when all candidates pass; includes actual extraction-run metadata |

Statuses are `provisional`, `abstained`, `quarantined`, `refused`, and
`provider_error`. Refused/incomplete/failed transport results do not create candidate
files. Provider error bodies and credentials are not copied into reports; HTTP
status and safe error codes are retained. Invalid batches are quarantined as a
whole, with no partial acceptance or retry. Existing directories are never replaced.

Mechanical acceptance does not assess entailment, generality, or scientific truth.
Free text can still contain overgeneralization or instance-specific claims. Every
accepted batch requires human review and remains provisional; no physical robots,
world states, execution episodes, ontology individuals or unconditional axioms are
instantiated by this software.

## Validation and next step

Offline tests cover both profiles, real-SDK serialization via mocked HTTP, strict
schema adaptation, provenance forgery, epistemic violations, source-injection
boundaries, exact raw artifacts, refusal, truncation, missing credentials, sanitized
errors, optional-dependency isolation and CLI exit codes. Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python verify_resources.py
.venv/bin/makf doctor
.venv/bin/python -m pip check
```

Recorded results with the optional SDK installed: **110 tests passed** (77 prior
tests and 33 provider/runner tests), no skips; **44/44 resources verified**;
doctor, both action validators and dependency consistency checks passed. The
updated reusable installation script was exercised successfully. A built wheel
also ran both fixture pipelines outside the checkout with the OpenAI import
disabled. Original ontology files and canonical E1 resources remain unchanged.

Live evidence and current validation outcomes are recorded in [current progress](CURRENT_PROGRESS.md). OpenAI authentication is verified. Transport v2 requests evidence IDs from a caller-derived catalogue of complete passages and source lines, with null offsets. After wire validation the runner resolves IDs to exact source text and validates canonical E1. Raw response and the catalogue are retained; unknown IDs and wrong attribution fail validation. E1 still supports verified offsets from other providers. This targets short excerpts; large documents need a separate chunking and schema-size design. See the [candidate review](experiments/e23_pouring/REVIEW.md) for coverage annotations and remaining scientific failures. No output is repaired after generation.

The user-requested order is preserved: first run and review the genuine OpenAI
experiment, **then** evaluate OntoGPT against the same source and checks. No OntoGPT
backend evaluation or recommendation has been made while the live run is blocked.

API references consulted: the [official OpenAI Python SDK](https://github.com/openai/openai-python)
and [Structured Outputs cookbook](https://github.com/openai/openai-cookbook/blob/main/examples/Structured_Outputs_Intro.ipynb).

## Optional quality review

The CLI now supports `--review-model`, `--revise-once` and `--select-reviewed`. See [quality review](QUALITY_REVIEW.md) for the bounded workflow, separate artifacts, explicit subset semantics, live results and limitations. Default single-call behavior is unchanged.
