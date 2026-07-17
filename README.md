# Architecture Governance Copilot

Architecture Governance Copilot is a short hackathon proof of concept for turning a synthetic
Microsoft Teams-style architecture review transcript into a source-backed governance record.
A human reviewer will be able to correct and approve the record before the application generates
standardized meeting minutes and mock Azure DevOps work-item payloads.

The final deliverable is a video shorter than four minutes, due on 22 July 2026. The goal is one
reliable end-to-end workflow, not a production platform.

## Business problem

Architecture governance meetings produce decisions, risks, actions, open questions, and requests
for evidence. Manually converting the conversation into a consistent record takes time, and the
result can lose ownership, deadlines, or traceability to the source discussion.

## Proposed solution

The planned Streamlit application will:

1. load one bundled synthetic Teams-style transcript;
2. analyze it through a provider interface with an offline deterministic provider as the
   reliable default;
3. display the review outcome, decisions, risks, action items, open questions, and missing
   evidence with source quotes or transcript references;
4. let a human edit, remove, and explicitly approve the proposed record; and
5. generate standardized Markdown minutes and mock ADO work-item JSON from the approved data.

No real Teams, Confluence, or Azure DevOps integration is planned for the MVP.

## Planned architecture

```text
Streamlit UI
    -> Governance service
        -> Extractor provider interface
            -> Deterministic fixture-backed provider (required)
            -> Optional real LLM provider (not on the demo critical path)
        -> Pydantic governance models
        -> Markdown minutes generator
        -> Mock ADO work-item generator
```

Streamlit session state will hold the current transcript, reviewed data, approval state, and
generated outputs. There is no database. The extraction interface will keep all LLM-specific
behavior outside the core workflow, and the application will remain usable without an LLM API.

See [SPEC.md](SPEC.md) for the model and architecture proposal and [DEMO.md](DEMO.md) for the
recording workflow.

## Repository structure

```text
architecture-governance-copilot/
├── app.py
├── pyproject.toml
├── README.md
├── SPEC.md
├── DEMO.md
├── .gitignore
├── src/
│   └── architecture_governance_copilot/
│       ├── __init__.py
│       ├── models.py
│       ├── extractors.py
│       ├── governance_service.py
│       ├── minutes_generator.py
│       └── ado_generator.py
├── samples/
│   ├── review_transcript.txt
│   └── expected_result.json
└── tests/
    ├── test_models.py
    ├── test_minutes_generator.py
    └── test_ado_generator.py
```

## Planned local setup and commands

Prerequisites:

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/)

Install the declared project and development dependencies:

```bash
uv sync
```

Run the planned Streamlit application:

```bash
uv run streamlit run app.py
```

Run the planned automated tests:

```bash
uv run pytest
```

Run lint checks:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

These are the intended project commands. **They are not yet claimed to provide a working
application or meaningful test suite:** dependencies have not been installed in the
initialization task, source files are placeholders, and the functional implementation has not
started. `uv.lock` will be created and maintained by `uv`, not edited manually.

## Current implementation status

**Planning and initialization only.**

At this stage:

- the src-based package skeleton and placeholder tests exist;
- `pyproject.toml` declares the planned runtime and development dependencies;
- the product, technical, implementation, and demo plans are documented;
- the transcript and expected-result files are placeholders; and
- there is no Streamlit UI, model implementation, extraction, generation, service
  orchestration, real LLM call, or functional automated test.

The next proposed task is phase 1 from `SPEC.md`: implement the Pydantic models and their
validation tests, but only after the planning output is reviewed and approved.

## PoC and data statement

This repository is a hackathon PoC using synthetic data only. It must not contain company-
confidential information, real meeting transcripts, personal data, secrets, or API credentials.
It is not production-ready and does not provide live Microsoft Teams, Confluence, or Azure
DevOps connectivity.
