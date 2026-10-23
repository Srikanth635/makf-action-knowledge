# E2.1/E2.2: ontology-guided prompt construction

This document records the prompt-construction milestone. E2.3 now adds a separate
[provider and validation runner](E2_PROVIDER_INTERFACE.md); the prompt API remains local.

This milestone prepares extraction requests locally. It does not generate candidate
knowledge, contact a provider, parse model output or implement quarantine. Both
pouring and grasping use the same API and policy with their packaged profiles.

## Python API

```python
from makf_knowledge import (
    ExtractionRequest, SourceDocument, SourcePassage, build_extraction_prompt,
)

# Invented illustrative text, NOT a scientific quotation or citation.
source = SourceDocument(
    document_id="synthetic-example",
    title="Synthetic illustrative paragraph (NOT scientific evidence)",
    synthetic_demo=True,
    passages=(SourcePassage(
        passage_id="paragraph-1",
        text="Under suitable conditions, changing a container's orientation may initiate outflow.",
    ),),
)
request = ExtractionRequest(
    batch_id="synthetic-batch",
    documents=(source,),
    profile="pouring",  # also "grasping" or a local profile YAML path
    perspectives=("causal", "epistemic", "applicability"),
)
prompt = build_extraction_prompt(request)
artifact = prompt.to_dict()  # JSON-serializable messages + response_schema + audit identifiers
```

`SourceDocument` requires source identity, title, an explicit synthetic flag, and
passages. URI, DOI and passage locator are optional and are copied only if supplied.
The API accepts multiple documents and passages. Passage IDs are unique within a
document; document IDs are unique across the request. Source strings retain their
original whitespace, line endings and Unicode, including combining characters.
Empty/whitespace-only required text, duplicate IDs, malformed profiles, undeclared
focus classes, action/frame mismatches and invalid perspective choices raise
`ValidationError`. The caller controls source identity; these checks do not
authenticate bibliographic claims.

`ExtractionPrompt` contains `prompt_version`, `source_sha256`, two role-separated
messages, and `response_schema`. `to_dict()` returns a detached copy. The digest is
SHA-256 over the UTF-8 JSON serialization of source documents, with sorted object
keys, no extra separators' whitespace, and unescaped Unicode. Array order is kept.
It identifies the exact metadata/text snapshot, not the truth of its contents.
There are no timestamps, random IDs or network lookups during construction.

`ExtractionProvider.generate(prompt) -> str` defines the E2.3 transport boundary.
Future adapters must consume **both** role-separated messages and the response
schema and return raw text. Construction never selects or invokes an adapter.
There are no new dependencies, provider SDKs or API-key requirements in E2.1/E2.2.

## CLI example

From the repository with the prepared virtual environment:

```bash
cat > /tmp/makf-synthetic.txt <<'TEXT'
Under suitable conditions, changing a container's orientation may initiate outflow.
TEXT
.venv/bin/makf prompt --profile pouring \
  --text-file /tmp/makf-synthetic.txt \
  --source-id synthetic-example \
  --source-title 'Synthetic illustrative paragraph (NOT scientific evidence)' \
  --batch-id synthetic-batch --passage-id paragraph-1 --synthetic-demo \
  --perspective causal --perspective epistemic --perspective applicability \
  --out /tmp/makf-prompt.json
```

Without `--out`, the artifact is printed to stdout. It includes the entire supplied
source text. `--source-uri`, `--doi` and `--locator` record known metadata; omit
unknown information. Omit `--perspective` to include all perspectives in the
profile. This is a prompt artifact, not an E1 extraction result, so do not pass it
to `makf validate`. Use the E2.3 `makf extract` command for an explicitly selected provider.

## Ontology selection and epistemic policy

The existing E1 validator loads the active local CRAM–AICOR, DUL alignment, MAKF,
pouring and grasping modules. Profile action/frame and focus classes are checked
against these declarations. The prompt contains only selected focus classes (at
most eight unique classes per perspective), a small shared MAKF description-class
set, and relevant allowed properties with their direct named domains/ranges.
Overlarge focus lists fail rather than being silently truncated. Class parents
and named existential restrictions are sorted; blank-node identifiers and recursive
ontology expansion are omitted. Output is deterministic across process hash seeds.
The source action profiles are configuration; their free-text notes are not used
as prompt instructions. Action vocabulary is not hard-coded into the prompt policy.

