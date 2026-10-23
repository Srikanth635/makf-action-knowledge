# MAKF Action Knowledge — installable research package

**Development stage:** P1.1 → P1.2 → P1.3 → E1. **Not E2.** This package provides a reproducible, **offline-first** foundation for ontology-guided extraction of world-model-agnostic, generalized, stereotypical and hypothetical action knowledge.

It contains the **unaltered original** AICOR and CRAM–AICOR Turtle ontologies, latest modular MAKF and pouring/grasping frames, a tentative DUL alignment, source inventories, the E1 LinkML extraction contract, synthetic examples, validators, tests, and historical source files. No robot/scene/execution instances are added.

## Codex Cloud setup

This repository is prepared for Codex Cloud development. Read [Codex setup](docs/CODEX_CLOUD_SETUP.md), [agent instructions](AGENTS.md), and [development handoff](docs/CODEX_HANDOFF.md) before starting E2. Do not make the repository public without verifying licenses of user-provided ontologies.

## Install and test

Python 3.10+ required (3.11/3.12 recommended). On Linux/macOS:

```bash
unzip makf_action_knowledge_package.zip
cd makf_action_knowledge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
makf doctor
python -m pytest -q
```

On Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
makf doctor
python -m pytest -q
```

If a `makf` console script is not on your PATH, use `python -m makf_knowledge` instead.

## Useful commands

```bash
makf status
makf ontologies
makf class paf:PouringKnowledgeFrame
makf class makf:ActingHypothesis
makf inventory
makf validate pouring --profile pouring
makf validate grasping --profile grasping
makf guidance --profile pouring --out /tmp/pouring_guidance.json
makf schema --out /tmp/makf_extraction.schema.json
```

To validate your own **E1 candidate JSON**: `makf validate path/to/candidates.json --profile pouring`. The CLI checks structure, ontology term declarations, relations, quotation exactness, and epistemic metadata. The bundled examples are **synthetic**, not scientific evidence.

## Architecture

```
DUL (declared external import; not bundled)
  └── Local DUL alignment (tentative)
        └── AICOR / CRAM–AICOR active merged vocabulary
              └── MAKF core, generalized action perspectives
                    ├── Pouring action frame
                    └── Grasping smoke-test frame
                          ⇣
                E1 LinkML contract and validators
                          ⇣
             Provisional action knowledge candidates
                          ⇣
                 E2 extraction (FUTURE)
```

**This is a conceptual dependency illustration, not a literal one-to-one OWL import chain:** the DUL bridge directly imports active CRAM–AICOR and external DUL; MAKF imports the bridge; pouring/grasping import MAKF. The original AICOR and expanded CRAM–AICOR share an ontology IRI; the expanded file is the active import target and the base is preserved for comparison only. A single OWL reasoner should not load both as separate definitions for that ontology IRI.

## Directory structure

```text
src/makf_knowledge/
  cli.py                Command-line entry point
  ontology.py           Direct OWL class/restriction inspection
  validation.py         E1 structural + semantic validator
  guidance.py           Action-specific ontology context generation
  schema.py             Minimal offline LinkML-subset JSON Schema compiler
  paths.py              Bundled assets
  resources/
    ontology/           Original and refactored Turtle ontologies
    schema/             LinkML YAML and generated JSON Schema
    profiles/           Pouring and grasping extraction profiles
    examples/           Synthetic extraction batches
    inventory/          P1.1 original report and full CSV indexes
    reports/            P1.3 and E1 original validation reports
    config/             Local ontology IRI catalog (DUL unresolved)
    legacy/p1_2/        Prior version of pouring module and utilities
docs/                   Original stage documentation and competency questions
historical_sources/     Original scripts, preserved for inspection
 tests/                 Package regression tests
```

## Boundaries and known limitations

- No live LLM extraction, OntoGPT adapter, TigerGraph server/client integration, RDF populated action-descriptions, SHACL execution, or execution/world-model pipeline. Those are E2/E3/later.
- Official **DUL is NOT bundled**. Its OWL import is declared but not resolved or certified. Local RDFLib loading deliberately parses local files only. No OWL DL consistency check has been run.
- E1's LinkML YAML is compiled with a documented **limited subset** converter; official LinkML validation/lint is still outstanding.
- Exact-quote validation is mechanical and **does not prove** a scientific claim is supported or true. Hypotheses remain provisional. All included example passages are artificial.
- The knowledge inventory is a **precomputed reference** from the supplied ontologies, not an automatic continuously updated ontology analysis tool.
- `makf class` returns direct asserted restrictions, **not inferred OWL knowledge**.
- DUL-alignment mappings are proposals and require a formal reasoner review before production use.
- Check [LICENSE-STATUS.md](LICENSE-STATUS.md) before redistributing the user-provided ontology files.

## Development stages

| Stage | Included | State |
|---|---|---|
| P1.1 | Complete pouring-related class/property inventory | Completed analytical inventory |
| P1.2 | Original multiperspective pouring frame | Preserved in legacy directory |
| P1.3 | MAKF core and refactored pouring frame; grasping test | Active modules |
| E1 | LinkML contract, ontology profiles, synthetics, validation suite | Active module |
| E2 | LLM-driven extraction from real literature | Not implemented |

See `docs/` for extensive prior design decisions and source provenance.
