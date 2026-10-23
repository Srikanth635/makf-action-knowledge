# MAKF Action Knowledge — installable research package

**Development stage:** P1.1 → P1.2 → P1.3 → E1 → **E2.3 optional OpenAI extraction adapter**. A live scientific pilot is prepared but awaiting credentials. This package provides a reproducible, **offline-first** foundation for ontology-guided extraction of world-model-agnostic, generalized, stereotypical and hypothetical action knowledge.

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

`makf prompt` prepares a provider-neutral prompt and response schema from a supplied
UTF-8 excerpt, source metadata, and either action profile. It runs locally and makes
no model calls. See [E2 prompt interface](docs/E2_PROMPT_INTERFACE.md) for the Python
API, a runnable synthetic example, provenance constraints, and validation results.

`makf extract --provider openai --model ...` performs one explicitly configured
model call, validates the response against the original request and E1 semantics,
and saves provisional candidates or quarantined output. Install the optional SDK
with `python -m pip install -e '.[dev,openai]'`; the baseline needs no SDK or key.
See [provider interface](docs/E2_PROVIDER_INTERFACE.md) and the
[scientific pilot record](docs/experiments/e23_pouring/README.md).

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
                 E2.1/E2.2 request + prompt interface
                          ⇣
                 E2.3 optional provider + validation/quarantine runner
```

**This is a conceptual dependency illustration, not a literal one-to-one OWL import chain:** the DUL bridge directly imports active CRAM–AICOR and external DUL; MAKF imports the bridge; pouring/grasping import MAKF. The original AICOR and expanded CRAM–AICOR share an ontology IRI; the expanded file is the active import target and the base is preserved for comparison only. A single OWL reasoner should not load both as separate definitions for that ontology IRI.

## Directory structure

```text
src/makf_knowledge/
  cli.py                Command-line entry point
  ontology.py           Direct OWL class/restriction inspection
  validation.py         E1 structural + semantic validator
  guidance.py           Action-specific ontology context generation
  extraction.py         E2 request/provider interfaces and deterministic prompt builder
  providers.py          Optional OpenAI and offline fixture transports
  pipeline.py           Request-bound validation, audit artifacts and quarantine
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

- OpenAI transport is implemented and tested offline, including through the real SDK with a mocked HTTP transport. Live scientific extraction has not yet run because credentials are unavailable. No OntoGPT adapter, TigerGraph integration, RDF population, SHACL or execution/world-model pipeline is implemented.
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
| E2.1/E2.2 | Extraction interface and ontology-guided prompt construction | Implemented offline |
| E2.3 | Optional OpenAI adapter, fixture transport, validated local run artifacts | Implemented; offline tests pass |
| E2.4/E2.5 | Scientific pilot and evaluation | Minimal validation/quarantine runner implemented; live pilot blocked on credentials |

See `docs/` for extensive prior design decisions and source provenance.
