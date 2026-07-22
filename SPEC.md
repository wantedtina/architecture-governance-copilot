# Architecture Governance Copilot — Product and Technical Specification

## Document purpose

This document defines a hackathon proof of concept (PoC) for drafting and reviewing a Solution
Intent (SI). The final deliverable is a video shorter than four minutes, due on 22 July 2026.
The PoC proves one reliable, human-controlled drafting handoff and SI review round; it is not a
production platform.

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
and explicitly confirm the reviewed record before minutes and mock ADO outputs are generated.
Formal approval remains the responsibility of the human Domain Architect.

## Target users

- **Primary:** Domain Architects who review Solution Intents and own the formal review outcome.
- **Secondary:** Product Owners and development teams who prepare and update the SI.
- **Secondary:** solution and enterprise architects who need traceable decisions, findings, and
  risks.
- **Secondary:** delivery leads and action owners who need follow-up work represented clearly.
- **Demo audience:** hackathon judges and stakeholders evaluating the usefulness of the workflow.

## Product goal

Given a synthetic SI template, selected synthetic source-code context, and supporting notes,
produce an editable SI draft for human confirmation. Given that confirmed SI, a synthetic
Teams-style review transcript, and basic review metadata, produce a structured proposal
containing:

- the current review-round outcome;
- review findings mapped to SI sections where possible;
- confirmed architecture decisions;
- risks;
- actions, owners, due dates, and priorities;
- open questions;
- missing governance information; and
- supporting evidence from the SI or meeting transcript.

After human review and confirmation of the reviewed record, generate:

1. a structured SI review record;
2. standardized review meeting minutes; and
3. mock ADO action work items linked to the governance ticket where available.

Success means the deterministic demo completes this one-round workflow reliably. It does not
mean that the PoC can govern arbitrary projects or replace Domain Architect judgment.

## Core end-to-end user journey

1. Start in the first-class Project Context stage.
2. Open the bundled synthetic project workspace and inspect its available source package.
3. Explicitly include or exclude the SI template, repository context, supporting evidence, and
   governance metadata, then confirm the context package.
4. Generate a deterministic SI draft behind the drafting-provider interface.
5. Let a project-team reviewer edit and confirm the draft.
6. Hand the confirmed SI directly to Review Inputs.
7. Alternatively, explicitly choose **Use Existing Solution Intent** and skip context selection
   and drafting.
8. Load the synthetic review transcript and metadata without replacing a confirmed SI, or load
   the complete bundled SI, transcript, and metadata review package.
9. Analyze the review using the SI, transcript, and review metadata.
10. Display the review outcome, findings, decisions, risks, actions, open questions, and missing
   information.
11. Show supporting SI or transcript evidence for each extracted claim.
12. Allow human review, editing, and removal of proposed items.
13. Let the Domain Architect explicitly confirm the reviewed record for output generation.
14. Generate the structured review record, review minutes, and mock ADO outputs from the
   human-confirmed state.

The implemented UI uses five peer-level routed stages: Project Context, Draft Solution Intent,
Review Inputs, Human Review, and Generated Outputs. Project Context is the default start. The
progress header marks context selection and drafting **Complete** after confirmation or
**Skipped** when the user chooses the existing-SI path.

The MVP performs this journey for one review round only. `review_round` metadata prepares the
record for future tracking, but the application will not compare versions, persist history, or
automatically carry findings between rounds.

## Functional requirements

### Pre-review SI drafting

- Present Project Context as Stage 1 and Draft Solution Intent as Stage 2, at the same navigation
  level as Review Inputs.
- Provide a project workspace selector and production-shaped source cards for the bundled
  synthetic template, repository, supporting evidence, and governance metadata.
- Require explicit confirmation of the required template and repository sources before drafting.
- Clearly label source statuses as simulated and make no external synchronization or API calls.
- Provide **Use Existing Solution Intent** as an explicit drafting bypass.
- Accept project name, SI template, selected source-code context, and optional supporting notes.
- Treat source code as pasted or pre-normalized text; do not clone, scan, or execute repositories.
- Hide draft generation behind a `SolutionIntentDrafter` provider interface.
- Use a deterministic offline provider for the bundled synthetic scenario.
- Produce a validated `SolutionIntentDraft` with explicit assumptions.
- Allow a human to edit the draft before confirmation.
- Require **Confirm SI Draft & Continue to Review** before handoff.
- Populate the existing Solution Intent review input with the confirmed content.
- Allow transcript and review metadata to load without replacing that SI.
- Preserve human edits during handoff, while clearly stating that the deterministic review
  extractor accepts only the unchanged bundled SI.
