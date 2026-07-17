# Architecture Governance Copilot — Product and Technical Specification

## Document purpose

This document defines the hackathon proof of concept (PoC) to be demonstrated in a video
shorter than four minutes and delivered by 22 July 2026. It is a planning document, not an
implementation claim. The current repository contains only project configuration,
documentation, and placeholder files.

## Problem statement

Architecture governance meetings create decisions, risks, follow-up actions, and evidence
requirements that must be converted from conversation into a durable governance record.
Doing this manually is slow and inconsistent. Important context can be lost, action ownership
can remain ambiguous, and reviewers may struggle to trace a recorded item back to what was
actually said.

The PoC will show that a transcript can be converted into structured, source-backed governance
information, reviewed by a human, and then reused to produce standardized minutes and
work-item payloads. It will prove one controlled workflow; it will not prove production-scale
accuracy, integration, or operations.

## Target users

- **Primary:** architecture governance reviewers who validate meeting outcomes and evidence.
- **Secondary:** solution and enterprise architects who need a clear record of decisions,
  conditions, risks, and follow-up work.
- **Secondary:** delivery leads and action owners who need governance actions represented as
  trackable work.
- **Demo audience:** hackathon judges and stakeholders evaluating whether the workflow is
  useful and credible.

## Product goal

Given a synthetic Microsoft Teams-style architecture governance meeting transcript, extract a
structured governance record with supporting source evidence for every item. Allow a human to
edit, remove, and approve that record. Only after approval, generate standardized meeting
minutes and mock Azure DevOps (ADO) work-item payloads for the approved action items.

Success means the demo reliably completes this end-to-end journey. It does not mean that the
PoC is suitable for production use.

## Core end-to-end user journey

1. The reviewer opens the Streamlit application in deterministic demo mode.
2. The reviewer clicks **Load Sample Transcript**.
3. The bundled synthetic Teams-style transcript appears in an editable text area.
4. The reviewer clicks **Analyze**.
5. The deterministic provider returns the known structured result for the bundled sample.
6. The UI displays Review Outcome, Decisions, Risks, Action Items, Open Questions, and Missing
   Evidence. Every outcome or item has a source quote or transcript reference.
7. The reviewer inspects the proposed record, edits at least one field, and may remove an item.
8. The reviewer clicks **Approve Governance Record**.
9. The application freezes the reviewed state as the approved record for that run.
10. The application displays standardized meeting minutes and mock ADO work-item JSON payloads
    derived only from the approved data.

If the transcript changes after analysis, the prior analysis and approval state must become
stale or be cleared so that outputs cannot silently diverge from their source.

## Functional requirements

### Transcript input

- Provide a **Load Sample Transcript** button.
- Load only the bundled synthetic transcript from `samples/review_transcript.txt`.
- Display the transcript in a multiline editable text area.
- Provide an **Analyze** button.
- Reject empty or whitespace-only input with a clear message.
- Make deterministic demo mode visible in the interface.

### Analysis and structured record

- Hide transcript analysis behind a provider interface.
- Use the deterministic demo provider by default.
- Display these sections in a stable order:
  1. Review Outcome
  2. Decisions
  3. Risks
  4. Action Items
  5. Open Questions
  6. Missing Evidence
- Show the supporting source quote and transcript reference for every displayed outcome or
  item.
- Preserve stable item identifiers through review and generation.
- Show a clear empty state for a category with no items.
- Surface validation or provider errors without losing the transcript.

### Human review

- Allow the reviewer to edit the meaningful extracted fields presented in each section.
- Allow the reviewer to remove list items before approval.
- Keep source evidence visible during editing.
- Do not let the reviewer approve a record that fails model validation.
- Make approval an explicit button action.
- Make approved outputs reflect the reviewed values, not the original provider response.
- Invalidate prior approval and generated outputs when the transcript is reanalyzed or the
  reviewed record changes.

For the PoC, source evidence itself should be treated as traceability metadata rather than
freeform content to rewrite. If evidence needs correction, the item should be removed and the
transcript reanalyzed. This reduces demo complexity and avoids presenting altered quotes as
source text.

### Approved outputs

