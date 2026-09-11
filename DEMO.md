# Architecture Governance Copilot — Demo Plan

Document role: `VERIFIED_BASELINE_DEMO_PROCEDURE`. This file demonstrates the checked-out baseline;
it does not authorize application changes or define future implementation scope.

## Demo objective

In less than four minutes, demonstrate the independent governance-review workflow: acquire a
versioned authoritative synthetic Solution Intent, transcript, and metadata; confirm their exact
manifest; produce a source-backed governance proposal; let a human reviewer edit and confirm the
record; and generate review minutes plus Azure DevOps work-item previews. Briefly show that SI
drafting is a separate peer workflow. Formal governance decisions remain with the Domain Architect.

The target runtime is **3 minutes 35 seconds**, leaving a 25-second safety margin. The demo does
not show a second review round.

The landing page exposes **Draft a Solution Intent** and **Review a Solution Intent** as peer
tasks. The recording follows the three-step review path: **Review Inputs → Human Review → Generated
Outputs**. Drafting has its own two-step path and never supplies an authoritative review source.

## Synthetic scenario

The fictional **Digital Payment Notification Service** team has prepared version **1.2** of its
Solution Intent. Its status is `under_review`, and the demo covers review round 2 only. Fictional
Domain Architect **Jordan Lee** reviews the SI with Lead Developer **Alex Chen** and Product
Owner **Priya Shah** in a Teams-style meeting.

The finalized synthetic SI contains concise sections for:

- Document Information
- Executive Summary
- Scope
- Conceptual Architecture
- Detailed Application Design
- Data Design
- Availability and Resilience
- Security
- Observability
- Deployment Design
- Operational Support
- Assumptions and Open Items

The review scenario must yield:

- a **Changes Requested** outcome;
- three open findings covering traffic failover, missing RTO/RPO values, and production support
  ownership;
- the traffic-failover finding mapped to **Availability and Resilience**;
- one confirmed decision accepting managed PostgreSQL as the system of record;
- one risk that pending production database sizing may affect the planned August release;
- two actions:
  - Alex updates the resilience section and deployment diagram by 24 July 2026;
  - Priya confirms RTO and RPO values by 25 July 2026;
- one unresolved question about whether Redis should be used;
- missing RTO/RPO values and production support ownership; and
- evidence drawn from both the SI and the review transcript.

The record may contain more supporting detail, but the recording should focus on these items. All
names, documents, ticket IDs, dates, and quotes must be obviously synthetic.

### Optional Internal fake acceptance rehearsal

The opt-in Internal fake path uses a separate **Synthetic Order Routing Service** package and is
not part of the primary four-minute recording. Its 1,083-word version 0.8 SI is represented by fake
Confluence page `synthetic-page-204` version 8, and its 28-line transcript contains four fictional
roles. The fixed fake AIF result proposes three findings, one decision, one risk, two actions, one
open question, and two missing-evidence items.

When rehearsing this path, enable it explicitly, load the three input components in a non-default
order, confirm the exact manifest, inspect every Human Review collection, and restore any test edit
or exclusion before confirmation. On Generated Outputs, select **Continue to Work Item Delivery**.
Verify that both actions are Ready with mapped owners, dates, priorities, and parent 204. Select
an action, choose **Preview Azure DevOps request**, inspect **Work item summary** and **Request JSON**,
then **Confirm request → Create work item**. Verify the receipt and GET read-back. Repeat separately
for the other action and confirm both receipts survive Back/Return navigation. Test an unmapped
owner and a cleared date by returning to Human Review, regenerating outputs, inspecting the named
blockers, and restoring the mapped values. Excluding the preceding action must never permit an
already succeeded or unknown surviving action to be created again. State that
the entire path is synthetic and no-network; its greater fixture depth does not demonstrate live
enterprise connectivity or general semantic extraction.

## Preconditions

- Use a clean local checkout with the finalized synthetic fixtures.
- Complete `uv sync` before recording.
- Start the app with `uv run streamlit run app.py` in the default demo profile.
- For fake rehearsal, use development/test with explicit `AGC_INTERNAL_FAKE_ENABLED=1`.
  The legacy flag-only command also resolves to development. Do not enable fake in explicit demo.
