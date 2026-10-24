# Create a replacement cloud environment

The repository includes E2.1/E2.2 prompt construction, the optional E2.3 OpenAI
provider, offline tests, and the genuine PourIt! pilot passage and provenance.
The live scientific experiment and subsequent OntoGPT evaluation remain pending.
No API key is stored in Git.

1. Create a new cloud environment, for example `makf-action-knowledge-e2`.
2. Select `Srikanth635/makf-action-knowledge`, branch `main`. Keep environment
   access private / Only me. Keep the old environment until the new one works.
3. Use Python 3.12 and the setup script below. It assumes the standard checkout
   location `/workspace/makf-action-knowledge`.
4. Configure one secret requirement named `MAKF_OPENAI_API_KEY`, targeting an
   environment variable with the same name and HTTPS destination `api.openai.com`.
   Choose **Environment** for an environment-managed key and enter its value
   securely. If instead using Personal Vault, choose the personal/user-provided
   source and bind the existing vault entry. The requirement source must match.
   Never paste the key in chat, a script, or a repository file.
5. Allow `api.openai.com` in network settings. Keep the package-manager network
   preset enabled for dependency installation. The scientific passage is already
   in the repository, so the pilot does not need to download the paper again.
6. Save the settings successfully, then publish the new environment. Use a single
   settings editor to avoid conflicting unsaved revisions.
7. Start a new task using that environment and paste the continuation prompt below.
   Delete the old environment only after the replacement has been verified.

## Setup script

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /workspace/makf-action-knowledge
export PIP_CACHE_DIR=/workspace/.cache/pip
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev,openai]'
.venv/bin/python -m pip check
.venv/bin/python verify_resources.py
.venv/bin/python -m pytest -q
.venv/bin/makf doctor
.venv/bin/makf validate pouring --profile pouring
.venv/bin/makf validate grasping --profile grasping
```

The same setup commands were verified in the original environment: 110 tests
passed and all 44 bundled resources verified. No live services or keys are
required for these checks. Tests of the OpenAI SDK use a mocked HTTP transport.

## Continuation prompt

> Read AGENTS.md, docs/CODEX_HANDOFF.md, docs/E2_PROVIDER_INTERFACE.md, and
> docs/experiments/e23_pouring/README.md. Use this existing checkout; cloud tasks
> are isolated, so do not create a Git worktree. Check the current environment's
> OpenAI credential and network readiness without printing secret values. Run the
> prepared bounded live OpenAI extraction on the genuine PourIt! passage, preserve
> raw output and audit artifacts, and assess exact citations, epistemic status,
> generalization and perspective coverage. Only after that actual live experiment,
> evaluate OntoGPT as an alternative backend. Keep all candidates provisional and
> do not modify original ontologies or introduce physical world-model instances.

If credentials are still unavailable, inspect this new environment's runtime
metadata and binding names before requesting configuration changes. A saved
credential requirement without a value binding does not enable an API call.
