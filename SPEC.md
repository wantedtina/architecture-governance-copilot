# Architecture Governance Copilot — Product and Technical Specification

## Document purpose

This document defines a hackathon proof of concept (PoC) for reviewing a Solution Intent (SI).
The final deliverable is a video shorter than four minutes, due on 22 July 2026. The PoC proves
one reliable, human-controlled SI review round; it is not a production platform.

## Domain context

A Solution Intent is the detailed project design document jointly prepared by the Product Owner
and development team. It normally covers conceptual and detailed design, deployment, resilience,
security, observability, data, and related architecture concerns. In the production process, the
SI is maintained in Confluence and has a corresponding Azure DevOps (ADO) governance ticket.

A Domain Architect reviews the SI over one or more rounds. A round may combine document review,
a meeting, written feedback, required changes, risks, decisions, and open questions. The project
team updates the SI until the Domain Architect approves it, often while software development
continues in parallel.

This PoC models one such review round. Confluence, Teams, and ADO are future production
integration targets; none is connected in the MVP.

## Problem statement

SI review information is split across a large design document, meeting discussion, and
governance tracking. Manually turning these sources into a consistent review record is slow and
error-prone. Findings can lose their SI-section context, actions can lack clear ownership, and
recorded conclusions may be difficult to trace back to the document or discussion that supports
them.

The PoC will show that one synthetic SI and one synthetic review transcript can be transformed
into a structured, evidence-backed review proposal. A human reviewer can correct that proposal
and explicitly approve the review record before minutes and mock ADO outputs are generated.
Formal approval remains the responsibility of the human Domain Architect.

## Target users

- **Primary:** Domain Architects who review Solution Intents and own the formal review outcome.
- **Secondary:** Product Owners and development teams who prepare and update the SI.
- **Secondary:** solution and enterprise architects who need traceable decisions, findings, and
  risks.
- **Secondary:** delivery leads and action owners who need follow-up work represented clearly.
- **Demo audience:** hackathon judges and stakeholders evaluating the usefulness of the workflow.

## Product goal

Given synthetic SI content, a synthetic Teams-style review transcript, and basic review
metadata, produce a structured proposal containing:

- the current review-round outcome;
- review findings mapped to SI sections where possible;
- confirmed architecture decisions;
- risks;
- actions, owners, due dates, and priorities;
- open questions;
- missing governance information; and
- supporting evidence from the SI or meeting transcript.

After human review and approval of the record, generate:

1. a structured SI review record;
2. standardized review meeting minutes; and
3. mock ADO governance-ticket updates and action work items.

Success means the deterministic demo completes this one-round workflow reliably. It does not
mean that the PoC can govern arbitrary projects or replace Domain Architect judgment.

## Core end-to-end user journey

1. Load synthetic SI content.
2. Load a synthetic review transcript.
3. Analyze the review using the SI, transcript, and review metadata.
4. Display the review outcome, findings, decisions, risks, actions, open questions, and missing
   information.
5. Show supporting SI or transcript evidence for each extracted claim.
6. Allow human review, editing, and removal of proposed items.
7. Let the Domain Architect explicitly approve the reviewed record.
8. Generate the structured review record, review minutes, and mock ADO outputs from the approved
   state.

The MVP performs this journey for one review round only. `review_round` metadata prepares the
record for future tracking, but the application will not compare versions, persist history, or
automatically carry findings between rounds.

## Functional requirements

### Inputs

- Provide a **Load Sample Solution Intent** action.
- Load synthetic SI content from `samples/solution_intent.md`.
- Display the SI in a readable multiline area.
- Provide a **Load Sample Review Transcript** action.
- Load a synthetic Teams-style Domain Architecture review transcript.
- Display the transcript in a separate multiline area.
- Collect or preload basic metadata:
  - project name;
  - SI title and version;
  - current SI status;
  - review-round number;
  - optional ADO governance-ticket ID;
  - optional Domain Architect; and
  - optional review date.
- Reject missing required input with clear feedback.
- Clearly label all content as synthetic.

### Analysis