- Production is an unavailable policy screen, not a demonstration or a production-ready deployment.
- Use **Deterministic demo mode**.
- Reset Streamlit session state before the take.
- Use the rehearsed browser resolution and zoom.
- Disable notifications and close unrelated or sensitive applications.
- Confirm that the workflow works with network access disabled.

## Exact click-by-click workflow and expected state

### Step 1 — Launch the application

**Action:** Start `uv run streamlit run app.py` and open the local Streamlit URL.

**Expected state:**

- **Architecture Governance Copilot** and the Solution Intent review subtitle are visible.
- A single global disclosure states **Demo Mode · Synthetic Data · No External Connections**.
- The workflow landing page is active.
- Both peer workflow choices are visible.
- Briefly note that drafting opens an authorized synthetic inventory and requires confirmation of
  an exact fingerprint-bound `Selected Source Package`; it does not scan or contact a repository.
- No analysis or outputs are displayed.

### Step 2 — Enter the governance-review workflow

**Action:** Point out **Draft a Solution Intent**, then click **Review a Solution Intent**.

**Expected state:**

- The browser navigates to **Review step 1 — Review Inputs**.
- Review progress contains Review Inputs, Human Review, Generated Outputs, and conditional
  Work Item Delivery. Local completion remains at Generated Outputs.
- Offline demo mode is selected and no source is implied to be loaded.
- Analyze is disabled.

### Step 3 — Acquire the review package in independent parts

**Click:** **Load synthetic transcript**, then **Load synthetic metadata**, then **Load authoritative
SI snapshot**.

**Expected state:**

- Component loading works in any order and does not clear already valid inputs.
- The SI is read-only and exposes synthetic page identity, version, retrieval time, canonicalizer,
  and content fingerprint.
- The SI opens in **Rendered** form and exposes **Canonical Markdown source** for exact inspection.
- Transcript and metadata remain separately editable.
- Readiness shows all three components as loaded, while Analyze remains disabled.

### Step 4 — Confirm the exact review-input manifest

**Click:** **Confirm review input manifest**.

**Expected state:**

- SI, transcript, and metadata each show **Confirmed**.
- The exact source, transcript, metadata, mode, and provider identity are fingerprint-bound.
- **Analyze review** becomes enabled only after confirmation.
- No output is generated and no source is published.

### Step 5 — Analyze the review

**Click:** **Analyze Review**.

**Expected state:**

- A short processing panel validates the review package, runs governance extraction, and prepares
  the human-review workspace.
- Analysis completes after an intentional approximately 1.2-second deterministic demo transition.
- The browser navigates to `/human-review`.
- The progress indicator advances to review step 2.
- **Review step 2 — Human Review** replaces the full input view.
- A compact analyzed-input summary and **Draft Structured Review** appear.
- Outcome shows **Changes Requested**.
- Metrics show one decision, three findings, one risk, two actions, one open question, and two
  missing-information entries.
- Counted tabs organize Decisions, Findings, Risks, Actions, Questions, and Missing Information.
- **Pending human changes** explicitly reports that current values still match the analyzed
  proposal.
- Every required item offers supporting evidence.
- No generated minutes or ADO work items appear automatically.

### Step 6 — Review the outcome and counts

**Action:** Point to **Changes Requested** and scan the seven summary metrics.

**Expected state:**

- The structured proposal is clearly labeled draft.
- Human review is visibly separated from deterministic analysis.

### Step 7 — Make a human edit

**Action:** Open **Actions · 2** and change the first action owner from **Alex Chen** to
**Taylor Kim**.

**Expected state:**

- The edited owner remains in the form.
- The pending summary reports one modified field and the Actions tab/item show one unconfirmed
  pending item.
- Evidence remains visible and unchanged.
- The record remains a human-reviewed draft, not a formal SI approval.

### Step 8 — Exclude the production-support finding

**Click:** Open **Findings · 3**, then clear **Include in reviewed record** for **Undefined
production support ownership**.

**Expected state:**

- The finding's evidence remains read-only in the current form.
- The finding is marked for omission from the reviewed result.
- The pending summary and Findings tab update, and the still-visible item is labelled excluded and
  unconfirmed.
- **Production support ownership is not specified** remains in Missing Information, so excluding
  the proposed finding does not create a misleadingly clean record.

### Step 9 — Confirm the reviewed record

