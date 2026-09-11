# Architecture Governance Copilot — Product and Technical Specification

Document role: `CURRENT_PRODUCT_CONTRACT`. This specification describes the implemented baseline
unless a section explicitly says future, optional, or historical. It does not independently define
approved post-baseline implementation scope.

## Document purpose

This document defines a hackathon proof of concept (PoC) for drafting and reviewing a Solution
Intent (SI). The current execution horizon is the repository and sub-four-minute video submission
due on 14 September 2026. The PoC proves one reliable, human-controlled drafting handoff and SI
review round; it is not a production platform.

## Domain context

A Solution Intent is the detailed project design document jointly prepared by the Product Owner
and development team. It normally covers conceptual and detailed design, deployment, resilience,
security, observability, data, and related architecture concerns. In the production process, the
SI is maintained in Confluence and has a corresponding Azure DevOps (ADO) governance ticket.

A Domain Architect reviews the SI over one or more rounds. A round may combine document review,
a meeting, written feedback, required changes, risks, decisions, and open questions. The project
team updates the SI until the Domain Architect approves it, often while software development
continues in parallel.

This PoC models one such review round. Confluence, Teams, AIF, and ADO are future production
integration targets. No live service is connected; opt-in in-memory fakes exercise the bounded
Confluence read, AIF analysis, and ADO Create contracts without network access.

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
produce an editable SI draft for human confirmation and manual transfer. Independently, given an
authoritative synthetic SI snapshot, a synthetic Teams-style review transcript, and explicit
review metadata, confirm their exact manifest and produce a structured proposal containing:

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

Success means the deterministic demo completes these bounded tasks reliably. It does not
mean that the PoC can govern arbitrary projects or replace Domain Architect judgment.

## Core user journeys

The drafting journey is:

1. Choose **Draft a Solution Intent** from the landing page.
2. Open the bundled synthetic project workspace and inspect its available source package.
3. Inspect the read-only governed template and governance metadata; select a repository and
   revision from the authorized synthetic inventory. Add or upload editable supporting evidence,
   select **Save evidence**, then confirm the exact fingerprint-bound source-package manifest.
4. Generate a deterministic SI draft behind the drafting-provider interface.
5. Let a project-team reviewer edit and confirm the draft, inspect its provenance, and download the
   unpublished Markdown artifact for manual transfer.

The governance-review journey is independent:

1. Choose **Review a Solution Intent** from the landing page.
2. Load a named, versioned, authoritative synthetic SI snapshot, a transcript, and review metadata
   in any order.
3. Inspect component provenance and readiness, then explicitly confirm the exact input manifest.
4. Analyze the review using the confirmed SI snapshot, transcript, and review metadata.
5. Display the review outcome, findings, decisions, risks, actions, open questions, and missing
   information.
6. Show supporting SI or transcript evidence for each extracted claim.
7. Allow human review, editing, and removal of proposed items.
8. Let the Domain Architect explicitly confirm the reviewed record for output generation.
9. Generate the structured review record, review minutes, and mock ADO outputs from the
   human-confirmed state.

The implemented UI has a workflow landing page and two local routed progress models: Project
Context → Draft Solution Intent, and Review Inputs → Human Review → Generated Outputs →
Work Item Delivery. Local artifacts complete the review at Generated Outputs; delivery is a
conditional fourth step. Neither
workflow represents the other as skipped, required, or completed.

The MVP performs this journey for one review round only. `review_round` metadata prepares the
record for future tracking, but the application will not compare versions, persist history, or
automatically carry findings between rounds.

## Functional requirements

### Pre-review SI drafting

- Enter drafting explicitly from the workflow landing page and present a local two-step progress
  model for Project Context and Draft Solution Intent.
- Provide a project workspace selector and an authorized synthetic inventory for the bundled
  template, repository revision, supporting evidence, and governance metadata.
- Keep the governed template read-only. Provide separate repository and revision selectors; the
  bundled inventory contains one repository, while the contract supports multiple repositories.
  Live ADO permission discovery remains deferred.
