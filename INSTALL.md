# Quick local verification

1. Create a virtual environment and install: `python -m pip install -e ".[dev]"`.
2. Inspect the bundled knowledge: `makf ontologies` and `makf class paf:PouringKnowledgeFrame`.
3. Validate included demos: `makf doctor`.
4. Run regression tests: `python -m pytest -q`.
5. Export candidate guidance: `makf guidance --profile pouring --out guidance.json`.
6. Validate your JSON: `makf validate my_candidates.json --profile pouring`.

No network is used during commands, but pip may need to fetch Python dependencies. The DUL ontology import is **not resolved offline**, and no live LLM or TigerGraph server is included.

## Programmatic API

```python
from makf_knowledge import SemanticValidator, describe_class, build_context
from makf_knowledge.paths import profile_path, example_path
import json, yaml

v = SemanticValidator()
profile = yaml.safe_load(profile_path('pouring').read_text())
batch = json.loads(example_path('pouring').read_text())
print(v.validate_batch(batch, profile))
print(describe_class('paf:PouringKnowledgeFrame'))
print(build_context(profile_path('pouring'))['profile_id'])
```

## Verify bundle file integrity

`python verify_resources.py` checks the sha256 manifest for all bundled research resource files.
