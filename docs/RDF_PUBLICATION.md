# Local RDF publication snapshots

`makf export-rdf` implements the first E3 exporter. It accepts canonical E1 JSON,
runs the existing schema and local-ontology validator, maps descriptions to RDF,
and validates the resulting source/candidate snapshot with packaged SHACL shapes.
It makes no model calls, fetches no sources and resolves no remote ontology imports.
The vocabulary remains [draft 0.1](design/publication-v0.1/CONTRACT.md).

## Install and export

```bash
python -m pip install -e '.[dev,rdf]'
makf export-rdf grasping --profile grasping \
  --base-iri https://example.org/makf/data/ \
  --out-dir /tmp/makf-grasping-rdf
```

This command uses the explicitly synthetic grasping example. Use a new output
directory for every export; existing bundles are never overwritten. The data base
is required and configurable. The example.org value is illustrative, never fetched
or registered. Ontology and publication vocabulary IRIs retain their contract values.

To export your own batch without attaching a review decision:

```bash
makf export-rdf path/to/candidates.json --profile pouring \
  --base-iri https://example.org/makf/data/ \
  --out-dir /tmp/makf-candidates-rdf
```

Every claim receives a system-recorded `pending` review state. A reviewer note,
source evidence or extraction success does not grant a model or human decision.
The input's epistemic and evidence labels are preserved; they are not certified.

## Preserve an E2 model selection

For an E2 run with explicit subset selection, supply both its selection manifest
and the full original batch that the model reviewed:

```bash
makf export-rdf path/to/run/selection/candidates.json --profile pouring \
  --selection-file path/to/run/selection/report.json \
  --reviewed-batch path/to/run/candidates.json \
  --base-iri https://example.org/makf/data/ \
  --out-dir /tmp/makf-selected-rdf
```

If selection followed a revision, these paths are inside that revision directory.
The exporter checks the original batch digest, the selected/withheld ID partition,
and equality of the entire selected subset, including its source and run metadata.
Only then does it record `model_selected_provisional`. Model decisions remain
advisory: a digest binds supplied content, not reviewer identity or scientific truth.
No option accepts or fabricates human approval. That requires a future authenticated
curation workflow.

The saved PourIt! experiment is reproducible without external run directories:

```python
from makf_knowledge.publication import export_batch, read_json

root = "docs/experiments/e23_pouring/"
result = export_batch(
    read_json(root + "quality-selected.json"),
    profile="pouring",
    base_iri="https://example.org/makf/data/",
    selection=read_json(root + "quality-evaluation.json")["selection"],
    reviewed_batch=read_json(root + "quality-reviewed.json"),
)
result.save("/tmp/makf-pourit-rdf")
```

`quality-reviewed.json` is the unchanged full revision batch from experiment 014.
Its digest matches the existing selection manifest. It retains withheld candidates
as audit input; only the selected candidate appears in the exported RDF.

## Bundle and validation boundaries

| File | Purpose |
| --- | --- |
| dataset.trig | Source and candidate named graphs, with exact evidence and provisional review records |
| candidates.json | Exact JSON values supplied for export; canonical whitespace/key ordering |
| assessment.json | Supplied model selection or explicit system pending record |
| reviewed-batch.json | Full original batch when attaching a selection; includes withheld audit records |
| validation.json | E1 result, warnings and SHACL conformance |
| shacl-report.ttl | Machine-readable SHACL report |
| manifest.json | Completion marker; graph IRIs, review state, counts, input/assessment digests, artifact hashes, dependency versions and schema/ontology/shape resource hashes |

All validation and serialization checks happen before creating the output directory.
Writes use a new private directory; `manifest.json` is installed atomically last.
Consumers must ignore directories without that marker and verify artifact hashes
before use. A failed write is cleaned up; an interrupted process may leave an
incomplete directory without a manifest. This is a local bundle completion protocol,
not a database transaction or a guarantee of durability after power loss.

Identical inputs produce identical record identifiers and graph content. TriG
formatting/order is not canonical; file hashes describe the actual saved bytes.
Review changes create a new candidate snapshot but preserve claim identity when
the candidate and sources are unchanged. Claim identity currently includes all
source snapshots in its batch, as specified in draft 0.1; adding an unrelated source
may therefore change claim IRIs. Cross-batch canonical identity is future curation
work. Timestamp RDF literals use datatype normalization; the exact submitted
timestamp spelling remains in `candidates.json`.

E1 checks ontology declarations, profile compatibility, local subclass membership,
predicate domains/ranges, evidence spans and hypothesis structure. Expanded SHACL
checks record cardinalities, enum values, nonblank required strings, source backlinks,
exact evidence and offset bounds, hypothesis condition/effect/strategy links,
generated-claim qualification and review-role separation. Validation uses precisely
the two named graphs in the manifest and rejects additional/default-graph data or
records moved across source/candidate graph boundaries. OWL inference is disabled.
`validate_dataset` checks RDF structure only; it does not replace `export_batch`'s
E1/profile checks and cannot authenticate arbitrary imported RDF or reviews.

Optional source fields and unmapped components are preserved. A proposed mapping is
an IRI reference, not an assertion that a physical action occurred. Relations between
components remain reified descriptions. Synthetic sources stay marked synthetic.
Two source records do not establish independent corroboration; the E1 warning is
retained in the bundle.

## Query the saved snapshot

The [strategy query](design/publication-v0.1/queries.rq) returns source, quote,
review state and mapping gaps. Bind its graph variables to the manifest:

```python
from pathlib import Path
from rdflib import Dataset, URIRef
from makf_knowledge.publication import read_json

bundle = Path("/tmp/makf-pourit-rdf")
manifest = read_json(bundle / "manifest.json")
dataset = Dataset().parse(bundle / "dataset.trig", format="trig")
query = Path("docs/design/publication-v0.1/queries.rq").read_text()
rows = list(dataset.query(query, initBindings={
    "candidateGraph": URIRef(manifest["candidates_graph"]),
    "sourcesGraph": URIRef(manifest["sources_graph"]),
}))
```

This query explicitly inspects model-selected provisional claims and excludes
synthetic sources. It returns one PourIt! strategy and its mapping gap. Changing the
review filter to `human_approved` returns no rows. Pending exports need a `pending`
filter; do not remove the review policy accidentally when building applications.

## Remaining work

This local exporter is an implemented E3 increment. Production promotion still
requires domain review of the semantic contract, ontology/DUL foundations, an
independent extraction evaluation, authenticated human decisions and a graph-store
transaction/retrieval policy. SHACL does not establish full source entailment,
scientific truth, source authenticity, or formal OWL consistency. OntoGPT and
TigerGraph remain unimplemented.

Run `python -m pytest -q` with the `rdf` extra installed to exercise export checks.
Without the extra, RDF-dependent tests skip and missing-dependency handling remains
tested; the default extraction and ontology tools still work offline.