- Start supporting evidence empty. Allow adding, editing, and removing notes or UTF-8 TXT/Markdown
  uploads (at most 10 items, 1 MiB each). Keep uploads in session memory and reject invalid encoding,
  empty content, unsupported extensions, and binary control characters.
- Offer **Add sample evidence** explicitly; never replace custom input with sample content. Record
  user-entered/uploaded provenance, original upload SHA-256 reference, and current content SHA-256.
  User content is not externally verified. Refresh and navigation preserve evidence; reset clears it.
- Allow valid saved custom packages to be confirmed; block unsupported generation on the drafting page. The current
  deterministic provider accepts only its exact sample inputs. Source edits invalidate drafting
  confirmation and artifacts without clearing independent review or publication history.
- Show stable resource IDs, canonical synthetic references, versions or revisions, exact SHA-256
  fingerprints, local validation status, and configured-provider compatibility.
- Treat the project name and governance work-item reference as required, source-controlled,
  read-only metadata.
- Require explicit human confirmation of one exact `Selected Source Package` manifest before
  drafting. Confirmation records inputs and never represents architecture approval.
- Require the template, repository revision, and supporting evidence selected by the current
  deterministic provider; report incomplete or incompatible packages without a fallback.
- Clearly label local validation and make no external synchronization or API calls.
- Accept project name, SI template, selected source-code context, and supporting notes from the
  confirmed package.
- Treat source code as pasted or pre-normalized text; do not clone, scan, or execute repositories.
- Hide draft generation behind a `SolutionIntentDrafter` provider interface.
- Use a deterministic offline provider for the bundled synthetic scenario.
- Produce a validated `SolutionIntentDraft` with explicit assumptions.
- Allow a human to edit the draft before confirmation.
- Present template and supporting-document Markdown as rendered documents with exact source
  available, while repository excerpts remain verbatim code.
- Distinguish the generated draft's Markdown editor from its live rendered preview; after
  confirmation, default to a read-only rendered document with exact Markdown and download.
- Require **Confirm SI draft** before offering provenance and Markdown download.
- Do not populate Review Inputs from a local drafting artifact. A separate review begins empty and
  must acquire its own authoritative source.
- Do not publish to Confluence or claim architecture approval.

### Inputs

- Enter review explicitly from the workflow landing page.
- Load a validated, read-only synthetic SI snapshot with page identity, space, URL, version,
  retrieval time, canonicalizer version, and content fingerprint.
- Load or paste a synthetic Teams-style Domain Architecture review transcript independently.
- Load and edit review metadata independently.
- Permit SI, transcript, and metadata acquisition in any order without clearing unrelated valid
  components.
- Show `Missing`, `Loaded`, `Edited`, `Invalid`, and `Confirmed` readiness where applicable.
- Require explicit confirmation of the exact complete manifest before enabling Analyze.
- Collect or preload basic metadata:
  - project name;
  - SI title and version;
  - current SI status;
  - review-round number;
  - optional ADO governance-ticket ID;
  - optional Domain Architect; and
  - optional review date.
- Reject missing or invalid required input with localized readiness guidance.
- Clearly label all content as synthetic.
- Present the authoritative SI as rendered canonical Markdown with a separate read-only canonical
  source view; keep transcript intake as literal plain text.

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
- Before Human Review, require each quote to occur in its declared source and validate every
  supplied SI section, transcript speaker, and timestamp against the matching source span.
- Assign trusted evidence references locally after validation and reject conflicting reuse of a
  nonempty reference within one analyzed snapshot.

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
- Show a normalized summary of human field changes and exclusions after confirmation without
  treating evidence as an editable field.
- Preserve routed form state during navigation; navigation alone must not invalidate analysis.
- Derive a live, session-local comparison with the analyzed proposal that identifies modified
  fields, exclusions, affected collections, and invalid in-progress values before confirmation.
- Keep excluded items and their evidence visible, label every affected item as unconfirmed, and
  remove pending indicators when values return to their normalized analyzed state.

### Action dates

- Use nullable date inputs for Human Review action due dates, initialized from the analyzed value.
- Provide an explicit Clear due date action; preserve genuine `None` when cleared and deterministic
  ISO serialization in reviewed outputs.
