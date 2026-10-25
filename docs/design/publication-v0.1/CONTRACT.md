# E1 → RDF publication contract, draft 0.1

Status: reviewable design with a worked fixture and executable initial SHACL checks.
The subsequent [local exporter](../../RDF_PUBLICATION.md) implements this draft
with expanded checks. A production promotion service and graph database remain pending.
The example retains the real selected candidate as provisional. No live LLM calls
are needed for this work. Original ontologies and E1 files are unchanged.

## Representation and semantics

`pub:` denotes `https://example.org/makf/publication/0.1#`, a proposed publication
vocabulary; instance IRIs use `https://example.org/makf/data/`. Both bases are
illustrative and must be configured before production. MAKF/AICOR/DUL identifiers
retain their original IRIs. This vocabulary describes records, not physical events.

A `pub:Claim` stores one immutable candidate version, qualification and evidence.
A `pub:Component` stores one candidate-local component description. `pub:actionClass`,
`pub:frameClass` and `pub:groundedClass` are IRI references to ontology classes;
they are NOT rdf:type assertions that a claim is a physical action or that a
proposed component is a formally accepted domain individual. This avoids silently
asserting unverified ontology restrictions. Domain-typed projection is a later,
explicit policy after ontology review. No owl:sameAs is generated.

A `pub:StructuralLink` records subject component, predicate IRI and object component.
Preserve existing MAKF relation IRIs (e.g. hasApplicabilityCondition,
predictsPossibleEffect, concernsStrategy) in `pub:predicate`; do not materialize
unreviewed relation triples as established facts. Link endpoints must belong to
that claim. A generated hypothesis retains its hypothetical labels and source
support roles. Recording a possible effect never asserts that it occurred.

## Label decisions

These are normative meanings proposed for the publication contract. They clarify
E1 usage without changing E1 enum values, rewriting historical records or changing
model prompts in this task. Domain review of the definitions is still pending.

| Dimension | Meaning and boundary |
| --- | --- |
| knowledge_kind | Shape of knowledge: strategy description, definition, hypothesis, etc. Not a confidence level. |
| proposed_strategy | A provisionally represented strategy description. It does not assert novelty, empirical success or that the source authors invented it. A cited earlier method can use this label. |
| source_explicit / source_paraphrase | Whether the candidate directly expresses or paraphrases a source claim. Neither establishes truth. |
| conditional_principle | An explicitly conditional general relationship. One observed comparison does not establish a general principle; preserve source scope and distinguish attribution from validation. |
| stereotype / typical | A qualified typical pattern, not the default for any method described in one experiment. |
| hypothesis | A conditional possibility with required hypothesis/condition/effect structure, never an asserted physical law. Generated hypotheses use llm_inference/llm_proposal and not_assessed evidence. |
| source_anchored | A claim has source-attributed evidence, not proof of full entailment or independent corroboration. |
| conditional / possible | Conditional restricts applicability; possible expresses possibility. Neither means a probability estimate or review approval. |
| reported observation | A source-level finding. E1 0.1 lacked a neutral observation label; E1 0.2 now uses reported_observation for both knowledge kind and epistemic status, with source derivation. See [migration](../../E1_V02_MIGRATION.md). Historical fixture labels remain unchanged. |
| needs_mapping | The component meaning exists, but a defensible ontology grounding has not been established. Omit groundedClass and retain the explanation. |

Review is a separate axis: `pending`, `model_selected_provisional`, `withheld`,
`human_approved`, `human_rejected`. A `pub:Review` is append-only, identifies the
reviewer kind and assessment artifact, and targets a specific claim version.
A model cannot set human_approved. Approval records require a human reviewer and
an actual decision artifact; no human decision is fabricated in this fixture.
Approval to store a claim still does not certify empirical truth. Future promotion
must enforce reviewer authorization, not merely trust a supplied reviewerKind field.
SHACL can test structure but cannot authenticate the author of that record.

## Identity and updates

Canonical JSON is UTF-8 `json.dumps(value, sort_keys=True, ensure_ascii=False,
separators=(',', ':'), allow_nan=False)`. Hashes are full SHA-256 hex. Source text
is never whitespace- or Unicode-normalized. Review state is not part of claim
identity; changing a review must not change the underlying candidate.

| Entity | Identity input |
| --- | --- |
| Source snapshot | Complete E1 document object. This is the supplied metadata/passage snapshot, not a verified hash/version of the entire original PDF. |
| Passage | Source snapshot IRI plus the exact E1 passage object. |
| Claim version | Candidate object, profile_id, sorted source snapshot IRIs. |
| Component | Claim IRI and local component object. |
| Evidence anchor | Claim IRI and exact E1 source_support object. |
| Structural link | Claim IRI and exact E1 structural_links object. |
| Extraction run | Exact extraction_run object, when present. Absence is preserved. |
| Review record | Claim IRI and assessment artifact digest. |
| Named graph | Contract version plus full input batch; the candidate graph also includes the assessment digest so review changes create a new snapshot. Production partition/transaction policy remains open. |

IRIs have the form `{base}/{kind}/{digest}`. Identical inputs are idempotent. A
changed statement, component, quote or source snapshot creates a new version; it
does not overwrite an existing claim. Explicit verified lineage may use
prov:wasRevisionOf; do not guess lineage from similar wording. Repeated ingestion
with equivalent but differently segmented metadata is not automatically deduped.
Document-level canonical identity resolution (DOI, edition, extraction version)
is later curation work and must preserve the original snapshot.

