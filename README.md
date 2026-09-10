# Architecture Governance Copilot

Document role: `CURRENT_PRODUCT_DESCRIPTION`. Current behavior is determined by the checked-out Git
revision, application code, tests, and synchronized maintained documentation. Roadmap language and
historical records do not independently authorize implementation.

Architecture Governance Copilot is a hackathon proof of concept for drafting and reviewing a
Solution Intent (SI). Its first workflow stage turns a synthetic SI template, selected
source-code context, and supporting notes into an editable SI draft. The confirmed draft then
enters the review workflow with a synthetic Domain Architecture review transcript and basic
review metadata. Users who already have an SI can explicitly skip drafting.

A human Domain Architect remains responsible for reviewing, editing, and making the formal
governance decision. Only a validated, human-confirmed reviewed record generates standardized
review minutes and mock Azure DevOps outputs.
The submission baseline supports the video and repository deliverables due on 14 September 2026.

## Business problem

A Solution Intent is the project's detailed design document, covering areas such as conceptual
and detailed design, deployment, resilience, security, observability, and data. Product Owners
and development teams maintain it while a Domain Architect reviews it over one or more rounds.

Findings, decisions, risks, actions, and questions are often spread across the SI, review
meetings, and governance tracking. Turning those sources into a traceable review record manually
is slow, and findings can lose their SI-section context or supporting evidence.

## Proposed solution

The implemented deterministic Solution Intent Copilot can:

1. open a synthetic project workspace and let the user inspect and select its SI template,
   repository context, supporting evidence, and governance metadata;
2. confirm that source package and generate a known SI draft behind a provider interface;
3. let a human edit and confirm that draft before it enters governance review;
4. load review transcript and metadata without replacing the confirmed SI;
5. alternatively load one complete bundled synthetic review package;
6. analyze both review sources with the deterministic fixture-backed extractor;
7. display the outcome, findings, decisions, risks, actions, open questions, and missing
   information;
8. identify supporting evidence as either SI or transcript evidence;
9. map findings to SI sections where supported;
10. let a reviewer edit fields and exclude proposed items while evidence remains read-only; and
11. validate the human-reviewed record before generating Markdown minutes and mock ADO action
   work items.

The UI presents one consistent five-stage route hierarchy: **Project Context → Draft Solution
Intent → Review Inputs → Human Review → Generated Outputs**. Project Context is the default
starting page. **Use Existing Solution Intent** moves directly to Review Inputs and marks both
context selection and drafting as skipped.
Analysis navigates to `/human-review`, and review confirmation navigates to
`/generated-outputs`. Browser history and Back actions therefore behave like page navigation
while shared session state preserves the current draft and review.

The MVP demonstrates one review round only. It does not compare SI versions, persist review
history, resolve findings automatically, or implement a multi-round workflow.

## Architecture

```text
Synthetic template + source context + supporting notes
                         |
                         v
             SI drafting provider/service
                         |
                         v
              Editable SI draft → Human confirm
                         |
                         v
Confirmed SI + synthetic transcript + review metadata
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
  - opt-in internal fake              - findings and evidence
                                      - decisions, risks, actions
        |                                 |
        +----------------+----------------+
                         |
             +-----------+-----------+
             v                       v
       Review minutes          Mock ADO previews
                                      |
                           guarded fake Create
```

The deterministic extractor is the required offline demo path. It validates the bundled
SI/transcript pair and review metadata, then returns an independent copy of the known structured
result. It supports only this frozen synthetic scenario and does not perform semantic extraction
of arbitrary text. Pure deterministic generators now transform a validated result into Markdown
review minutes and typed mock ADO action work items. `GovernanceReviewService` intentionally
keeps analysis separate from output generation so the Streamlit UI can place human review and
editing between them. Explicit session state holds only the current one-round inputs, analysis,
reviewed record, generated outputs, stale-input fingerprint, and active route stage; there is no
database.

An opt-in internal fake mode exercises Confluence read, AIF analysis, and guarded ADO Create
contracts entirely in memory without network access. It is an integration-development aid, not
evidence of live enterprise connectivity. Microsoft Teams ingestion and every real transport
remain deferred.

See [SPEC.md](SPEC.md) for the complete domain and technical design and [DEMO.md](DEMO.md) for
the planned recording flow.

## Repository structure