- Hide analysis behind a small provider interface.
- Use a deterministic demo provider by default.
- Analyze SI content and the transcript together rather than treating the transcript as the
  primary object.
- Return a validated `GovernanceResult` for exactly one review round.
- Display these sections in a stable order:
  1. Review Outcome
  2. Review Findings
  3. Decisions
  4. Risks
  5. Action Items
  6. Open Questions
  7. Missing Information
- Map a finding to an SI section when the source supports that mapping.
- Do not invent a section, owner, date, or outcome.
- Show an explicit empty state when a category has no items.

### Evidence and traceability

- Every outcome other than `not_stated` must have evidence.
- Every finding, decision, risk, action, and open question must have at least one evidence item.
- Evidence must identify its source as `solution_intent` or `meeting_transcript`.
- SI evidence should show its section when available.
- Transcript evidence should show speaker and timestamp when available.
- Missing-information evidence may be empty because a checklist or document inspection can
  identify absence without a direct quote.
- Do not apply strict source-specific locator validation in the MVP.

### Human review and approval

- Allow the reviewer to edit meaningful extracted fields.
- Allow the reviewer to remove proposed list items.
- Keep supporting evidence visible during review.
- Treat evidence as traceability metadata rather than freeform text to casually rewrite.
- Prevent approval when the reviewed record fails validation.
- Require an explicit **Approve SI Review Record** action.
- Present formal approval as the human Domain Architect's responsibility.
- Generate outputs from the approved, edited state rather than the original provider response.
- Invalidate approval and outputs after reanalysis or subsequent edits.

### Approved outputs

- Generate outputs only after explicit human approval.
- Display a structured, JSON-serializable SI review record.
- Generate deterministic Markdown meeting minutes containing:
  - review context;
  - review outcome;
  - findings with SI sections;
  - decisions;
  - risks;
  - actions;
  - open questions;
  - missing information; and
  - evidence references.
- Generate a mock update for the parent ADO governance ticket.
- Generate one mock ADO action work item per approved action.
- Allow mock work items to include the parent ticket, SI section, and acceptance criteria.
- Clearly state that no payload is sent to Azure DevOps.

## Non-functional requirements

- **Reliability:** the bundled scenario must work offline without credentials or an LLM API.
- **Human accountability:** the system proposes a record; it does not approve the SI.
- **Traceability:** claims retain evidence source, quote, and available locator information.
- **Determinism:** stable inputs produce stable results and generated outputs.
- **Simplicity:** use direct Python modules, Pydantic, and Streamlit session state.
- **Testability:** models and pure transformations must be testable without Streamlit.
- **Readability:** the review and evidence must be legible during a short screen recording.
- **State safety:** stale approval and outputs must not survive changes to source or review data.
- **Data safety:** use synthetic data only and commit no secrets or confidential information.
- **Maintainability:** Python 3.12, modern type syntax, a src layout, concise public docstrings,
  pytest, and Ruff.
- **Dependency management:** use `pyproject.toml`, `uv`, and the generated `uv.lock`; do not use
  `requirements.txt`.
- **Accessibility:** use clear labels and do not rely on color alone to communicate state.

## Assumptions

- The demo runs locally with Python 3.12 and `uv`.
- One bundled SI and one matching transcript are sufficient for the recorded scenario.
- The SI may contain headings and plain text rather than production Confluence markup.
- The transcript contains synthetic speakers and timestamps or line references.
- The Domain Architect reviews and owns the final outcome.
- The ADO ticket identifier is metadata only.
- A single Streamlit session is sufficient; no durable state or concurrent use is required.
- The optional LLM provider is not required for the primary demo.

## Explicit MVP exclusions

- More than one active review round.
- SI version comparison or document diffing.
- Automatic resolution, reopening, or carry-forward of findings.
- Review history persistence or multi-round workflow logic.
- Database, audit-log storage, authentication, or authorization.
- Real Confluence access, page updates, identifiers, or URLs.
- Real Teams or Microsoft Graph transcript ingestion.
- Real ADO authentication, ticket updates, or work-item creation.
- RAG, embeddings, vector databases, or enterprise knowledge retrieval.
- Agent frameworks or autonomous workflows.
- File upload, bulk review, dashboards, analytics, and cross-project search.
- Production deployment, monitoring, scaling, support, or service-level objectives.
- Live audio transcription or meeting-bot behavior.
- Use of real company-confidential or personal data.