**Click:** **Confirm Reviewed Record & Generate Outputs**.

**Expected state:**

- A short processing panel validates the human-reviewed record, generates minutes, and prepares
  two Azure DevOps work-item previews.
- The UI confirms output generation without claiming formal SI approval.
- The browser navigates to `/generated-outputs`.
- The progress indicator advances to review step 3.
- **Review step 3 — Generated Outputs** replaces the edit form.
- A **Governance package ready** completion panel clearly marks the workflow as complete.
- Summary cards show completion, outcome, one minutes artifact, and the work-item preview count.
- **Start New Review** provides a deliberate reset for the next rehearsal.
- The reviewed record excludes the production-support finding but retains the matching missing
  information.
- Two action work-item previews remain because no action was excluded.
- Nothing is sent to an external service.

### Step 10 — Show the generated minutes

**Action:** Show the **Rendered** view, then briefly select **Markdown source**.

**Expected state:**

- The generated record shows **Changes Requested** and the edited action owner.
- The Human Review change summary shows the owner edit and the excluded production-support
  finding.
- The evidence-to-output comparison shows the original source quote beside the Taylor Kim action,
  its actual minutes entry, and its matching ADO preview.
- The accountability notice says the record must be reviewed before publication.

### Step 11 — Show the Azure DevOps work-item previews

**Action:** Scroll to **Azure DevOps Work Item Previews**.

**Expected state:**

- Exactly two work-item preview cards are visible.
- The first item is assigned to **Taylor Kim**.
- Parent ID, due dates, priorities, tags, descriptions, and source indices are visible.
- The page states: **No real Azure DevOps work item has been created.**

### Step 12 — Close on accountability and scope

**Action:** Return to the completion panel and point to **Start New Review** without clicking it.

**Expected state:**

- The complete human-controlled one-round workflow is clear.
- The completion state and optional restart action are unambiguous.
- Each workflow stage has a dedicated view with Back and Reset navigation.
- Demo mode, synthetic data, and the preview-only integration disclosure remain visible.
- Formal governance responsibility remains with the Domain Architect.
- There is no review history, second round, SI diff, or automatic finding resolution.

## Preliminary narration

1. “A Solution Intent is the project's detailed architecture design. This PoC starts by drafting
   one from a synthetic template, selected code context, and supporting notes.”
2. “Drafting and review are separate tasks. Review starts from its own authoritative, read-only SI
   snapshot rather than a locally generated draft.”
3. “We can acquire the transcript, metadata, and SI in any order, but analysis stays disabled until
   a human confirms the exact manifest.”
4. “This finding maps back to the SI's Availability and Resilience section, and its evidence
   includes both the document and the meeting.”
5. “The machine proposes the record; the Domain Architect remains responsible for review and
   formal approval.”
6. “I’ll change one action owner and exclude the production-support finding; the underlying
   missing information remains visible.”
7. “Only the validated, human-reviewed state generates minutes and Azure DevOps work-item
   previews.”
8. “There is no live Confluence, Teams, or Azure DevOps integration and no multi-round workflow
   in this MVP.”

## Video structure

| Time | Segment | Focus |
| --- | --- | --- |
| 0:00–0:20 | Problem and scope | SI governance problem, one-round PoC, human accountability. |
| 0:20–0:35 | Choose workflow | Show the two peer tasks and enter Review. |
| 0:35–1:10 | Review inputs | Load three components independently and confirm the manifest. |
| 1:10–1:40 | Analyze | Show Changes Requested, counts, and read-only evidence. |
| 1:40–2:15 | Human review | Edit one owner, exclude one finding, and emphasize human control. |
| 2:15–3:15 | Confirm and generate | Show rendered/raw minutes and two ADO work-item previews. |
| 3:15–3:35 | Close | State real versus mocked scope and no multi-round behavior. |

Hard stop at 3:35. Do not show environment setup, code, a second review round, optional LLM mode,
or every output field.

## What is real and what is mocked

### Real in the PoC