- Generate outputs only after **Approve Governance Record** is clicked.
- Generate deterministic Markdown meeting minutes with:
  - meeting metadata,
  - review outcome,
  - confirmed decisions,
  - risks,
  - actions with owner, due date, and priority,
  - open questions,
  - missing governance evidence,
  - source references.
- Generate one mock ADO work-item payload for each approved action item.
- Clearly label ADO payloads as mock data that is not sent to Azure DevOps.
- Keep generated outputs stable for the same approved input.

## Non-functional requirements

- **Demo reliability:** the bundled sample and expected result must work offline with no LLM
  credentials or network access.
- **Traceability:** every extracted outcome and list item must include at least one valid source
  evidence record.
- **Human control:** no minutes or work-item payloads are generated from an unapproved record.
- **Readability:** the main workflow and six result sections must be understandable at normal
  laptop resolution during screen recording.
- **Simplicity:** use direct Python modules and Streamlit session state; do not introduce an
  agent framework, persistence layer, or unnecessary abstractions.
- **Determinism:** the demo provider, generators, and tests must give stable results for stable
  inputs.
- **Testability:** models and pure generator functions must be testable without starting
  Streamlit.
- **Maintainability:** Python 3.12, type hints for public functions, Pydantic v2 models, and a
  src-based package layout.
- **Quality gates:** planned automated checks are `pytest`, `ruff check`, and
  `ruff format --check`, all invoked through `uv`.
- **Data safety:** use synthetic data only and commit no API keys, secrets, personal data, or
  company-confidential information.
- **Performance:** analysis of the bundled sample should appear effectively immediate in
  deterministic mode; a specific production service-level objective is out of scope.
- **Accessibility:** use clear labels, headings, button text, and status messages; do not rely
  on color alone to communicate state.

## Assumptions

- The final demo runs locally on a laptop with Python 3.12 and `uv` available.
- Internet access and LLM credentials may be unavailable during recording or judging.
- The demonstration uses exactly one bundled synthetic meeting scenario.
- The transcript is plain text formatted to resemble a Teams transcript, including speakers
  and timestamps or stable line references.
- The human reviewer is responsible for the final approved wording.
- ADO output is inspected as JSON in the UI and is never submitted to a service.
- A single Streamlit browser session is sufficient; concurrent users and durable state are not
  required.
- The optional real LLM provider, if attempted, comes after the deterministic workflow is
  complete and does not become a dependency of the demo.

## Explicit MVP exclusions

- Production readiness, deployment, observability, scaling, and support.
- Authentication, authorization, role management, and audit-log persistence.
- A database or any other durable state.
- Real Microsoft Teams ingestion or Microsoft Graph integration.
- Real Confluence publishing.
- Real Azure DevOps API calls, authentication, or work-item creation.
- RAG, vector databases, embeddings, document retrieval, or knowledge bases.
- Agent frameworks, tool-calling agents, autonomous workflows, or multi-agent systems.
- Dashboards, analytics, reporting history, and cross-meeting search.
- Live audio, transcription, diarization, or meeting-bot functionality.
- Multiple transcript formats, bulk processing, and file upload.
- Production-grade prompt evaluation, model routing, retries, or cost controls.
- Use of real internal company information.

## Definition of Done

The PoC is done when all of the following are true:

- The repository follows the agreed structure and uses only `pyproject.toml` and the
  tool-generated `uv.lock` for dependency management.
- A fresh environment can be created with `uv sync`.
- `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .` pass.
- **Load Sample Transcript** loads the synthetic transcript into the text area.
- **Analyze** uses deterministic demo mode successfully without any LLM API.
- All six required result sections are displayed.
- Review Outcome and every extracted list item display valid supporting evidence.
- The reviewer can edit meaningful fields and remove list items.
- Invalid reviewed data cannot be approved.
- **Approve Governance Record** generates minutes and mock ADO payloads from the reviewed data.
- The number and content of mock ADO payloads match the approved action items.
- Generated outputs are clearly distinguished from external integrations.
- Reanalysis or review changes cannot leave stale approved outputs visible as current.
- The deterministic result and generated outputs have automated coverage for core behavior.
- `README.md`, this specification, and `DEMO.md` match the implemented workflow.
- The recorded demonstration uses only synthetic data, completes the workflow reliably, and is
  shorter than four minutes.