Components are candidate-local by default. Reuse across sources requires a curated
canonical concept with an auditable matching decision; labels alone are inadequate.
Each paper keeps its own claim/evidence even if curated strategy identity is shared.
Different conditions do not automatically imply contradiction. Disagreements should
be qualified relations with provenance, not unconditional OWL negation.

## Field mapping

| E1 location | RDF mapping |
| --- | --- |
| batch_id, profile_id | pub:Batch / pub:batchId, pub:profileId; batch pub:claim and pub:document links |
| documents[] | pub:SourceSnapshot; pub:documentId, dct:title, pub:sourceURI, pub:doi, pub:syntheticDemo |
| passages[] | pub:Passage; pub:passageId, pub:text, pub:locator, pub:document; source pub:passage backlink |
| candidate_id | pub:Claim / pub:candidateId |
| action_class, frame_class | pub:actionClass and pub:frameClass, expanded IRIs; not rdf:type |
| perspectives[] | Repeated pub:perspective literals; preserve E1 enum values |
| statement | pub:statement verbatim |
| knowledge_kind, modality, epistemic_status | pub:knowledgeKind, pub:modality, pub:epistemicStatus |
| derivation_mode, evidence_status | pub:derivationMode, pub:evidenceStatus |
| components[] | pub:hasComponent → pub:Component; pub:componentId, pub:componentKind, pub:description |
| ontology_class, grounding_status, grounding_note | pub:groundedClass IRI, pub:groundingStatus, pub:groundingNote |
| structural_links[] | pub:structuralLink → pub:StructuralLink; pub:subjectComponent, pub:predicate, pub:objectComponent |
| source_support[] | pub:evidence → pub:EvidenceAnchor; pub:document, pub:passage, pub:exactQuote, pub:supportRole |
| start_char, end_char | Optional pub:startChar / pub:endChar, xsd:integer; both present or both absent, Unicode code-point offsets, end exclusive |
| reviewer_note | pub:reviewerNote verbatim; a note is not proof that a human reviewed it |
| extraction_run | pub:ExtractionRun (prov:Activity); pub:engine/modelName/promptVersion and pub:recordedAt; claim prov:wasGeneratedBy. Recording time is not assumed to be activity start time. |
| No E1 field: review | Explicit assessment sidecar → pub:Review; status/reviewerKind/artifactSha256/assesses. Never inferred from evidence_status or reviewer_note. |

RDF literals retain source bibliographic URI/DOI strings; no invented normalization
or HTTP fetch occurs. Exact class CURIE expansion uses the E1 prefix map. Optional
fields absent in E1 are absent in RDF; no blank strings, guessed IDs or null triples.
Array order is not semantic except candidate-local identifiers; ordering must be
explicitly modeled if a later application needs it.

## Trust and named graphs

The worked dataset has separate source and candidate graphs. Review provenance
lives with the candidate snapshot; the example contains only a model review record.
Queries explicitly name these graphs and return review state. Production consumers
must choose a review policy; a graph name or presence in storage is not approval.
Validate only the intended source/candidate snapshot closure, not an arbitrary union
of unrelated tenants, synthetic examples or historical claims. Publish atomically
only after E1 validation and RDF shape validation; quarantine failed snapshots.

## Initial validation scope and worked example

`worked-example.trig` is a fixture generated from `quality-selected.json`, not a
production exporter output. `build_example.py` is a local demonstration builder
that preserves the selected claim and the assessment manifest. `vocabulary.ttl`
declares the proposed record vocabulary; `shapes.ttl` checks core record cardinality,
enums, evidence linkage/quote inclusion, offset pairing, local link endpoints,
grounding state and separation of human/model review. `queries.rq` returns strategy,
source, review and mapping gaps without requiring every component to be grounded.

These initial shapes are not a complete substitute for E1 semantic validation,
OWL reasoning, entailment checking or authorization. They do not yet encode every
hypothesis graph rule, validate every grounded class against an ontology version,
verify source authenticity, or prove complete evidence coverage. Keep those checks
in the existing validator/review path and expand SHACL before production publishing.

Verified result: 61 quads across two named graphs; the baseline passes SHACL and
rebuilds with identical identifiers and graph content. Nineteen mutation checks
pass (one valid offset variant and eighteen invalid variants rejected). The scoped
query returns one provisional strategy with its source and mapping gap; the same
query restricted to human-approved records returns zero rows. The report is saved
in [validation-summary.json](validation-summary.json) and
[validation-report.ttl](validation-report.ttl). Checks run locally with no API calls.

The query runner binds `candidateGraph` and `sourcesGraph` from `manifest.json`.
Use those bindings when reusing `queries.rq`; executing it unbound searches every
matching named graph and does not provide the intended snapshot isolation.

Reproduce in an isolated validation environment:

```bash
python3 -m venv /workspace/.venvs/makf-rdf-design
/workspace/.venvs/makf-rdf-design/bin/python -m pip install -r docs/design/publication-v0.1/requirements.txt
/workspace/.venvs/makf-rdf-design/bin/python docs/design/publication-v0.1/build_example.py
/workspace/.venvs/makf-rdf-design/bin/python docs/design/publication-v0.1/validate_example.py
```

The configurable local exporter now uses this fixture as a contract test; see
[implementation and expanded validation](../../RDF_PUBLICATION.md). Ontology identity,
DUL reasoning, observation-label gaps and production namespace authorization remain
explicit prerequisites for production promotion.
