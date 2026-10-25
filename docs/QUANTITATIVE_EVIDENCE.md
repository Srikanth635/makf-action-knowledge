# Quantitative simulation evidence 0.1

The first quantitative evidence contract and offline validator are implemented.
It stores source-backed scalar configuration/results, preserves numeric spelling,
checks units and derivations, and reports unresolved conditions. It is separate
from E1 candidate descriptions. Quantitative RDF export is now implemented as
described below; simulator execution remains a later increment.

## Use

```bash
makf validate-quantitative fluidlab
makf validate-quantitative path/to/evidence.json
```

The bundled FluidLab fixture represents the four saved annex records as ten atomic
quantities: one **observed** particle budget, six material parameters and three
runtime settings. They are published simulation reports, not locally reproduced
runs. The schema and self-contained fixture ship as package resources:

- `src/makf_knowledge/resources/quantitative/schema.json`
- `src/makf_knowledge/resources/quantitative/fluidlab.json`

Python callers can use `makf_knowledge.quantitative.validate_quantitative(data)`.
It returns a report without changing its input. Use the existing strict JSON reader
`makf_knowledge.publication.read_json(path)` to reject duplicate keys and non-finite
JSON numbers. Invalid structure, evidence or derivations raise `ValidationError`.

## Contract

| Field | Meaning |
| --- | --- |
| schema_version | Exact version `0.1`; additional/unknown fields are rejected |
| study | Source/version, published/local simulation origin, simulator/version status, declared context, transcription method, pending review |
| artifacts | Exact source text, SHA-256 and locator; no network fetch occurs |
| quantities | Stable local ID, annex record ID, kind, subject, role, original numeric text, unit status and exact anchors |
| conversions | Separate input-linked unit-conversion derivation and expected decimal value |
| timing_checks | Explicit references to a reported step, substep count and substep duration |
| issues | Source-attributed material/context/code questions linked to affected quantities |

Version 0.1 accepts **scalar** numeric strings, preserving source spellings such as
`2e-3`, `0.0` and `277.78`. Decimal arithmetic avoids binary floating-point rounding.
Finite values have bounded length/exponents. Ranges, time series, arbitrary formulas,
uncertainty distributions and physical-experiment origins are not supported yet.
They must not be encoded as invented scalar summaries. Large trajectories remain
external artifacts for a future artifact-reference contract.

All source hashes are checked. Each quote must occur verbatim in its artifact;
reported numeric spelling and any supplied unit text must occur in the cited quotes.
Counts must be nonnegative integers, integration counts/time durations positive,
and fraction metrics require a definition/denominator and a valid known-unit range.
Duplicate identifiers, dangling references, fake quotes and extra approval fields
fail validation. Simulator version is either explicitly supplied or marked unreported.

These mechanical checks do not establish that a quoted number was assigned to the
right table column, that a source assertion is true, or that two kinds of particles
are interchangeable. The fixture retains table headers, row labels and appendix
context for review. In particular, `observed_particle_count` and
`total_particle_count` are distinct kinds; no conversion between them is provided.
Semantic transcription and subject/column selection still need review.

## Units and conversion

Unit statuses are `explicit`, `dimensionless`, `simulation_units`, `unreported`,
and `unresolved`. Unknown/unreported units cannot carry a made-up symbol. A missing
unit cannot be relabeled dimensionless without cited source support. Explicit and
simulation units retain their source wording. This initial conversion registry
supports seconds/milliseconds, counts and fraction/percentage representations only.
Known symbols must agree with the actual cited labels: `seconds` cannot silently
be mapped to `ms`. Unrecognized explicit units can be archived but are not accepted
for conversion by this bounded registry.

A conversion records `input_id`, `target_unit`, `derived_value_text`, a separate ID
and `method=unit_conversion_v1`. The validator recomputes the value and rejects an
incorrect result, incompatible dimensions or unknown input scales. For example,
`2e-3` s converts to `2` ms while preserving the original reported value. Six
FluidLab material parameters have unreported units and cannot be converted to SI.
Lamé μ is not automatically dynamic viscosity. QUDT mappings and fluid-property
unit conversions remain future verified registry work.

## Eligibility and conflicts

Validation success means the evidence can be stored with its issues; CLI exit code
0 does not mean a usable simulator configuration. The report exposes:

- `storage_eligible`: true only after structural and numeric checks pass.
- `unit_conversion_eligible`: the quantity has a supported, source-grounded unit.
  A valid conversion can still be made for a source value in a conflicting study.