- Preserve dates across routed navigation and apply no unapproved business date bounds.
- Keep finding due dates and existing optional metadata contracts unchanged.

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
- In offline mode, clearly state that no payload is sent to Azure DevOps.
- Show one evidence-to-output comparison using the reviewed action's stable collection index, its
  actual minutes entry, and its matching ADO preview.
- In opt-in internal fake mode only, allow a separately confirmed exact JSON Patch request to pass
  through correlation lookup, at most one in-memory Create call, and GET verification.
- Block stale previews, duplicate or ambiguous correlations, unconfirmed requests, and automatic
  retry after an unknown Create result.
- Present generated review minutes with purpose-labelled rendered and exact Markdown-source views.
- Escape structured values interpolated into generated Markdown so they cannot introduce headings,
  lists, links, HTML blocks, or emphasis; preserve exact values in forms, evidence/source views,
  typed records, and JSON.

### Governed work-item delivery

- Always show Work Item Delivery as review step 4; guard its route with confirmed reviewed outputs.
- Generated Outputs remains locally complete and usable for all delivery states. Normal Back and
  Return navigation preserves outputs, selection, preview, confirmation, and operation history.
- Resolve the configured fake capability against exact manifest/source/provider/transcript/metadata
  facts; never infer capability solely from the visible analysis-mode label. Offline has no target.
- Report Ready, Not applicable, Unavailable, In progress, Succeeded, Failed, or Needs reconciliation
  separately from local completion. Present every confirmed action with readiness and operation state.
- Resolve owner identities only through the authorized stable target mapping. Missing required
  owner/date/parent or unmapped owner/priority/parent blocks preparation with an action-specific
  explanation. Return to Human Review for editable corrections; do not rewrite reviewed ownership.
- Keep project, type, API version, parent, classifications, identities, and priorities read-only.
- Maintain independent delivery selection and one active exact request/confirmation. Preserve
  original analyzed action positions through exclusions as a session-local delivery binding; keep
  provider-neutral output indices compact and evidence unchanged.
- Use original positions for correlation while checking retained legacy compact-index correlations
  before Create. Succeeded, submitting, and unknown operations remain protected through exclusion,
  restoration, reset, and session-schema migration. Known legacy IDs receive GET read-back and remain
  reconciliation-only when they cannot be verified against the current exact request.
- Require Preview Azure DevOps request, separate Confirm request, and Create work item in order.
  Work item summary and Request JSON are peer views of the immutable prepared request, including
  every outgoing field, parent relation, description/evidence, correlation, and binding fingerprint.
- Revalidate every binding at submission, reconcile correlations before one Create, and GET-verify
  the result. Surface prepared, confirmed, submitting, succeeded, definitely failed, and unknown
  states. Unknown results expose correlation and any known ID and cannot be retried directly.
- Revoke the active request after source, result, target, mapping, or selection changes; retain
  per-correlation history independently. This is session-local protection, not durable or exactly-once
  delivery. No live connector, bulk Create, automatic retry, Update, or administration surface exists.

### Deployment-policy foundation

- Resolve immutable environment policy for demo, development, test, or production at application
  entry; normalize profile names and accepted boolean spellings, reject invalid explicit settings,
  and require operator restart for configuration changes. Do not add an administrative surface.
- Preserve the default zero-configuration demo. An absent profile with explicit enabled fake flag
  resolves to development; explicit demo/production with enabled fake is invalid. Development/test
  require the same opt-in flag for fake. Training uses a separate demo deployment.
- Show truthful environment and synthetic status. Hide single-option review selectors.
- Enforce policy before every stage renderer reads state or redirects, and at review runtime and
  delivery capability resolution. Production has no currently accepted providers and exposes only
  an unavailable status, with no synthetic drafting, review, export, or publication path.
- Distinguish invalid configuration from valid-but-unavailable production. Do not echo environment
  values, fabricate live capabilities, or substitute synthetic output on provider failure.