## Technical architecture

The PoC uses a small layered design:

```text
Streamlit UI (app.py)
        |
        v
Governance service (workflow orchestration)
        |
        +--> ExtractorProvider interface
        |        +--> DeterministicDemoProvider (required)
        |        \--> Optional real LLM provider (future)
        |
        +--> Pydantic governance models
        |
        +--> Minutes generator (pure transformation)
        |
        \--> Mock ADO generator (pure transformation)
```

### Module responsibilities

- `app.py`: Streamlit layout, event handling, editable review widgets, approval action, and
  session-state presentation. It should contain no extraction or output-mapping logic.
- `models.py`: Pydantic models, enums, field validation, and cross-model invariants.
- `extractors.py`: the provider protocol and deterministic provider. An optional real provider
  may later live here while the interface remains small.
- `governance_service.py`: coordinates provider analysis, record validation, approval, and
  generation. It should accept dependencies explicitly and remain independent of Streamlit.
- `minutes_generator.py`: deterministic conversion of an approved `GovernanceResult` to
  standardized Markdown.
- `ado_generator.py`: deterministic conversion of approved action items to
  `MockAdoWorkItem` objects or JSON-ready dictionaries.
- `samples/review_transcript.txt`: synthetic, Teams-style demo transcript.
- `samples/expected_result.json`: known valid structured response used by deterministic mode.

Streamlit session state is the only planned runtime state. The UI owns a transcript, the latest
analyzed result, the editable reviewed result, its approval state, and generated outputs. No
state is persisted between sessions.

## Proposed Pydantic model design

The following designs are proposals for phase 1. They are intentionally not implemented yet.
All models should reject unknown fields (`extra="forbid"`) to expose drift between providers,
fixtures, and generators. Strings should be trimmed. Required descriptive strings should reject
empty or whitespace-only values. IDs should be stable, human-readable strings unique within a
`GovernanceResult`, such as `DEC-001` or `ACT-001`.

### Shared value conventions

- Dates use `datetime.date` and serialize as ISO 8601 `YYYY-MM-DD`.
- Timestamps, when present, use a display-oriented `HH:MM:SS` string validated for valid clock
  time; they are transcript offsets, not time-zone-aware event times.
- Priorities use a small enum: `high`, `medium`, or `low`.
- Review outcome status uses: `approved`, `approved_with_conditions`, `deferred`, or `rejected`.
- Risk severity uses: `high`, `medium`, or `low`.
- Optional owner or due-date fields may be `None` when the transcript does not establish them;
  corresponding ambiguity should appear as an open question or missing-evidence item.

### `SourceEvidence`

Represents the trace from one structured claim to the transcript.

| Field | Type | Rules |
| --- | --- | --- |
| `evidence_id` | `str` | Required, non-empty; unique within the complete result. |
| `quote` | `str` | Required exact excerpt, non-empty; concise enough for the review UI. |
| `speaker` | `str \| None` | Trimmed; `None` only if the source format lacks a speaker. |
| `timestamp` | `str \| None` | Valid `HH:MM:SS` when present. |
| `line_start` | `int \| None` | Positive when present. |
| `line_end` | `int \| None` | Positive and greater than or equal to `line_start`; present only when `line_start` is present. |

At least one locator must be present: `timestamp` or `line_start`. The quote is stored with the
item so the demo remains readable, while the locator supports verification against the source.

### `ReviewOutcome`

Represents the meeting-level governance disposition.

| Field | Type | Rules |
| --- | --- | --- |
| `status` | outcome enum | Required and limited to the four declared values. |
| `summary` | `str` | Required, non-empty, concise human-readable conclusion. |
| `conditions` | `list[str]` | Defaults to empty; each entry non-empty and unique after normalization. |
| `evidence` | `list[SourceEvidence]` | Required and must contain at least one entry. |

`approved_with_conditions` must contain at least one condition. Other statuses may have an empty
conditions list. Duplicate evidence references within the outcome are rejected.

### `Decision`

