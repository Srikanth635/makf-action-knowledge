# Publish MAKF privately to GitHub and run it in Codex Cloud

## 1. Prepare a GitHub repository
This archive contains a local Git repository with a clean initial commit (branch `main`). The intended destination is a **new private repository**, e.g. `Srikanth635/makf-action-knowledge`. The connected account may not have it yet. Do NOT push this project's original ontologies to a public repository without reviewing permissions.

Option A — GitHub CLI already authenticated locally:
```bash
gh repo create Srikanth635/makf-action-knowledge --private --source=. --remote=origin --push
```
Option B — create an empty **private** repository at https://github.com/new (do not pre-create README), then from this folder:
```bash
git remote add origin https://github.com/Srikanth635/makf-action-knowledge.git
git push -u origin main
```
If GitHub authentication requires it, sign in through Git Credential Manager or GitHub CLI. Never store tokens in source files.

## 2. Create a Codex Cloud environment
Current official procedure: https://learn.chatgpt.com/docs/environments/cloud-environments

1. In ChatGPT web or desktop, choose **Work in > Cloud > Select environment > Create environment** (or Settings > Codex Cloud > Environments > Create environment).
2. Connect GitHub if asked; select `Srikanth635/makf-action-knowledge`.
3. Ask Codex to prepare Python 3.12, then run `bash scripts/setup_codex.sh` as its install script if automatic setup does not suffice.
4. Verify `.venv/bin/python -m pytest -q`, `.venv/bin/python verify_resources.py`, `.venv/bin/makf doctor`. No network data services or API secrets are required for the baseline.
5. Choose **Only me** under environment privacy. Review the setup report, **Publish**, and start a task.

## 3. Example first task
See `docs/FIRST_CODEX_TASK.md` and paste its instruction into the new Codex task. Read `AGENTS.md` and `docs/CODEX_HANDOFF.md` before starting.

## 4. Later model-provider configuration
For E2, configure an API key through Codex Cloud's environment variables / network secrets controls; allow only the provider domains needed. Do not commit secrets. Live tests must remain opt-in. The baseline is offline and requires no keys.

## Caveats
- Codex Cloud environments are not part of this Git checkout; publishing the environment requires the user's authorized UI action.
- Original AICOR/CRAM–AICOR licenses are not globally assigned; keep the repo private by default.
- The official DUL import is declared but not downloaded or fully reasoned over.