- Retain policy identity in session state; revalidate selected mode and provider identity each
  rerun. Invalidate incompatible packages, analyses, outputs, and confirmations while preserving
  compatible independent workflow state and protected publication history. Require explicit review
  recovery after a disallowed mode; do not silently select Offline from stale state.
- R9a foundation verification does not complete R9b live capability acceptance or authorize release.

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
- **Theme:** use one project-level native Streamlit light theme for the PoC. The application remains
  light under a Dark host preference and exposes no unsupported in-app theme choice. Dark-mode
  support requires a separately approved future refinement.

## Assumptions

- The demo runs locally with Python 3.12 and `uv`.
- One bundled SI and matching transcript are sufficient for the recorded offline scenario; the
  opt-in Internal fake path uses a separate synchronized synthetic package.
- The SI may contain headings and plain text rather than production Confluence markup.
- The transcript contains synthetic speakers and timestamps or line references.
- The Domain Architect reviews and owns the final outcome.
- The ADO ticket identifier is metadata in the offline workflow and a validated parent mapping in
  the fake publication contract.
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
- The exact drafting source manifest must be valid and human-confirmed before generation.
- SI draft generation works deterministically without network access or credentials.
- The draft is editable and requires explicit human confirmation.
- The landing page exposes two independent workflows with truthful local progress and scoped reset.
- A confirmed draft remains an unpublished downloadable artifact and never becomes a review SI.
- Review Inputs uses a read-only authoritative SI snapshot plus independently acquired transcript
  and metadata.
- Analyze remains unavailable until the exact complete manifest is explicitly confirmed.
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
- Pending modifications, exclusions, affected sections, and validation issues are visible before
  confirmation and survive routed Back/Return without becoming an audit or approval record.
- Invalid reviewed data cannot generate outputs.
- Reviewed-record confirmation is explicit and does not imply formal SI approval.
- Analysis and confirmation change the browser route rather than appending the next stage below
  the previous one.
- Generated outputs reflect the edited, confirmed record.
- Markdown-bearing documents have explicit rendered/editor/source roles, while transcripts,
  evidence quotes, repository excerpts, and machine payloads remain literal.
- A normalized change summary identifies edited fields and excluded proposals while retaining the
  provider evidence unchanged.
- Source quotes and supported locators are validated before Human Review, and stale inputs cannot
  regain output eligibility through navigation or edit-and-revert.
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
             \--> Human-confirmed Markdown artifact (not published)

Review Inputs
    |-- authoritative synthetic SI snapshot
    |-- synthetic review transcript
    |-- SolutionIntentReviewContext
    |-- explicit confirmed manifest
    v
Governance service
    |
    +--> GovernanceExtractor
    |       +--> DeterministicDemoExtractor (required)
    |       +--> AifGovernanceExtractor + in-memory fake (opt-in)
    |       \--> Real AIF transport (future internal work)
    |
    +--> Source/reference validation + Pydantic one-round review models
    |
    +--> Review-record / minutes generator
    |
    +--> Mock ADO action work-item generator
    |
    \--> Exact publication coordinator + in-memory ADO fake (opt-in)