Represents a confirmed architecture decision, not a suggestion or unresolved question.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | `str` | Required stable identifier; `DEC-` prefix proposed. |
| `title` | `str` | Required, non-empty, short display label. |
| `description` | `str` | Required, non-empty statement of the confirmed decision. |
| `rationale` | `str \| None` | Optional non-empty text when the rationale was stated. |
| `evidence` | `list[SourceEvidence]` | Required and non-empty. |

The model does not include a decision status because only confirmed decisions belong in this
collection. Proposed or pending choices belong in `OpenQuestion`.

### `Risk`

Represents an identified architecture or delivery risk.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | `str` | Required stable identifier; `RSK-` prefix proposed. |
| `title` | `str` | Required, non-empty summary. |
| `description` | `str` | Required, non-empty explanation of the risk. |
| `impact` | `str` | Required, non-empty consequence if the risk materializes. |
| `severity` | severity enum | Required: `high`, `medium`, or `low`. |
| `mitigation` | `str \| None` | Optional; non-empty if supplied. |
| `owner` | `str \| None` | Optional because the meeting may not assign one. |
| `evidence` | `list[SourceEvidence]` | Required and non-empty. |

Priority is intentionally reserved for actions; risks use severity. The UI can expose an
unassigned owner without inventing one.

### `ActionItem`

Represents agreed follow-up work.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | `str` | Required stable identifier; `ACT-` prefix proposed. |
| `title` | `str` | Required, non-empty, suitable as a work-item title. |
| `description` | `str` | Required, non-empty statement of the required work. |
| `owner` | `str \| None` | Trimmed name; `None` if no owner was confirmed. |
| `due_date` | `date \| None` | ISO date when serialized; `None` if no date was confirmed. |
| `priority` | priority enum | Required: `high`, `medium`, or `low`. |
| `evidence` | `list[SourceEvidence]` | Required and non-empty. |

The model accepts missing owner or due date so the record can faithfully represent incomplete
governance. The deterministic sample should make at least one action complete enough to generate
a useful payload. Missing information is not silently defaulted.

### `OpenQuestion`

Represents an unresolved question explicitly raised or clearly left open.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | `str` | Required stable identifier; `QUE-` prefix proposed. |
| `question` | `str` | Required, non-empty, ending punctuation normalized by presentation rather than validation. |
| `owner` | `str \| None` | Optional person expected to resolve it. |
| `due_date` | `date \| None` | Optional follow-up date. |
| `evidence` | `list[SourceEvidence]` | Required and non-empty. |

The model does not infer an answer. Once answered and approved, the item should be removed or
converted into the appropriate decision/action through reanalysis or review.

### `MissingEvidence`

Represents governance material that the meeting says is absent, incomplete, or still required.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | `str` | Required stable identifier; `EVD-` prefix proposed. |
| `item` | `str` | Required, non-empty name of the missing artifact or proof. |
| `reason_required` | `str` | Required, non-empty explanation of its governance relevance. |
| `owner` | `str \| None` | Optional person responsible for supplying it. |
| `due_date` | `date \| None` | Optional committed date. |
| `evidence` | `list[SourceEvidence]` | Required and non-empty evidence that the gap was identified. |

This records evidence missing from the governance submission. Its `evidence` field is different:
it cites the transcript statement that identified the gap.

### `GovernanceResult`

The canonical analyzed and reviewed governance record.

| Field | Type | Rules |
| --- | --- | --- |
| `schema_version` | `str` | Required fixed initial value such as `1.0`. |
| `meeting_title` | `str` | Required, non-empty. |
| `meeting_date` | `date` | Required ISO date. |
| `review_outcome` | `ReviewOutcome` | Required. |
| `decisions` | `list[Decision]` | Defaults to empty. |
| `risks` | `list[Risk]` | Defaults to empty. |
| `action_items` | `list[ActionItem]` | Defaults to empty. |
| `open_questions` | `list[OpenQuestion]` | Defaults to empty. |
| `missing_evidence` | `list[MissingEvidence]` | Defaults to empty. |

Cross-model validation must ensure:

- item IDs are unique across all five item collections;
- evidence IDs are unique, or a deliberate shared-evidence policy is defined before
  implementation (the simpler proposed rule is unique evidence objects per item);
- every collection item and the outcome have at least one source record;
- meeting metadata are present;
- the serialized fixture round-trips without loss.

