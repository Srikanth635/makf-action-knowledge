# Research and published-simulation expansion 001

This pilot expands the source corpus with **two papers and six exact passages**.
It also retains **four published simulation-configuration records** for curation.
It does not run a simulator, ingest raw simulation trajectories, or certify a
paper's results. All graph claims remain provisional.

## Sources and evidence

| Source | Version checked in PDF | Material captured |
| --- | --- | --- |
| [SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation](https://arxiv.org/abs/2011.07215v2) | arXiv v2, 8 March 2021 | PourWater controls/reward, fluid incompressibility model, pouring task variations |
| [FluidLab: A Differentiable Environment for Benchmarking Complex Fluid Manipulation](https://arxiv.org/abs/2303.02346v1) | arXiv v1, 4 March 2023; ICLR 2023 paper | Fine-grained pouring objective, reported trajectory-optimization comparisons, pouring loss; Tables 3–4 and runtime settings |

[source-catalog.json](source-catalog.json) records authors, PDF hashes, actual
retrieval URLs/times, document versions, extraction method and exact passage hashes
and offsets. Source JSON retains `synthetic_demo=false`: these are real published
sources even though their experiments use simulation. `evidence_origin` distinguishes
published simulation from locally executed experiments. No DOI was guessed.

PDFs and full extracted text remain outside the checkout at
`/workspace/makf-corpus-runs/expansion-001/`. The bounded excerpts in this directory
are contiguous slices of `pdftotext` output, preserving line breaks, page breaks
and extractor artifacts. No equations were silently repaired.

## Live extraction and review outcome

Model: `gpt-5.4-2026-03-05`. Each source had one extraction, one advisory review,
at most one revision, and a final review: eight calls in total, 52,862 input tokens
and 7,562 output tokens. This was a bounded corpus pilot, not an accuracy benchmark.
Raw prompts, responses, transport records and all intermediate reports are saved in
`/workspace/makf-corpus-runs/expansion-001/extraction/`.

| Source | Initial candidates | Revised candidates | Selected for provisional RDF | Held / omitted |
| --- | ---: | ---: | ---: | --- |
| SoftGym | 3 | 3 | 1 | 2 held for knowledge-kind/epistemic labeling |
| FluidLab | 3 | 2 | 0 | 2 held after review; 1 omitted by revision |

The selected SoftGym claim describes controlling the held cup with x/y displacement
and rotation in the reported PourWater benchmark. Its component remains
`needs_mapping`; no unsupported specialized ontology class was forced onto it.

The model struggled to distinguish a benchmark reward definition, a task objective,
reported observations and an actual strategy. The advisory reviewer also remains
imperfect: its FluidLab rationale treats `needs_mapping` as a reason to reject a
mapping, although the contract intentionally permits unresolved mappings. These
holds are not scientific refutations. Original and revised output are retained
unchanged; there is no retry-until-pass or fabricated human approval.

[experiment-results.json](experiment-results.json) records call metadata and counts.
`*-original.json`, `*-reviewed.json`, `*-original-review.json`, `*-review.json` and
`*-selection.json` preserve local audit inputs. Only SoftGym has a selected E1 batch.

## Published simulation settings

[simulation-evidence.json](simulation-evidence.json) contains four source-attributed
configuration records; Tables 3 and 4 were also checked visually on PDF page 15:

- Pouring observation budget: **500 observed particles per fluid body**, with
  rotational control around z. This is not the full simulator particle count.
- Light pouring liquid: reported density parameter **0.8**, with μ = 0 and λ = 277.78.
- Heavy pouring liquid: reported density parameter **1.5**, with μ = 0 and λ = 277.78.
- Runtime timing: the text reports a **0.002 s step**, **10 substeps** and
  **0.0001 s per substep**. Their arithmetic does not agree; the record is flagged.

The material table does not specify physical units; these values are not asserted
as SI measurements. Section 4.1 calls the pouring liquids non-Newtonian, while the
table lists them as Liquid with μ = 0. The relationship needs implementation/version
checking. These records are a research evidence annex, **not executable simulator
configuration or quantitative E1 knowledge**. Their units, provenance and modeling
uncertainties must be resolved before quantitative RDF integration.

## Expanded graph

`/workspace/makf-rdf-runs/research-expansion-001/` contains:

- `collection.trig`: **127 quads**, two source/candidate graph pairs and **two
  provisional claims**—the original PourIt! claim and the new SoftGym claim.
- `bundles/`: independently E1/SHACL-validated snapshots, preserving original IDs.
- `claims.rq` and `query-results.json`: source-qualified, review-filtered queries.
- `manifest.json`: graph-pair allowlist, hashes, evidence origins and FluidLab's
  explicit withheld-source entry. Consumers must ignore incomplete directories
  without this marker. This remains a file-based RDF collection, not a graph server.

The prior graph is preserved. Candidate IDs such as `cand-1` are local to their
batches; their content/source-bound RDF IRIs prevent a cross-paper overwrite.
Different papers are not automatically merged into a shared scientific assertion.
The numeric annex is stored separately and is not counted as four new graph claims.

The selected collection can answer which control descriptions the two papers
provide, where their exact evidence comes from, and which ontology mappings are
still open. The annex can support inspection of reported simulation settings. This
pilot cannot answer how changing viscosity changes spillage: it has no controlled
viscosity sweep or independently reproduced results.

## Reproduce

Offline assembly uses the saved source/review artifacts and needs the `rdf` extra:

```bash
.venv/bin/python docs/experiments/corpus_expansion_001/assemble_collection.py \
  --out-dir /tmp/makf-research-expansion
.venv/bin/python -m pytest tests/test_research_collection.py -q
```

Use a new output directory. The assembler validates every snapshot separately,
then preserves its named graphs in the collection; it does not validate an arbitrary
union of unrelated histories as one snapshot.

To explicitly repeat the live experiment (incurs model calls), use a new run path:

```bash
.venv/bin/python docs/experiments/corpus_expansion_001/extract_sources.py \
  --model gpt-5.4 --out-dir /tmp/makf-new-research-run
.venv/bin/python docs/experiments/corpus_expansion_001/review_sources.py \
  --model gpt-5.4 --run-dir /tmp/makf-new-research-run
```

These commands use the saved exact source JSON. `prepare_sources.py` can regenerate
those excerpts from the preserved PDF-text cache and `downloads.json`; it checks
version markers and the original download hashes. Repeating live calls does not
replace this pilot's saved selections or graph.

## Next work

1. Define benchmark/task descriptions and reported observations explicitly in the
   semantic contract, with positive/negative examples and a compatible migration.
   Fix review treatment of `needs_mapping` before scaling automated selection.
2. Resolve FluidLab's material units and timing from its versioned implementation;
   define a quantitative evidence schema with units, model assumptions, simulator
   version, parameters and links to published tables/artifacts.
3. Expand to 5–10 diverse pouring papers with reviewed annotations, including
   viscosity, geometry, spillage and control strategies. Keep held-out evaluation
   separate from these development passages.
4. After this evidence layer is established, consider importing published raw
   rollouts or running reproducible simulations as a separate, explicitly labeled
   evidence source. Preserve concrete simulation artifacts outside the generalized
   action-knowledge layer.

Validation for this increment: three new offline integrity/integration checks pass;
46/46 packaged resource hashes remain valid. No application code, ontology modules
or E1 schema were changed by this experiment.
