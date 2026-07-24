# Repository Instructions

## Scope and product boundaries

- This repository is a hackathon proof of concept using synthetic data.
- Preserve the deterministic offline demo path. The application must remain usable without an
  LLM API or enterprise connection.
- Human review and confirmation are mandatory. Never represent provider output as formal
  architecture approval.
- Do not add real Confluence, Teams, Azure DevOps, AIF/LLM, database, authentication, RAG, or
  agent-framework functionality unless the user explicitly expands the task.
- Never add secrets, credentials, or real confidential company data.

## Project conventions

- Use Python 3.12 and `uv`.
- Keep `pyproject.toml` as the dependency and tool configuration source and retain `uv.lock`.
- Do not create `requirements.txt` or other manually maintained dependency lists.
- Keep reusable application code under `src/architecture_governance_copilot/`.
- Keep Pydantic models strict and evidence traceable.
- Keep provider-specific behavior behind the existing `SolutionIntentDrafter` and
  `GovernanceExtractor` boundaries.
- Keep review analysis separate from output generation so human edits occur before outputs.
- Preserve the synthetic fixtures in `samples/` as the deterministic contract; update fixtures
  and their validation tests together.

## Streamlit structure

- `app.py` owns the shared Streamlit shell and stage renderers.
- `pages/` files are thin route entry points used by `st.switch_page()`; do not treat them as
  disposable duplicates.
- Shared workflow state, fingerprints, reset behavior, and reviewed-result reconstruction belong
  in `src/architecture_governance_copilot/ui_support.py`.
- When changing stage or state behavior, add or update focused tests in `tests/test_app.py` and
  `tests/test_ui_support.py`.

## Verification

Use these commands from the repository root:

```bash
uv sync
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```

Run tests and both Ruff checks after application changes. Run `git diff --check` before handoff.

## Repository hygiene

- Do not commit `.env` files, virtual environments, caches, browser automation state, raw voice
  recordings, generated working audio, or local output directories.
- Treat new large videos, recordings, and generated presentation binaries as external
  deliverables unless the user explicitly asks to version them.
- Existing tracked media under `video/` is historical repository state. Do not rewrite Git
  history, force-push, migrate to Git LFS, or delete the package without explicit approval.
- Keep application changes separate from video-production changes when practical.

## Current implementation caveat

The deterministic providers support only the bundled synthetic scenario. Do not describe them as
general semantic extraction or drafting. A materially edited SI will not match the deterministic
review fixture; arbitrary-input support requires a future approved provider.