- Do not publish to Confluence or claim architecture approval.

### Inputs

- Provide a **Load Sample Review** action.
- Load synthetic SI content from `samples/solution_intent.md`.
- Display the SI in a readable multiline area.
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
  2. Decisions
  3. Review Findings
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

### Human review and confirmation

- Allow the reviewer to edit meaningful extracted fields.
- Allow the reviewer to remove proposed list items.
- Keep supporting evidence visible during review.
- Treat evidence as traceability metadata rather than freeform text to casually rewrite.
- Prevent output generation when the reviewed record fails validation.
- Require an explicit **Confirm Reviewed Record & Generate Outputs** action.
- Advance to Human Review after successful analysis and to Generated Outputs after successful
  reviewed-result validation.
- Show only the active routed stage, with browser-style Back and Reset navigation.
- State that formal governance decisions remain the Domain Architect's responsibility.
- Generate outputs from the confirmed, edited state rather than the original provider response.
- Invalidate reviewed outputs after reanalysis or subsequent input edits.

### Reviewed outputs

- Generate outputs only after explicit human confirmation of the reviewed record.
- Keep the validated reviewed `GovernanceResult` as the source for generated outputs.
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
- Generate one mock ADO action work item per included reviewed action.
- Allow mock work items to reference the parent ticket, SI section, and acceptance criteria.
- Clearly state that no payload is sent to Azure DevOps.

## Non-functional requirements

- **Reliability:** the bundled scenario must work offline without credentials or an LLM API.
- **Human accountability:** the system proposes a record; it does not approve the SI.
- **Traceability:** claims retain evidence source, quote, and available locator information.
- **Determinism:** stable inputs produce stable results and generated outputs.
- **Perceived responsiveness:** Analyze and Confirm show short, configurable processing phases
  before routed navigation; the delay is demo presentation only and does not simulate external
  integrations.
- **Simplicity:** use direct Python modules, Pydantic, and Streamlit session state.
- **Testability:** models and pure transformations must be testable without Streamlit.
- **Readability:** the review and evidence must be legible during a short screen recording.
- **State safety:** stale confirmation and outputs must not survive changes to source or review
  data.
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

- Arbitrary-project SI generation.
- Repository cloning, recursive source-code scanning, build execution, or static analysis.
- Binary document parsing, OCR, or unrestricted file ingestion.
- Real Confluence template retrieval or SI publication.
- Production enterprise LLM drafting.
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

- The bundled drafting template, source context, and supporting notes load together.
- SI draft generation works deterministically without network access or credentials.
- The draft is editable and requires explicit human confirmation.
- The five-stage progress header truthfully distinguishes completed and skipped context and
  drafting stages.
- The confirmed SI appears in existing Review Inputs.
- Loading transcript and metadata preserves the confirmed SI.
- `uv sync` creates a working Python 3.12 environment.
- `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .` pass.
- The sample SI, matching review transcript, and metadata load together.
- Basic review metadata identifies one SI review round.
- Analyze works in deterministic mode without network or API credentials.
- The seven required result sections appear in the planned order.
- At least one finding maps to an SI section.
- Evidence is visibly distinguished as SI or transcript evidence.
- Review Outcome and all required list items contain valid evidence.
- The reviewer can edit and remove proposed items.
- Invalid reviewed data cannot generate outputs.
- Reviewed-record confirmation is explicit and does not imply formal SI approval.
- Analysis and confirmation change the browser route rather than appending the next stage below
  the previous one.
- Generated outputs reflect the edited, confirmed record.
- The structured record and minutes are clearly labeled, and ADO output is presented as
  preview-only with an explicit no-submission disclosure.
