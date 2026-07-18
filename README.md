# Architecture Governance Copilot

Architecture Governance Copilot is a hackathon proof of concept for reviewing a Solution Intent
(SI). It combines synthetic SI content, a synthetic Domain Architecture review transcript, and
basic review metadata to propose a structured, source-backed record for one review round.

A human Domain Architect remains responsible for reviewing, editing, and approving the record.
Only the approved state will generate standardized review minutes and mock Azure DevOps outputs.
The final deliverable is a video shorter than four minutes, due on 22 July 2026.

## Business problem

A Solution Intent is the project's detailed design document, covering areas such as conceptual
and detailed design, deployment, resilience, security, observability, and data. Product Owners
and development teams maintain it while a Domain Architect reviews it over one or more rounds.

Findings, decisions, risks, actions, and questions are often spread across the SI, review
meetings, and governance tracking. Turning those sources into a traceable review record manually
is slow, and findings can lose their SI-section context or supporting evidence.

## Proposed solution

The planned Solution Intent Review Copilot will:

1. load one bundled synthetic SI;
2. load one matching synthetic Teams-style review transcript;
3. combine both sources with review-round metadata;
4. display the outcome, findings, decisions, risks, actions, open questions, and missing
   information;
5. identify supporting evidence as either SI or transcript evidence;
6. map findings to SI sections where possible;
7. let a Domain Architect edit, remove, and approve the proposed record; and
8. generate a structured review record, review minutes, and mock ADO updates from the approved
   state.

The MVP demonstrates one review round only. It does not compare SI versions, persist review
history, resolve findings automatically, or implement a multi-round workflow.

## Planned architecture

```text
Synthetic SI + synthetic transcript + review metadata
                         |
                         v
                    Streamlit UI
                         |
                         v
                 Governance service
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
Extractor provider                 Pydantic models
  - deterministic default            - review context
  - optional LLM later               - findings and evidence
                                      - decisions, risks, actions
        |                                 |
        +----------------+----------------+
                         |
             +-----------+-----------+
             v                       v
       Review minutes          Mock ADO outputs
```

The deterministic extractor is the required offline demo path. It validates the bundled
SI/transcript pair and review metadata, then returns an independent copy of the known structured
result. It supports only this frozen synthetic scenario and does not perform semantic extraction
of arbitrary text. Pure deterministic generators now transform a validated result into Markdown
review minutes and typed mock ADO action work items. `GovernanceReviewService` intentionally
keeps analysis separate from output generation so a later UI can place human review and editing
between them. Streamlit session state will eventually hold the current one-round review state;
there is no database.

Confluence, Microsoft Teams, and Azure DevOps are production integration targets only. This PoC
does not connect to them.

See [SPEC.md](SPEC.md) for the complete domain and technical design and [DEMO.md](DEMO.md) for
the planned recording flow.

## Repository structure

```text
architecture-governance-copilot/
├── app.py
├── pyproject.toml
├── uv.lock
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
│   ├── solution_intent.md
│   ├── review_metadata.json
│   ├── review_transcript.txt
│   └── expected_result.json
└── tests/
    ├── test_models.py
    ├── test_sample_data.py
    ├── test_extractors.py
    ├── test_minutes_generator.py
    └── test_ado_generator.py
```

The samples freeze one fully synthetic Digital Payment Notification Service review scenario.
Automated tests validate its metadata, model compatibility, evidence quotes, scenario
cardinality, and basic data safety.

## Setup and commands

Prerequisites:

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/)

Synchronize the environment:

```bash
uv sync
```

Run the planned Streamlit application:

```bash
uv run streamlit run app.py
```

Run tests:

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

The model tests and quality commands work at the current stage. The Streamlit command is the
planned run command, but the application entry point remains a placeholder and does not yet
provide the review workflow.

## Current implementation status

**Domain models, synthetic demo dataset, deterministic extractor, output generators, and
governance-service orchestration complete; UI workflow not implemented.**

Implemented:

- strict Pydantic models for one SI review round;
- SI lifecycle and review outcome enums;
- typed SI/transcript evidence;
- Solution Intent review metadata;
- SI-section-aware review findings;
- existing decisions, risks, actions, questions, and missing-information models;
- enriched mock ADO work-item preview fields;
- comprehensive model validation tests;
- a 1,136-word synthetic Solution Intent and 32-line matching review transcript;
- validated review metadata, expected governance result, and evidence-consistency tests;
- a synchronous `GovernanceExtractor` protocol; and
- a fixture-validated `DeterministicDemoExtractor` for offline tests and demo fallback;
- deterministic Markdown SI review-minutes generation; and
- typed mock ADO work-item generation with no external request;
- an immutable `GovernanceOutputs` bundle; and
- `GovernanceReviewService`, with separate analysis and reviewed-result generation stages.

Not yet implemented:

- real LLM extraction;
- parent ADO governance-ticket update generation;
- Streamlit input, review, approval, or output UI;
- external integrations; or
- any multi-round workflow behavior.

The deterministic provider supports only the bundled synthetic sample; it does not claim to
analyze arbitrary documents. Mock ADO work items are local preview models and are never submitted
to Azure DevOps. The service does not approve or edit records: the future UI must explicitly
place human review between analysis and output generation. The next proposed phase is the
Streamlit UI. A real LLM provider remains an optional later phase.

## PoC and data statement

This is a hackathon PoC using synthetic data only. It must contain no real internal SI,
confidential architecture information, meeting transcript, personal data, secret, or API
credential. It is not production-ready and does not provide live Confluence, Microsoft Teams,
or Azure DevOps connectivity.