- Loading local synthetic SI and transcript content.
- Generating a fixture-backed SI draft from local synthetic context.
- Validating one-round review metadata and results with Pydantic.
- Distinguishing SI evidence from transcript evidence.
- Mapping findings to SI sections where supported.
- Showing findings, decisions, risks, actions, questions, and missing information.
- Editing and removing proposed review items in the session.
- Guided one-stage-at-a-time navigation with workflow-local progress.
- Explicit human confirmation before output generation.
- Generating deterministic structured output and minutes from the reviewed record.
- Generating local JSON-ready mock ADO action work items.
- Showing normalized human changes and tracing an action from immutable evidence into minutes and
  its ADO preview.
- Automated validation and transformation tests.

### Mocked or simulated

- The SI resembles content normally held in Confluence but is loaded locally.
- The transcript resembles Teams output but is loaded locally.
- Deterministic analysis returns a curated fixture for the bundled pair.
- Offline ADO action work items are previews and are never submitted. An opt-in development mode
  can send an exact separately confirmed request only to an in-memory fake gateway.
- No identity, authorization, persistence, audit history, or production operations exist.
- The `review_round` field does not implement multi-round tracking.

## Deterministic demo mode

- It is the default and required recording mode.
- It matches both bundled inputs and validated metadata.
- It returns a known `GovernanceResult` fixture.
- It requires no LLM, API key, SDK, network, Confluence page, Teams meeting, or ADO account.
- It fails clearly when either input does not match the sample.
- The narration must disclose that it is fixture-backed.
- It proves review, traceability, human control, and downstream generation—not general-purpose
  extraction intelligence.

## Failure fallbacks

| Failure | Response |
| --- | --- |
| App is not running | Restart with the documented `uv` command and begin a new take. |
| SI or transcript does not load | Reload the affected component and restart the take if needed. |
| Deterministic input mismatch | Reload both bundled inputs without editing them before Analyze. |
| Analysis fixture fails validation | Stop; align models and fixture before recording. |
| An edit is lost | Stop; repair session-state behavior before making the human-review claim. |
| Confirmation is blocked | Restore the rehearsed valid edit or reanalyze; never bypass validation. |
| Outputs ignore the edit | Stop; fix generation from reviewed state before recording. |
| Provider fails | Stop the affected review. Never substitute synthetic results; begin a separately labelled demo session deliberately if needed. |
| Layout hides evidence | Restore rehearsed zoom and collapse unrelated sections. |
| Runtime approaches 3:35 | Stop and record a shorter take; preserve evidence and confirmation steps. |
| Network disconnects | Continue; deterministic mode is offline. |

## Recording checklist

### Content

- [ ] SI, transcript, people, ticket, and dates are synthetic.
- [ ] Only one review round—round 2—is shown.
- [ ] The landing page shows the two peer workflows.
- [ ] Review progress contains three local artifact steps and a conditional Work Item Delivery step.
- [ ] Transcript, metadata, and SI are loaded independently.
- [ ] The authoritative SI is read-only and versioned.
- [ ] Analyze stays disabled until the exact manifest is confirmed.
- [ ] Changes Requested is shown.
- [ ] At least one finding maps to an SI section.
- [ ] One confirmed decision is visible.
- [ ] One risk is visible.
- [ ] Two actions are visible.
- [ ] The production-support finding is visible before exclusion and absent from generated
  findings, while its Missing Information entry remains.
- [ ] SI and transcript evidence are both demonstrated.
- [ ] The human edit persists.
- [ ] Outputs remain hidden until reviewed-record confirmation.
- [ ] Generated outputs reflect the edit.
- [ ] ADO content is clearly labeled preview-only and not submitted.

### Technical rehearsal

- [ ] `uv sync` succeeds.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check .` passes.
- [ ] `uv run ruff format --check .` passes.
- [ ] `uv run streamlit run app.py` starts the implemented app.
- [ ] Deterministic mode works offline.
- [ ] The exact click path succeeds twice before recording.

### Recording safety and quality

- [ ] Rehearsal is 3:35 or shorter.
- [ ] Notifications and unrelated applications are closed.
- [ ] No credentials, secrets, account data, or confidential material are visible.
- [ ] Text is legible at the recording resolution.
- [ ] Cursor movement and scrolling are easy to follow.
- [ ] Audio is clear.
- [ ] Narration states synthetic data, offline analysis, human control, and preview-only outputs.
- [ ] Final video is shorter than four minutes.
- [ ] Exported video is played through once before submission.
- [ ] Submission requirements and the 14 September 2026 deadline are confirmed.