Approval metadata should not be embedded in this provider-facing result for the MVP. The service
and UI can track whether the current reviewed instance has been explicitly approved.

### `MockAdoWorkItem`

Represents a JSON-ready preview, not a real Azure DevOps API request.

| Field | Type | Rules |
| --- | --- | --- |
| `work_item_type` | `Literal["Task"]` | Fixed to `Task` for the PoC. |
| `title` | `str` | Required; copied from the approved action title; enforce a reasonable limit such as 128 characters. |
| `description` | `str` | Required; includes the approved action description and source references. |
| `assigned_to` | `str \| None` | Copied from the approved action; never invented. |
| `due_date` | `date \| None` | Copied from the approved action. |
| `priority` | priority enum | Copied from the approved action. |
| `tags` | `list[str]` | Non-empty unique tags, including `Architecture Governance` and `Hackathon PoC`. |
| `source_action_id` | `str` | Required and equal to the originating approved action ID. |

Unknown fields are rejected. The payload is intentionally provider-neutral JSON rather than the
Azure DevOps JSON Patch wire format, which would imply an integration that the PoC does not
provide.

## LLM provider abstraction

Use one small interface, tentatively:

```text
ExtractorProvider.analyze(transcript: str) -> GovernanceResult
```

The interface should be represented by a Python `Protocol` or abstract base class only if the
implementation benefits from it; a `Protocol` is the lighter proposal. The governance service
receives a provider instance through its constructor or function argument. It validates the
returned model and does not know whether the provider is deterministic or LLM-backed.

Provider-specific prompt construction, response parsing, API credentials, and SDK exceptions
must stay behind the provider boundary. No provider may generate minutes or ADO payloads. A
future real provider must return the same `GovernanceResult` and must not be required to run the
app in demo mode.

## Deterministic demo-provider design

The required demo provider is a fixture adapter, not a simulated language model:

1. Read the bundled transcript and expected JSON fixture using paths resolved from the project,
   not the current working directory.
2. Normalize only line endings and insignificant outer whitespace.
3. Verify that the analyzed transcript matches the bundled sample, preferably with a stable
   digest or exact normalized comparison.
4. On a match, load `samples/expected_result.json` and validate it as `GovernanceResult`.
5. Return a fresh model instance so UI edits cannot mutate a cached fixture.
6. On a mismatch, show a clear deterministic-mode limitation and retain the transcript. Do not
   fabricate a result for arbitrary input.

This design guarantees a known demo result, catches fixture drift early, works with no network or
API key, and honestly limits deterministic mode to the sample. Unit tests should prove fixture
validity, sample matching, mismatch behavior, and repeatable output. The provider selector
should default to deterministic mode even if an optional API key exists.

## Main technical and demo risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Extraction output does not match the transcript | Demo loses credibility. | Use a curated synthetic transcript and reviewed expected fixture; require evidence on every item; rehearse quote verification. |
| LLM API, credentials, network, quota, or latency fails | Analyze step stalls or fails during recording. | Make deterministic mode the default and fully offline; do not require the optional provider for any demo step. |
| Fixture and Pydantic schema drift apart | Deterministic mode fails at runtime. | Validate the fixture in automated tests and during service startup or first analysis; update schema and fixture in the same phase. |
| Streamlit reruns erase edits or approval state | Human-review sequence becomes unreliable. | Define explicit session-state keys and state transitions; add focused service tests and rehearse the exact click path. |
| Generated outputs use pre-edit extraction | Demo violates the human-in-the-loop claim. | Generate only from the approved reviewed model; include an edited value in generator tests and the demo script. |
| Stale outputs remain after transcript or record changes | Minutes no longer match the displayed source. | Clear approval and outputs on transcript reload, reanalysis, and review changes; display current state clearly. |
| Evidence is hidden or hard to read on video | Traceability benefit is not visible. | Use compact expanders or cards with a visible quote/reference; test at recording resolution and zoom. |
| Too many fields make review slow | Video exceeds four minutes. | Use one concise scenario, stable section order, preplanned single edit and removal, and a 3:35 target timeline. |
| Missing owner or due date breaks ADO generation | Action conversion fails or invents data. | Keep fields nullable, preserve nulls in mock payloads, and represent the gap in open questions or missing evidence. |
| Users mistake mock output for a live integration | Scope and trust are misrepresented. | Label deterministic mode and mock ADO JSON prominently in the UI, documentation, and narration. |
| Accidental use of confidential data | Creates data-handling risk. | Commit only an obviously fictional scenario with fictional names and systems; review the recording before submission. |
| Dependency setup changes close to the deadline | Local run becomes unreliable. | Keep dependencies minimal, let `uv` generate the lockfile during implementation, and perform a clean-environment rehearsal before recording. |
| Optional real provider consumes core schedule | Reliable path remains unfinished. | Treat it as phase 9 and start it only after phases 1–8 pass; omit it entirely if time is constrained. |

