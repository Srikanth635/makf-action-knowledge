# Quantitative simulation evidence: proposed first milestone

Status: original design following E1 0.2 calibration. The first scalar storage and
validation milestone is implemented; quantitative RDF promotion remains pending.
The FluidLab annex is the first acceptance fixture; unresolved units and
inconsistencies are preserved.

Implementation update: the [scalar contract and validator](QUANTITATIVE_EVIDENCE.md)
now complete the first archival milestone: four annex records, ten quantities,
explicit missing units and timing/material issues. Quantitative RDF, broader units
and executable configuration validation remain pending. The sequence below retains
the original design scope.

## Representation

Add a versioned quantitative evidence contract alongside E1 candidate descriptions.
E1 captures what a source says about an action; quantitative evidence captures a
reported configuration, a result or an explicitly derived quantity. Link evidence
to the relevant claim version without making numbers into action ontology axioms.
Concrete simulation trajectories stay in artifact storage; the generalized graph
contains study metadata, qualified findings and references to those artifacts.

Use these records:

| Record | Required meaning |
| --- | --- |
| Study/source | Evidence origin: published simulation, locally executed simulation, physical experiment or analytical calculation; bibliography/artifact identity and review state |
| Model/configuration | Simulator name and available version/commit; fluid/constitutive model; geometry, gravity, boundary conditions and control assumptions when reported |
| Quantity | Role (input/configuration/output), quantity kind, subject/material, reported value and unit status, scope and evidence anchor |
| Result summary | Metric definition, denominator, conditions, aggregation/sample count and uncertainty when supplied |
| Derivation | Formula, input quantity IDs, conversion/reference scales, method/version and clearly marked derived value |
| Issue | Missing units, conflicting settings, model ambiguity, source/code mismatch or unsupported conversion; affected records and resolution provenance |

Missing information is explicit, not guessed. Do not require fabricated simulator
versions, uncertainty estimates or sample counts to store a published record.
These may block comparison or execution while still permitting archival storage.

## Values and units

Preserve `reported_value_text` (e.g. "0.8"), a parsed decimal where appropriate,
and a `unit_status`: `explicit`, `dimensionless`, `simulation_units`, `unreported`
or `unresolved`. Absence of a unit does not mean dimensionless. Preserve symbols and
source unit spelling before canonicalization.

Use QUDT quantity/unit identifiers where a verified mapping exists, without requiring
remote imports. A normalized value needs a compatible quantity kind, an established
unit conversion and a separate derivation record. Nondimensional parameters require
reference scales before physical-unit conversion. The μ and λ in FluidLab's table
are labeled Lamé parameters; do not reinterpret μ as dynamic viscosity.

A proposal illustrating the known light-liquid parameter:

```json
{
  "record_id": "fluidlab-light-liquid-density-reported",
  "record_kind": "configuration_quantity",
  "quantity_kind": "reported_density_parameter",
  "subject_label": "Light Liquid in Pouring",
  "reported_value_text": "0.8",
  "parsed_decimal": "0.8",
  "unit_status": "unreported",
  "evidence_origin": "published_simulation",
  "source_ref": "xian-etal-fluidlab-arxiv-2303.02346v1",
  "evidence_ref": "fluidlab-table-4-light-liquid-row",
  "review_state": "pending",
  "eligible_for_unit_conversion": false
}
```

This example is a design illustration, not a validated production record. The
complete contract must resolve `evidence_ref` to an immutable text/table artifact
with exact quote, locator, hash and relevant row/column labels.

## Validation and use policies

Separate three decisions: structurally valid for storage, comparable under stated
conditions, and suitable for executing a simulator configuration. Missing units may
pass storage validation but fail comparison and execution. Never treat passing
SHACL, a model-selected claim, or a paper's presence as scientific approval.

First checks should include:

- Finite numeric values and valid scalar/range/series structure. Preserve decimal
  precision; reject NaN/infinity. Require ordered ranges and positive time steps.
- Explicit unit status; reject invented canonical units and conversions without
  compatible dimensions or required reference scales.
- Metric definitions: particle counts versus observed particle budgets, volume
  versus mass fractions, and fractions versus percentages. A success fraction needs
  its denominator; 500 observed particles must not become 500 total particles.
- Time consistency: store FluidLab's reported 0.002 s step, 10 substeps and 0.0001 s
  substep separately. Flag that 10 × 0.0001 = 0.001 s, retaining all reported values.
  An inconsistent source configuration cannot be marked executable without resolution.
- Context: material model, geometry, boundary conditions, controller and evaluation
  regime when reported. Missing/conflicting context blocks unjustified comparisons.
- Provenance: source quote/artifact hash, paper/code version when known, extraction
  or transcription method, and separately attributed arithmetic/derived results.
- Review and evidence origin: published simulation is distinct from a simulation
  reproduced here and from a physical measurement. Qualitative reported comparisons
  must not acquire invented numerical effect sizes or uncertainty estimates.

## Implementation sequence

1. **Freeze a small contract and fixtures.** Split the four annex records into
   atomic quantities and contextual records. Preserve table rows/headers and runtime
   quotes. Add synthetic adversarial fixtures for invented SI units, swapped observed/
   total particle counts, wrong timestep arithmetic and missing source anchors.
2. **Implement JSON Schema and semantic checks.** Keep original reported values
   immutable. Produce issue records and explicit storage/comparison/execution
   eligibility. Test known-good unit conversions independently from unknown-unit
   source records.
3. **Export evidence records to RDF.** Add a separate quantitative vocabulary/module
   and shapes; use QUDT/PROV references where verified. Link to E1 claims by stable
   version IRIs. Do not change original AICOR/CRAM–AICOR files or invent domain mappings.
4. **Check FluidLab against versioned code.** Identify the matching release/commit,
   reference scales, time integration and material implementations. Resolve or retain
   each issue with provenance; never silently overwrite the paper's report.
5. **Expand carefully.** Import more published simulation results, then consider
   reproducible local runs. Keep development fixtures separate from domain-reviewed
   held-out evaluation. Compare quantities only when units, metric definitions and
   relevant conditions are compatible.

Completion criterion for the first milestone: all four FluidLab annex records can
be stored with exact provenance; missing units remain missing; conflicting settings
are flagged; unsupported conversions fail; and no unresolved configuration is
presented as executable. Running a new fluid simulator is a later milestone.