### Future extensions, not MVP commitments

- Persisted review history across multiple rounds.
- Comparison of SI versions and finding status across rounds.
- Confluence retrieval and publication.
- Teams transcript ingestion.
- Real ADO governance-ticket and action updates.

These extensions must not appear in the required demo path.

## Definition of Done

The PoC is done when:

- `uv sync` creates a working Python 3.12 environment.
- `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .` pass.
- The sample SI and matching review transcript load independently.
- Basic review metadata identifies one SI review round.
- Analyze works in deterministic mode without network or API credentials.
- The seven required result sections appear in the planned order.
- At least one finding maps to an SI section.
- Evidence is visibly distinguished as SI or transcript evidence.
- Review Outcome and all required list items contain valid evidence.
- The reviewer can edit and remove proposed items.
- Invalid reviewed data cannot be approved.
- Approval is an explicit Domain Architect action.
- Generated outputs reflect the edited, approved record.
- The structured record, minutes, and mock ADO outputs are clearly labeled.
- Reanalysis or edits invalidate stale approval and generated outputs.
- No live Confluence, Teams, or ADO operation occurs.
- Tests cover the model, deterministic provider, generators, and core orchestration.
- Documentation matches the implemented one-round SI workflow.
- The recorded demo uses only synthetic data and remains shorter than four minutes.

## Technical architecture

```text
Streamlit UI
    |
    |-- synthetic SI content
    |-- synthetic review transcript
    |-- SolutionIntentReviewContext
    v
Governance service
    |
    +--> GovernanceExtractor
    |       +--> DeterministicDemoExtractor (required)
    |       \--> Optional real LLM provider (future)
    |
    +--> Pydantic one-round review models
    |
    +--> Review-record / minutes generator
    |
    \--> Mock ADO update and work-item generator
```

### Module responsibilities

- `app.py`: UI, input loading, review widgets, evidence presentation, explicit approval, and
  session-state transitions.
- `models.py`: strict Pydantic enums and models for one SI review round.
- `extractors.py`: provider protocol and deterministic fixture-backed provider.
- `governance_service.py`: coordinates analysis, validation, review approval, and generation.
- `minutes_generator.py`: pure deterministic transformation to review minutes.
- `ado_generator.py`: pure deterministic transformation to mock governance-ticket and action
  payloads.
- `samples/`: frozen synthetic SI, review metadata, transcript, and expected result fixtures.
- `tests/`: validation and transformation tests independent of external services.

Streamlit session state is the only planned runtime state. It will hold the three inputs, latest
analysis, editable reviewed record, approval state, and generated outputs. It will not hold or
simulate review history.

## Model design

All models inherit one small strict base configuration with `extra="forbid"` and whitespace
normalization. Required strings reject blank values after trimming. Dates use `datetime.date`.
Collection defaults use independent factories. All models serialize with
`model_dump(mode="json")`.

### Enums

| Enum | Values | Purpose |
| --- | --- | --- |
| `EvidenceSource` | `solution_intent`, `meeting_transcript` | Identifies the evidence origin. |
| `SolutionIntentStatus` | `draft`, `under_review`, `changes_requested`, `conditionally_approved`, `approved`, `rejected` | Current overall SI lifecycle status. |
| `ReviewOutcome` | `changes_requested`, `conditionally_approved`, `approved`, `rejected`, `pending`, `not_stated` | Outcome of this review round only. |
| `FindingSeverity` | `low`, `medium`, `high`, `critical` | Impact of a review finding. |
| `FindingStatus` | `open`, `resolved`, `deferred`, `accepted` | Finding tracking state; normally `open` in the MVP. |
| `RiskSeverity` | `low`, `medium`, `high`, `critical` | Severity of a risk. |
| `ActionPriority` | `low`, `medium`, `high` | Priority of an action. |

### `SourceEvidence`