The shared classes include hypothesis, strategy, applicability and predicted-effect
descriptions. This allows a compact profile to express a qualified hypothesis
without inventing an action-specific class. Unmapped notions must use E1's
`needs_mapping` plus a note, or cause abstention. Parent and filler IRIs are only
references; they are not automatically offered as declared grounding classes.

The policy keeps E1 `knowledge_kind`, `epistemic_status`, `derivation_mode`,
`evidence_status`, and `modality` separate. It requires exact source anchors,
applicability conditions and possible-effect links for hypotheses, and a strategy
link for strategy hypotheses. LLM proposals/inferences use motivating quotes as
`context_only`, remain `not_assessed`, and retain qualified modality. An invented
idea cannot be attributed to the source or promoted to an established physical law.
All candidates remain provisional. Concrete robots, scenes, world states and
physical action occurrences are excluded; no ontology individuals are created.

## E1 compatibility and abstention

The response schema is copied from the canonical E1 LinkML subset compiler. E1
resources and the semantic validator are unchanged. The copied response schema
binds batch/profile/action/frame and document records to the request using `const`,
and narrows candidate perspectives to the selected subset. A provider cannot
replace the source text in a schema-valid response to make a fabricated quote
appear supported. All original epistemic enums remain intact.

E1's required candidate array has `minItems: 1`. Rather than relaxing E1 or requiring
a fabricated candidate, the **response** schema adds a separate alternative:

```json
{"abstained": true, "reason": "No supported generalized claim in this excerpt."}
```

This object is not an E1 batch. E2.4 must handle it separately; candidate responses
must still pass the original E1 semantic validator. Empty candidate batches remain
invalid. The schema is standard JSON Schema 2020-12, not a promise of compatibility
with every vendor's restricted structured-output dialect. E2.3 must test adapters
and retain local validation if a vendor cannot enforce these constraints.

## Trust boundary and remaining work

The system message is static. Every source field, including titles and IDs, appears
only in the JSON-encoded user message and request-bound response schema. Embedded
role markers, delimiters, tool requests and attempts to rewrite epistemic status
remain source data; they cannot create additional messages or alter system policy.
The tests verify this structural boundary. They do not prove that a future model
will obey the policy or resist every injection attempt.

The E2.3 provider module now supplies an offline fixture provider and optional
OpenAI adapter configured deliberately by the user. Its companion runner parses
output, checks the request-bound schema, verifies original source identity,
runs E1 semantic validation, and quarantines failures.
Prompt instructions are not a semantic enforcement mechanism. Existing E1 checks
verify mechanical quotations and structural relations; they do not establish
scientific entailment, truth, or the absence of world-specific claims in free text.
Generated extraction-run metadata must be recorded from actual execution by the
caller. No source ingestion, remote DUL resolution, full OWL reasoning, RDF
population, SHACL, TigerGraph or OntoGPT integration was added.

## Validation results

Baseline before implementation: **39 tests passed**, **44/44 resources verified**,
and `makf doctor` passed for both synthetic action examples.

Final validation on Python 3.12:

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | **77 passed** (39 existing + 38 new), no skips or expected failures |
| `.venv/bin/python verify_resources.py` | **44/44** bundled resources verified |
| `.venv/bin/makf doctor` | **PASS**, including pouring and grasping synthetic E1 validation |
| Documented Python and CLI examples above | **PASS** |
| Wheel build and installation to a separate directory | **PASS** |
| Wheel imported from outside checkout | Both prompt profiles, E1 validators, packaged resources and CLI **passed** using the prepared runtime dependencies |
| `git diff --check` | **PASS** |

New coverage includes vocabulary selection, custom profile limits, exact Unicode
and CRLF preservation, multiple sources, source-bound schema constraints,
abstention, unchanged epistemic enums, five prompt-injection payloads, malformed
requests/profiles, duplicate IDs, unknown classes/perspectives, mismatched action
frames, world-model field rejection, offline construction and determinism across
processes. The original ontology files, E1 resources and dependency declarations
have no changes. No live model behavior was tested.