## Implementation plan

Each phase is small enough to verify independently. Work should stop after a phase if its
verification fails. The optional real provider is not on the critical path.

| Phase | Files to modify | Expected outcome | Verification method | Depends on |
| --- | --- | --- | --- | --- |
| 1. Pydantic models and validation tests | `src/architecture_governance_copilot/models.py`, `tests/test_models.py` | Implement the proposed models, enums, and invariants with representative valid/invalid cases. | `uv run pytest tests/test_models.py`; Ruff checks for changed files. | Planning only. |
| 2. Synthetic transcript and deterministic expected result | `samples/review_transcript.txt`, `samples/expected_result.json`, possibly `tests/test_models.py` | Add one fictional Teams-style review and a source-backed fixture valid against the models. | Parse the JSON as `GovernanceResult`; manually verify every quote/reference against the transcript; run model tests. | Phase 1. |
| 3. Deterministic extractor provider | `src/architecture_governance_copilot/extractors.py`, add focused extractor tests | Return the fixture only for the normalized bundled sample and provide a clear mismatch error. | Tests for sample match, mismatch, repeatability, missing/corrupt fixture, and no network requirement. | Phases 1–2. |
| 4. Meeting-minutes generator | `src/architecture_governance_copilot/minutes_generator.py`, `tests/test_minutes_generator.py` | Produce stable, readable Markdown containing all approved sections and source references. | Snapshot-like assertions for headings, reviewed values, empty sections, and deterministic output. | Phases 1–2. |
| 5. Mock ADO work-item generator | `src/architecture_governance_copilot/ado_generator.py`, `tests/test_ado_generator.py` | Produce one validated mock work item per action, preserving owner, due date, priority, and source ID. | Tests for mapping, ordering, nullable fields, edited values, and action-count parity. | Phases 1–2. |
| 6. Governance service orchestration | `src/architecture_governance_copilot/governance_service.py`, add service tests | Coordinate analysis, validation, approval, and both generators without Streamlit dependencies. | Service tests with the deterministic provider, including validation failure and generation only after approval. | Phases 3–5. |
| 7. Streamlit UI | `app.py`, possibly small presentation helpers, README run notes | Deliver transcript loading, analysis, stable result sections, evidence display, approval, and output panes. | Manual smoke test with `uv run streamlit run app.py` through the core path; Ruff and full tests. | Phase 6. |
| 8. Editable human-review workflow | `app.py`, service/models only if validation feedback requires it, add relevant tests | Support edits and removals, validate reviewed data, and invalidate stale approvals/outputs. | Manual test edit/remove/approve/reanalyze paths; automated tests proving outputs use edited data. | Phase 7. |
| 9. Optional real LLM provider | `src/architecture_governance_copilot/extractors.py` or a narrowly scoped provider module, `pyproject.toml` only if an SDK is justified, provider tests, README | Optionally transform arbitrary synthetic transcripts into the same schema without changing deterministic mode. | Mocked provider tests plus one synthetic manual trial; deterministic tests remain fully offline. | Phases 1–8; skip if schedule or credentials are uncertain. |
| 10. Final tests and demo hardening | All tests as needed, `README.md`, `SPEC.md`, `DEMO.md`, fixture/UI wording | Align docs and behavior, fix edge cases, rehearse a sub-four-minute stable demo, and verify no sensitive data. | Run all five documented `uv` commands as applicable, clean-environment smoke test, timed rehearsal, and recording checklist. | Phases 1–8; phase 9 optional. |