```text
architecture-governance-copilot/
├── app.py
├── pages/
│   ├── solution_intent_drafting.py
│   ├── review_inputs.py
│   ├── human_review.py
│   └── generated_outputs.py
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
│       ├── si_drafting.py
│       ├── ui_support.py
│       ├── minutes_generator.py
│       ├── ado_generator.py
│       ├── evidence_validation.py
│       ├── publication.py
│       ├── runtime_dependencies.py
│       └── integrations/
│           ├── confluence.py
│           ├── aif.py
│           └── azure_devops.py
├── samples/
│   ├── si_template.md
│   ├── source_context.txt
│   ├── supporting_context.md
│   ├── solution_intent.md
│   ├── review_metadata.json
│   ├── review_transcript.txt
│   └── expected_result.json
└── tests/
    ├── test_models.py
    ├── test_sample_data.py
    ├── test_extractors.py
    ├── test_governance_service.py
    ├── test_si_drafting.py
    ├── test_ui_support.py
    ├── test_app.py
    ├── test_minutes_generator.py
    ├── test_ado_generator.py
    ├── test_evidence_validation.py
    ├── test_confluence_integration.py
    ├── test_aif_integration.py
    ├── test_azure_devops_integration.py
    └── test_publication.py
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

Run the Streamlit application:

```bash
uv run streamlit run app.py
```

The PoC deliberately uses one project-level light theme. It remains light when the browser or
operating system prefers Dark mode; there is no supported in-app theme switch. Dark-mode support
may be reconsidered only as a separately approved future refinement.

The local demo uses a 0.4-second pause for each visible processing phase, producing an
approximately 0.8-second transition after SI confirmation and 1.2-second transitions after
Analyze and reviewed-record confirmation. To rehearse with a different per-phase delay:

```bash
AGC_DEMO_STEP_DELAY_SECONDS=0.6 uv run streamlit run app.py
```

Use `AGC_DEMO_STEP_DELAY_SECONDS=0` to disable transition pauses.

The deterministic offline path is the required submission path and needs no environment
configuration. To exercise the explicitly labelled, no-network integration fakes during
development:

```bash
AGC_INTERNAL_FAKE_ENABLED=1 uv run streamlit run app.py
```

This flag enables only in-memory fakes. It does not accept credentials or connect to Confluence,
AIF, Microsoft Teams, or Azure DevOps.

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

The primary guided flow is: **Open Demonstration Project → inspect/select sources → Confirm
Context & Continue → Generate SI Draft → human edit/confirm → Load Sample Transcript & Metadata
→ Analyze Review → edit or exclude items → Confirm Reviewed Record & Generate Outputs**.

The existing-SI shortcut is: **Use Existing Solution Intent → Load Sample Review → Analyze
Review**.
The application is fixture-backed and supports only the bundled synthetic drafting and review
scenario. Human edits are preserved into Stage 2, but the current deterministic review extractor
can analyze only the unchanged bundled SI; arbitrary edited SI analysis requires a future
approved provider.

## Current implementation status

**The deterministic routed PoC workflow is the verified 14 September submission baseline.**

Implemented:

- strict SI-drafting request/result models and a `SolutionIntentDrafter` provider protocol;
- a deterministic offline drafter for the bundled template, source excerpts, and supporting
  notes;
- a production-shaped Project Context stage with explicit source selection and simulated local
  source statuses;
- a first-class routed drafting stage with editable human confirmation;
- direct handoff of the confirmed SI to Review Inputs;
- transcript-and-metadata loading that preserves the confirmed SI;
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
- `GovernanceReviewService`, with separate analysis and reviewed-result generation stages;
- one consistent five-stage route hierarchy, durable state, and
  stale-analysis protection;
- one deliberate project-level light theme for consistent native and branded surfaces;
- editable human review with item exclusion, a normalized change summary, and read-only evidence;
- exact source-quote and supported-locator validation before Human Review;
- unified input, mode, source-version, and provider-identity invalidation;
- an evidence-to-output comparison joining source quotes, the confirmed action, its minutes entry,
  and its generated ADO preview;
- rendered/raw Markdown output and Azure DevOps work-item preview cards; and
- an explicit completed-workflow panel with artifact counts and a safe **Start New Review**
  reset; and
- pure UI-support tests plus Streamlit `AppTest` workflow coverage;
- fake-only Confluence, AIF, and ADO boundaries with recoverable error contracts; and
- an exact ADO JSON Patch preview, separate confirmation, correlation lookup, single fake Create,
  GET verification, duplicate protection, and unknown-result handling.

Not yet implemented:

- general-purpose drafting from arbitrary repositories or documents;
- source repository cloning, scanning, or code execution;
- real Confluence retrieval or SI publication;
- a production enterprise LLM drafting provider;
- real AIF/LLM extraction;
- real ADO authentication or Create;
- Microsoft Teams or Graph ingestion;
- parent ADO governance-ticket update generation;
- Confluence review-page write-back; or
- any multi-round workflow behavior.

The deterministic drafting and review providers support only the bundled synthetic scenario;
they do not claim to draft from arbitrary repositories or analyze arbitrary documents. Offline
ADO work items remain local previews. Internal fake mode can submit one preview to an in-memory
gateway only; it never reaches Azure DevOps. The UI confirms a draft for review handoff and later
confirms a reviewed record for output generation; neither action formally approves the Solution
Intent or replaces the Domain Architect.

**Reset semantics:** Reset and Start New Review clear local workflow inputs, analysis,
confirmation, previews, and outputs. Publication operations that may identify a remote result are
retained for reconciliation within the current session. Restarting the process is not evidence
that an attempted remote Create did not happen. The current fake gateway is in memory and is not a
durable audit store.

Release gates at freeze: G1 offline **passed**; G2 external preparation with fakes and documented
adapter contracts **passed**; G3 internal live acceptance **not run**. Conditional I9 writes are
therefore deferred and no secondary-write controls are exposed. See
[`docs/INTERNAL_INTEGRATION_HANDOFF.md`](docs/INTERNAL_INTEGRATION_HANDOFF.md) for the bounded live
acceptance sequence.

## PoC and data statement

This is a hackathon PoC using synthetic data only. It must contain no real internal SI,
confidential architecture information, meeting transcript, personal data, secret, or API
credential. It is not production-ready and does not provide live Confluence, Microsoft Teams,
or Azure DevOps connectivity. The opt-in fakes make no network request and do not change this
statement.