- Reanalysis or input edits invalidate stale generated outputs.
- No live Confluence, Teams, or ADO operation occurs.
- Tests cover the model, deterministic provider, generators, and core orchestration.
- Documentation matches the implemented one-round SI workflow.
- The recorded demo uses only synthetic data and remains shorter than four minutes.

## Technical architecture

```text
Streamlit UI
    |
    |-- synthetic drafting template
    |-- selected source-code context
    |-- synthetic supporting notes
    v
SolutionIntentDraftingService
    |
    +--> SolutionIntentDrafter
    |       +--> DeterministicDemoDrafter (required)
    |       \--> Optional enterprise LLM drafter (future)
    |
    +--> SolutionIntentDraftRequest / SolutionIntentDraft
    |
    \--> Human confirmation
             |
             v
        Review Inputs
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
    \--> Mock ADO action work-item generator
```

### Module responsibilities

- `app.py`: common application shell, route configuration, SI-drafting controls, input loading,
  review widgets, read-only evidence, explicit confirmations, output rendering, and state
  transitions.
- `pages/`: thin file-backed route entry points for SI Drafting, Review Inputs, Human Review,
  and Generated Outputs.
- `ui_support.py`: pure sample, state, fingerprint, optional-field, and reviewed-result helpers.
- `models.py`: strict Pydantic enums and models for one SI review round.
- `si_drafting.py`: drafting-provider protocol, deterministic provider, and drafting service.
- `extractors.py`: provider protocol and deterministic fixture-backed provider.
- `governance_service.py`: separately coordinates extractor analysis and output generation from
  a caller-supplied reviewed result; it does not approve records.
- `minutes_generator.py`: pure deterministic transformation to review minutes.
- `ado_generator.py`: pure deterministic transformation to mock ADO action-work-item payloads.
- `samples/`: frozen synthetic SI, review metadata, transcript, and expected result fixtures.
- `tests/`: validation and transformation tests independent of external services.

Streamlit session state is the only runtime state. It holds drafting context and draft,
human-confirmed SI content, the review inputs, latest analysis, independent review draft,
validated reviewed record, generated outputs, errors, analyzed-input fingerprint, durable
in-progress review fields, and active route stage. It does not hold or simulate review history.

## Model design

All models inherit one small strict base configuration with `extra="forbid"` and whitespace
normalization. Required strings reject blank values after trimming. Dates use `datetime.date`.
Collection defaults use independent factories. All models serialize with
`model_dump(mode="json")`.

### SI-drafting models

- `SolutionIntentDraftRequest` contains required `project_name`, required template text,
  required selected source-code context, and optional supporting-document context.
- `SolutionIntentDraft` contains the project name, generated Markdown content, provider name,
  input-type provenance, and explicit assumptions.
- `DraftInputType` distinguishes template, source-code, and supporting-document context.
- Both models reject unknown fields and blank required strings. The draft requires at least two
  context types. Provider output is always human-editable and never represents publication or
  approval.

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

The implemented SI-drafting provider boundary is:

```text
SolutionIntentDrafter.draft(
    request: SolutionIntentDraftRequest,
) -> SolutionIntentDraft
```

`SolutionIntentDraftingService` receives the provider explicitly. The current
`DeterministicDemoDrafter` accepts only the bundled synthetic template, source context, and
supporting notes. It returns the known synthetic SI plus explicit assumptions. It does not scan
repositories, execute source, call an LLM, publish to Confluence, or approve architecture.

The implemented governance-review provider boundary is:

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

The implemented service boundary deliberately keeps the human-review point between two calls:

```text
Analyze → Human review/edit in the Streamlit UI → Generate outputs from reviewed result
```

`GovernanceReviewService.analyze_review` delegates only to the injected extractor.
`GovernanceReviewService.generate_outputs` does not rerun extraction; it transforms the
caller-supplied validated result into immutable `GovernanceOutputs`. The service carries no
approval flag, UI state, or governance authority.

## Deterministic demo-provider design

The deterministic drafter:

1. loads the bundled synthetic template, source context, supporting notes, and expected SI;
2. checks normalized inputs against those fixtures;
3. returns a validated independent `SolutionIntentDraft`; and
4. requires human confirmation before review handoff.