```

### Module responsibilities

- `app.py`: common application shell, route configuration, SI-drafting controls, input loading,
  review widgets, read-only evidence, explicit confirmations, output rendering, and state
  transitions.
- `pages/`: thin file-backed route entry points for the landing page, Project Context, SI Drafting,
  Review Inputs, Human Review, Generated Outputs, and Work Item Delivery.
- `ui_support.py`: workflow identity, schema migration, scoped reset, provenance, readiness,
  manifest fingerprint, sample, optional-field, and reviewed-result helpers.
- `models.py`: strict Pydantic enums and models for review-input manifests and one SI review round.
- `si_drafting.py`: drafting-provider protocol, deterministic provider, and drafting service.
- `extractors.py`: provider protocol and deterministic fixture-backed provider.
- `evidence_validation.py`: provider-neutral source-quote, locator, and reference validation.
- `governance_service.py`: separately coordinates extractor analysis and output generation from
  a caller-supplied reviewed result; it does not approve records.
- `minutes_generator.py`: pure deterministic transformation to review minutes.
- `ado_generator.py`: pure deterministic transformation to mock ADO action-work-item payloads.
- `runtime_dependencies.py`: explicit offline/fake mode dependency wiring and provider identity.
- `integrations/`: strict Confluence, AIF, and Azure DevOps boundary contracts plus deterministic
  in-memory fakes; no live transport implementation.
- `publication.py`: exact-preview binding, separate confirmation, reconciliation, single-Create,
  read-back verification, and observable failure-state coordination.
- `samples/`: frozen synthetic SI, review metadata, transcript, and expected result fixtures.
- `tests/`: validation and transformation tests independent of external services.

Streamlit session state is the only runtime state. It holds the authorized drafting inventory,
source selections, live and confirmed source-package manifests, drafting context and draft,
human-confirmed SI content, the review inputs, latest analysis, independent review draft,
validated reviewed record, generated outputs, errors, input fingerprints, durable in-progress
review fields, and active route stage. It does not hold or simulate review history.

## Model design

All models inherit one small strict base configuration with `extra="forbid"` and whitespace
normalization. Required strings reject blank values after trimming. Dates use `datetime.date`.
Collection defaults use independent factories. All models serialize with
`model_dump(mode="json")`.

### SI-drafting models

- `DraftingSourceResource` and `DraftingSourceInventory` identify authorized local resources with
  roles, references, revision kinds, exact content fingerprints, validation status, provenance,
  and content.
- `SelectedDraftingSource` and `DraftingSourcePackageManifest` retain immutable, content-independent
  identities for the exact human-confirmed provider package.
- `SolutionIntentDraftRequest` contains required `project_name`, required template text,
  required selected source-code context, and structurally optional supporting-document context.
  The configured deterministic provider requires the exact bundled supporting context.
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

This remains the provider-neutral preview model. Conversion to an exact Create request is exercised
only by the in-memory fake publication path; real API submission remains future internal work.

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
Draft eligibility and stale-result detection additionally bind the canonical request to the
confirmed source-package fingerprint and provider configuration identity without changing this
provider protocol.

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
generate downstream outputs. `GovernanceExtractor` is a synchronous structural protocol. The
fixture-backed `DeterministicDemoExtractor` is the required offline implementation; the opt-in
`AifGovernanceExtractor` is exercised only with an in-memory fake transport in this repository.

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

The opt-in Internal fake runtime uses a distinct 1,083-word Synthetic Order Routing Service SI,
28 timestamped transcript lines across four fictional roles, and a fixed fake AIF response. The
response contains three findings, one decision, one risk, two actions, one open question, and two
missing-evidence items. The fake Confluence storage body canonicalizes exactly to the committed
Markdown snapshot, and every proposed item is validated against exact SI or transcript evidence
before locally trusted references are assigned. The richer package exercises the provider-shaped
contracts and Human Review surface; it does not make a network request or support arbitrary input.

## Main technical and demo risks

| Risk | Mitigation |
| --- | --- |
| Draft generation overstates what source code proves | Use selected synthetic excerpts, preserve explicit gaps, show assumptions, and require human review. |
| Sensitive repositories or documents are uploaded | Do not clone, scan, or execute repositories in the PoC; use synthetic pasted context only. |
| A generated SI appears published, authoritative, or approved | Label it as an unpublished draft, require human confirmation, and keep authoritative review-source acquisition separate. |
| Findings are not traceable to the SI | Require typed evidence and map findings to SI sections where supported. |
| Transcript is treated as the reviewed object | Keep SI content visually primary and require both documents as analysis inputs. |
| The tool appears to approve architecture autonomously | Label the action as reviewed-record confirmation and state that formal decisions remain with the Domain Architect. |
| Fixture and model drift | Validate the complete expected result in automated tests. |
| Streamlit reruns lose reviewed state | Define explicit state transitions and invalidate stale outputs. |
| Generated outputs ignore human edits | Generate only from the validated reviewed model and test edited values. |
| ADO previews look like live updates | Keep offline previews explicitly local; label fake publication as in-memory/no-network and require a second exact-preview confirmation. |
| Provider evidence is plausible but unsupported | Match exact quotes and supported locators against immutable source snapshots before Human Review. |
| Create is duplicated or times out ambiguously | Reconcile by correlation before Create, never retry automatically, and retain `unknown_result` for manual reconciliation. |
| Multi-round capability expands the MVP | Store only `review_round`; exclude history, comparison, and resolution logic. |
| Video exceeds four minutes | Use one round, one key finding, one decision, one risk, two actions, and one open item. |
| Network or LLM failure | Record in deterministic offline mode. |
| Confidential data enters the demo | Use obviously fictional project, document, and people data only. |

## Historical implementation summary

Document status: `HISTORICAL_SUMMARY`. This table is retained to explain how the current product was
built. It is not an active execution plan; incomplete or optional entries require current change
approval and a bounded execution plan.

| Phase | Files | Expected outcome | Verification | Depends on |
| --- | --- | --- | --- | --- |
| 0. Optional deterministic SI drafting (complete) | `si_drafting.py`, drafting models, synthetic context, drafting route, tests | Generate, edit, confirm, and download a known synthetic SI without treating it as an authoritative review source. | Provider mismatch tests, state-isolation tests, Streamlit end-to-end test. | Existing review PoC. |
| 1. SI domain models and tests (complete) | `models.py`, `test_models.py` | Strict models for one SI review round, findings, and dual-source evidence. | Model tests, Ruff. | Planning. |
| 2. Synthetic SI, transcript, metadata, and expected result (complete) | `samples/`, `test_sample_data.py` | One internally consistent fictional review-round fixture. | Validate JSON, models, scenario counts, safety, and every evidence quote. | Phase 1. |
| 3. Deterministic provider (complete) | `extractors.py`, `test_extractors.py` | Match both sources and return the known validated result offline. | Match, mismatch, repeatability, and corrupt-fixture tests. | Phases 1–2. |
| 4. Review minutes generator (complete) | `minutes_generator.py`, generator tests | Stable minutes covering context, findings, and evidence. | Deterministic content assertions. | Phases 1–2. |
| 5. Mock ADO action generator (complete) | `ado_generator.py`, generator tests | One typed mock work item per action; parent-ticket update remains future work. | Mapping, counts, nulls, SI section, and criteria tests. | Phases 1–2. |
| 6. Governance service (complete) | `governance_service.py`, service tests | Keep extractor analysis separate from generation using a caller-supplied reviewed result. | Delegation, separation, edit-preservation, exception, and independence tests. | Phases 3–5. |
| 7. Streamlit UI (complete) | `app.py`, `pages/`, `ui_support.py`, UI tests | Choose between independent drafting and review workflows, confirm an exact review-input manifest, show seven editable sections with evidence, and display reviewed outputs. | Streamlit `AppTest`, route-guard tests, pure support tests, and headless startup. | Phase 6. |
| 8. Editable human review (complete) | `app.py`, `ui_support.py`, focused tests | Edit/exclude items, validate a reconstructed result, and prevent stale generation. | Edit, exclusion, validation, mutation, reset, and stale-input tests. | Phase 7. |
| 9. Optional real LLM provider (not implemented or authorized) | Provider module/tests, dependency only if justified | Analyze arbitrary synthetic SI reviews without changing deterministic mode. | Mocked API tests and one synthetic trial. | Phases 1–8; optional. |
| 10. Final hardening (complete for the frozen baseline) | Tests and docs | Clean setup, stable demo, and aligned implementation documentation. | Full `uv` checks and verified browser scenarios recorded in `docs/SUBMISSION_BASELINE.md`. | Phases 1–8. |

Multi-round tracking, version comparison, and finding resolution are deliberately absent from
this plan's MVP phases.

Evidence changes require **Save evidence** before **Confirm Context & Continue**. Saving is local to
the session; the visible status changes back to unsaved after editing, adding, or removing content.
Valid saved custom evidence can reach the drafting step. There, unsupported inputs disable
**Generate SI Draft** with an explanation; no sample output is substituted.