- `comparison_ready`: numeric/unit/context prerequisites only. Requires declared
  complete context and no applicable issues. It does **not** approve comparison to
  arbitrary studies or establish compatible controllers, materials or geometries.
- `execution_eligible`: always false in this archival contract version. There is
  no executable-configuration validator; callers cannot inject this flag as input.

The FluidLab report retains all ten quantities and emits missing-unit issues,
material-model ambiguity, incomplete context and a computed timing conflict:
`10 × 1e-4 s = 0.0010 s`, whereas the source reports `2e-3 s`. Both reported and
calculated values are retained. No source value is silently corrected.

The report is saved in
`docs/experiments/corpus_expansion_001/quantitative-validation.json`.
Storage passes; comparison and execution are blocked. Review remains pending.
Source/code matching is needed before resolving the material and timing issues.

## Next implementation

1. Define pairwise comparison policies with structured material, geometry,
   controller, boundary-condition and metric context; a declared complete flag is
   insufficient for scientific compatibility.
2. Add verified quantity-kind/unit mappings (including QUDT identifiers), reference
   scales for nondimensional models and preserved conversion provenance.
3. Implement the quantitative RDF vocabulary and SHACL shapes alongside E1, linked
   to specific claim versions. Do not promote unknown-unit values to physical laws.
4. Check FluidLab's versioned implementation and retain auditable resolutions of
   the source/code issues. A reproducible execution profile is a separate contract.

See [original design sequence](QUANTITATIVE_SIMULATION_PLAN.md). The first storage/
validation milestone is implemented; no live GPT calls are needed to verify decimal
arithmetic, unit dimensions, hashes and schema rules.

## Verified checks

The full regression run passed 223 tests. The final quantitative-only run passed
30 tests, including two signed-value/precision cases added after that full run
started. All 48 resource hashes passed. A rebuilt installed wheel loaded the
packaged schema/fixture, validated all ten quantities and rejected a sign-changing
transcription outside the source checkout. Test logs remain at
`/workspace/makf-quantitative-tests.log`.

## Quantitative RDF increment

`makf export-quantitative-rdf` now exports provisional records behind the `rdf` extra:

```bash
makf export-quantitative-rdf fluidlab \
  --base-iri https://example.org/makf/data/ --out-dir /tmp/makf-quantitative-rdf
```

Use a new output directory. Python callers use
`makf_knowledge.quantitative_rdf.export_quantitative(data, base_iri=...)` and save
its `PublicationResult`. The existing no-overwrite/manifest completion protocol is
reused. Input scalar validation, serialization roundtrip, JSON/RDF fidelity checks
and SHACL run before output creation.

The illustrative vocabulary is `https://example.org/makf/quantitative/0.1#`.
It represents Snapshot, Study, Quantity, UnitDeclaration, Artifact, Anchor, Issue,
TimingCalculation and Conversion records. Original numeric text and queryable
xsd:decimal values are separate. A numeric density parameter without units does
not become an SI density. No physical action instances or ontology axioms are added.

One named graph contains the snapshot. Every record includes canonical JSON;
the snapshot also retains the complete input JSON, including contextual fields
and original issue/derivation specifications. Quantity/evidence/unit/issue/input
relationships are explicit RDF links. Source-code observations can be stored as
additional artifacts and issues without overwriting published quantities.

`validate_quantitative_rdf` requires the manifest's one graph, recomputes scalar
validation/identity and rebuilds the expected mapping before SHACL. This rejects
altered values, units, eligibility, missing issue links, invented quotes and extra
/default graphs. Hashes are integrity checks, not signatures or reviewer identity.
It does not authenticate arbitrary imported JSON, prove source entailment or approve
execution. Original and calculated values remain separate; no conflict is repaired
by export.

The bundle contains `dataset.trig`, `evidence.json`, `validation.json`,
`shacl-report.ttl` and `manifest.json`, including input/report/resource/artifact
hashes. Graph identifiers bind the input and computed report; identical inputs
produce identical graph content. TriG formatting is not canonical.

Study/quantity records share the source bibliography with E1 descriptions. Explicit
curated links to specific E1 claim versions, QUDT mappings and collection-wide
comparison policies remain future increments. No inferred claim association is
introduced by this exporter.

The [versioned FluidLab audit](experiments/fluidlab_code_audit_001/README.md) now
records code-versus-paper findings and an additional annotated RDF snapshot. It
partly explains timing/material issues, but exact experiment provenance and SI
reference scales remain unresolved.