The deterministic review extractor:

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
| Draft generation overstates what source code proves | Use selected synthetic excerpts, preserve explicit gaps, show assumptions, and require human review. |
| Sensitive repositories or documents are uploaded | Do not clone, scan, or execute repositories in the PoC; use synthetic pasted context only. |
| A generated SI appears published or approved | Label it as a draft and require separate human confirmation before governance review. |
| Findings are not traceable to the SI | Require typed evidence and map findings to SI sections where supported. |
| Transcript is treated as the reviewed object | Keep SI content visually primary and require both documents as analysis inputs. |
| The tool appears to approve architecture autonomously | Label the action as reviewed-record confirmation and state that formal decisions remain with the Domain Architect. |
| Fixture and model drift | Validate the complete expected result in automated tests. |
| Streamlit reruns lose reviewed state | Define explicit state transitions and invalidate stale outputs. |
| Generated outputs ignore human edits | Generate only from the validated reviewed model and test edited values. |
| ADO previews look like live updates | Label them preview-only, show a no-submission disclosure, and perform no external request. |
| Multi-round capability expands the MVP | Store only `review_round`; exclude history, comparison, and resolution logic. |
| Video exceeds four minutes | Use one round, one key finding, one decision, one risk, two actions, and one open item. |
| Network or LLM failure | Record in deterministic offline mode. |
| Confidential data enters the demo | Use obviously fictional project, document, and people data only. |

## Implementation plan

| Phase | Files | Expected outcome | Verification | Depends on |
| --- | --- | --- | --- | --- |
| 0. Optional deterministic SI drafting (complete) | `si_drafting.py`, drafting models, synthetic context, drafting route, tests | Generate, edit, confirm, and hand a known synthetic SI to existing Review Inputs. | Provider mismatch tests, state-handoff tests, Streamlit end-to-end test. | Existing review PoC. |
| 1. SI domain models and tests | `models.py`, `test_models.py` | Strict models for one SI review round, findings, and dual-source evidence. | Model tests, Ruff. | Planning. |
| 2. Synthetic SI, transcript, metadata, and expected result | `samples/`, `test_sample_data.py` | One internally consistent fictional review-round fixture. | Validate JSON, models, scenario counts, safety, and every evidence quote. | Phase 1. |
| 3. Deterministic provider (complete) | `extractors.py`, `test_extractors.py` | Match both sources and return the known validated result offline. | Match, mismatch, repeatability, and corrupt-fixture tests. | Phases 1–2. |
| 4. Review minutes generator (complete) | `minutes_generator.py`, generator tests | Stable minutes covering context, findings, and evidence. | Deterministic content assertions. | Phases 1–2. |
| 5. Mock ADO action generator (complete) | `ado_generator.py`, generator tests | One typed mock work item per action; parent-ticket update remains future work. | Mapping, counts, nulls, SI section, and criteria tests. | Phases 1–2. |
| 6. Governance service (complete) | `governance_service.py`, service tests | Keep extractor analysis separate from generation using a caller-supplied reviewed result. | Delegation, separation, edit-preservation, exception, and independence tests. | Phases 3–5. |
| 7. Streamlit UI (complete) | `app.py`, `pages/`, `ui_support.py`, UI tests | Navigate four peer-level stages, support a completed or skipped drafting path, show seven editable sections with evidence, and display reviewed outputs. | Streamlit `AppTest`, route-guard tests, pure support tests, and headless startup. | Phase 6. |
| 8. Editable human review (complete) | `app.py`, `ui_support.py`, focused tests | Edit/exclude items, validate a reconstructed result, and prevent stale generation. | Edit, exclusion, validation, mutation, reset, and stale-input tests. | Phase 7. |
| 9. Optional real LLM provider | Provider module/tests, dependency only if justified | Analyze arbitrary synthetic SI reviews without changing deterministic mode. | Mocked API tests and one synthetic trial. | Phases 1–8; optional. |
| 10. Final hardening | Tests and docs | Clean setup, stable demo, aligned documentation, timed recording. | Full `uv` checks and two successful rehearsals. | Phases 1–8. |

Multi-round tracking, version comparison, and finding resolution are deliberately absent from
this plan's MVP phases.