| Field | Type | Validation |
| --- | --- | --- |
| `source_type` | `EvidenceSource` | Required. |
| `quote` | non-empty string | Required. |
| `speaker` | non-empty string or `None` | Optional; primarily transcript evidence. |
| `timestamp` | non-empty string or `None` | Optional; no timestamp parsing yet. |
| `section` | non-empty string or `None` | Optional; primarily SI evidence. |
| `reference` | non-empty string or `None` | Optional source reference. |

The model deliberately does not enforce source-specific locators yet.

### `SolutionIntentReviewContext`

| Field | Type | Validation |
| --- | --- | --- |
| `project_name` | non-empty string | Required. |
| `si_title` | non-empty string | Required. |
| `si_version` | non-empty string | Required. |
| `current_si_status` | `SolutionIntentStatus` | Required. |
| `review_round` | integer | Required and at least 1. |
| `ado_ticket_id` | non-empty string or `None` | Optional; no company-specific format validation. |
| `domain_architect` | non-empty string or `None` | Optional. |
| `review_date` | date or `None` | Optional ISO date in JSON. |

The context identifies one round but contains no prior or subsequent rounds and no Confluence
identifier.

### `ReviewFinding`

| Field | Type | Validation |
| --- | --- | --- |
| `title` | non-empty string | Required. |
| `description` | non-empty string | Required. |
| `category` | non-empty string or `None` | Optional. |
| `si_section` | non-empty string or `None` | Optional mapping to the SI. |
| `severity` | `FindingSeverity` | Required. |
| `status` | `FindingStatus` | Defaults to `open`. |
| `recommended_change` | non-empty string or `None` | Optional. |
| `owner` | non-empty string or `None` | Optional; never invented. |
| `due_date` | date or `None` | Optional. |
| `evidence` | list of `SourceEvidence` | Required and non-empty; may mix both sources. |

There is no finding identifier, persistence state, or automatic resolution behavior.

### Existing review-item models

- `Decision`: required statement, optional rationale, and non-empty evidence.
- `Risk`: required description and severity, optional owner, and non-empty evidence.
- `ActionItem`: required title and priority, optional owner and due date, and non-empty evidence.
- `OpenQuestion`: required question, optional owner, and non-empty evidence.
- `MissingEvidence`: required item, optional reason, and evidence defaulting to an empty list.

These models accept evidence from either source through `SourceEvidence`.

### `GovernanceResult`

| Field | Type | Validation |
| --- | --- | --- |
| `context` | `SolutionIntentReviewContext` | Required. |
| `review_outcome` | `ReviewOutcome` | Required. |
| `outcome_evidence` | list of `SourceEvidence` | Defaults empty; must be non-empty unless outcome is `not_stated`. |
| `findings` | list of `ReviewFinding` | Independent empty default. |
| `decisions` | list of `Decision` | Independent empty default. |
| `risks` | list of `Risk` | Independent empty default. |
| `action_items` | list of `ActionItem` | Independent empty default. |
| `open_questions` | list of `OpenQuestion` | Independent empty default. |
| `missing_evidence` | list of `MissingEvidence` | Independent empty default. |

The result contains one round only. It excludes generated outputs, UI state, approval history,
and multi-round history.

### `MockAdoWorkItem`

| Field | Type | Validation |
| --- | --- | --- |
| `title` | non-empty string | Required. |
| `assigned_to` | non-empty string or `None` | Optional. |
| `due_date` | date or `None` | Optional. |
| `priority` | `ActionPriority` | Required. |
| `description` | non-empty string | Required. |
| `tags` | list of non-empty strings | Independent empty default. |
| `source_action_index` | integer | Required and non-negative. |
| `parent_work_item_id` | non-empty string or `None` | Optional governance ticket reference. |
| `si_section` | non-empty string or `None` | Optional SI-section context. |
| `acceptance_criteria` | list of non-empty strings | Independent empty default. |

This is a preview model only. Action-to-ADO conversion and API submission are future work.

## Provider abstraction

The implemented provider boundary is:

```text
GovernanceExtractor.extract(
    solution_intent: str,
    review_transcript: str,
    context: SolutionIntentReviewContext,
) -> GovernanceResult
```

