# Packaging validation — 2026-10-23

- Python interpreter in build environment: Python 3.13.5 (the project declares Python >=3.10; other versions were not directly tested here).
- Local editable install via `pip install -e . --no-deps --no-build-isolation`: **PASS**.
- Non-editable wheel creation using setuptools: **PASS**.
- Installed-wheel test outside source tree: **PASS**, including original AICOR resource and `makf doctor`. For this isolated smoke test, existing build-environment dependencies were put on the import path; a standalone fresh environment would normally install the declared dependencies through pip.
- Offline `makf doctor`: **PASS** for pouring and grasping synthetic extraction batches.
- `python -m pytest -q`: **39 passed** (E1 extraction contract + package API + asserted ontology layer checks).
- Bundled SHA-256 resource integrity: **44/44**.
- DUL remote import closure / full description-logic reasoning: **NOT TESTED**.
- Official LinkML CLI validation: **NOT TESTED**.
- Live OntoGPT/OpenAI/TigerGraph integration: **NOT IMPLEMENTED**, so not tested.