The governance service receives the provider explicitly. Provider-specific prompts, credentials,
response parsing, and API errors stay behind this interface. Providers do not approve the SI or
generate downstream outputs. `GovernanceExtractor` is a synchronous structural protocol; the
fixture-backed `DeterministicDemoExtractor` is its only current implementation.

## Deterministic demo-provider design

The implemented deterministic provider:

1. loads the bundled synthetic SI, transcript, metadata, and expected result;
2. normalizes only line endings and outer whitespace;
3. confirms that both input documents match their fixtures;
4. validates metadata expected by the scenario;
5. parses the expected JSON as `GovernanceResult`; and
6. returns a deep independent model copy.

If either source differs, deterministic mode must report its limitation rather than fabricate an
analysis. It requires no network, credential, model SDK, Confluence page, Teams API, or ADO API.

## Main technical and demo risks

| Risk | Mitigation |
| --- | --- |
| Findings are not traceable to the SI | Require typed evidence and map findings to SI sections where supported. |
| Transcript is treated as the reviewed object | Keep SI content visually primary and require both documents as analysis inputs. |
| The tool appears to approve architecture autonomously | Make approval an explicit Domain Architect action and state this in UI and narration. |
| Fixture and model drift | Validate the complete expected result in automated tests. |
| Streamlit reruns lose reviewed state | Define explicit state transitions and invalidate stale outputs. |
| Generated outputs ignore human edits | Generate only from the approved reviewed model and test edited values. |
| ADO previews look like live updates | Label them as mock and perform no external request. |
| Multi-round capability expands the MVP | Store only `review_round`; exclude history, comparison, and resolution logic. |
| Video exceeds four minutes | Use one round, one key finding, one decision, one risk, two actions, and one open item. |
| Network or LLM failure | Record in deterministic offline mode. |
| Confidential data enters the demo | Use obviously fictional project, document, and people data only. |

## Implementation plan

| Phase | Files | Expected outcome | Verification | Depends on |
| --- | --- | --- | --- | --- |
| 1. SI domain models and tests | `models.py`, `test_models.py` | Strict models for one SI review round, findings, and dual-source evidence. | Model tests, Ruff. | Planning. |
| 2. Synthetic SI, transcript, metadata, and expected result | `samples/`, `test_sample_data.py` | One internally consistent fictional review-round fixture. | Validate JSON, models, scenario counts, safety, and every evidence quote. | Phase 1. |
| 3. Deterministic provider (complete) | `extractors.py`, `test_extractors.py` | Match both sources and return the known validated result offline. | Match, mismatch, repeatability, and corrupt-fixture tests. | Phases 1–2. |
| 4. Review minutes generator (complete) | `minutes_generator.py`, generator tests | Stable minutes covering context, findings, and evidence. | Deterministic content assertions. | Phases 1–2. |
| 5. Mock ADO action generator (complete) | `ado_generator.py`, generator tests | One typed mock work item per action; parent-ticket update remains future work. | Mapping, counts, nulls, SI section, and criteria tests. | Phases 1–2. |
| 6. Governance service | `governance_service.py`, service tests | Analyze, validate, approve, and generate without UI dependencies. | Approval-gating and stale-state tests. | Phases 3–5. |
| 7. Streamlit UI | `app.py` | Load both sources, show seven sections and evidence, approve, and display outputs. | Manual one-round smoke test. | Phase 6. |
| 8. Editable human review | `app.py`, focused tests | Edit/remove items and invalidate approval on changes. | Manual review paths and edited-output tests. | Phase 7. |
| 9. Optional real LLM provider | Provider module/tests, dependency only if justified | Analyze arbitrary synthetic SI reviews without changing deterministic mode. | Mocked API tests and one synthetic trial. | Phases 1–8; optional. |
| 10. Final hardening | Tests and docs | Clean setup, stable demo, aligned documentation, timed recording. | Full `uv` checks and two successful rehearsals. | Phases 1–8. |

Multi-round tracking, version comparison, and finding resolution are deliberately absent from
this plan's MVP phases.
