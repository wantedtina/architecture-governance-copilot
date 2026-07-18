# Architecture Governance Copilot — Demo Plan

## Demo objective

In less than four minutes, demonstrate one reliable Solution Intent review round: load a
synthetic SI and its review transcript, produce a source-backed review proposal, let a human
reviewer edit and confirm the record, and generate review minutes plus mock Azure DevOps outputs.
Formal governance decisions remain with the Domain Architect.

The target runtime is **3 minutes 35 seconds**, leaving a 25-second safety margin. The demo does
not show a second review round.

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

## Preconditions

- Use a clean local checkout with the finalized synthetic fixtures.
- Complete `uv sync` before recording.
- Start the app with `uv run streamlit run app.py`.
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
- The page states that the PoC uses synthetic data.
- Deterministic demo mode is clearly identified.
- SI and transcript areas are empty.
- No analysis or outputs are displayed.

### Step 2 — Load the complete sample

**Click:** **Load Sample Review**.

**Expected state:**

- The SI area contains the Digital Payment Notification Service SI with visible section headings.
- The transcript area contains the matching synthetic review meeting.
- Review metadata identifies SI version 1.2, status `under_review`, round 2, and governance ticket
  `ARCH-POC-1024`.
- A visible message confirms that the synthetic sample is loaded.
- No result is displayed yet.

### Step 3 — Inspect the inputs

**Action:** Briefly switch between the **Solution Intent** and **Review Transcript** tabs.

**Expected state:**

- The SI headings and synthetic disclaimer are visible.
- The transcript preserves speaker names, timestamps, and line breaks.
- The metadata remains visible without exposing local file paths.

### Step 4 — Analyze the review

**Click:** **Analyze Review**.

**Expected state:**

- Analysis completes quickly in deterministic mode.
- **Stage 2 — Human Review** and **Draft Structured Review** appear.
- Outcome shows **Changes Requested**.
- Metrics show one decision, three findings, one risk, two actions, one open question, and two
  missing-information entries.
- Every required item offers supporting evidence.
- No generated minutes or ADO work items appear automatically.

### Step 5 — Review the outcome and counts

**Action:** Point to **Changes Requested** and scan the seven summary metrics.

**Expected state:**

- The structured proposal is clearly labeled draft.
- Human review is visibly separated from deterministic analysis.

### Step 6 — Make a human edit

**Action:** Change the first action owner from **Alex Chen** to **Taylor Kim**.

**Expected state:**

- The edited owner remains in the form.
- Evidence remains visible and unchanged.
- The record remains a human-reviewed draft, not a formal SI approval.

### Step 7 — Exclude the Redis question

**Click:** Clear **Include in reviewed record** for the Redis open question.

**Expected state:**

- The Redis evidence remains read-only in the current form.
- The question is marked for omission from the reviewed result.

### Step 8 — Confirm the reviewed record

**Click:** **Confirm Reviewed Record & Generate Outputs**.

**Expected state:**

- The UI confirms validation and output generation without claiming formal SI approval.
- **Stage 3 — Generated Outputs** appears.
- The reviewed record excludes the Redis question.
- Two mock action work items remain because no action was excluded.
- Nothing is sent to an external service.

### Step 9 — Show the generated minutes

**Action:** Show the **Rendered Markdown** view, then briefly select **Raw Markdown**.

**Expected state:**

- The generated record shows **Changes Requested** and the edited action owner.
- Redis is absent.
- The accountability notice says the record must be reviewed before publication.

### Step 10 — Show the mock ADO work items

**Action:** Scroll to **Mock Azure DevOps Work Items**.

**Expected state:**

- Exactly two mock work-item cards are visible.
- The first item is assigned to **Taylor Kim**.
- Parent ID, due dates, priorities, tags, descriptions, and source indices are visible.
- The page states: **No real Azure DevOps work item has been created.**

### Step 11 — Close on accountability and scope

**Action:** Position the page so the generated-record notice and mock-integration notice are
visible.

**Expected state:**

- The complete human-controlled one-round workflow is clear.
- Synthetic data, deterministic mode, and mock integrations remain visible.
- Formal governance responsibility remains with the Domain Architect.
- There is no review history, second round, SI diff, or automatic finding resolution.

## Preliminary narration

1. “A Solution Intent is the project's detailed architecture design. Domain Architects review it
   over one or more rounds, but this PoC deliberately proves one round.”
2. “One click loads the synthetic SI, matching transcript, and review metadata.”
3. “Deterministic offline analysis combines both sources into a structured review proposal.”
4. “This finding maps back to the SI's Availability and Resilience section, and its evidence
   includes both the document and the meeting.”
5. “The machine proposes the record; the Domain Architect remains responsible for review and
   formal approval.”
6. “I’ll change one action owner and exclude the unresolved Redis question.”
7. “Only the validated, human-reviewed state generates minutes and mock ADO work items.”
8. “There is no live Confluence, Teams, or Azure DevOps integration and no multi-round workflow
   in this MVP.”

## Video structure

| Time | Segment | Focus |
| --- | --- | --- |
| 0:00–0:20 | Problem and scope | SI governance problem, one-round PoC, human accountability. |
| 0:20–0:45 | Load inputs | Load the complete sample and inspect both tabs. |
| 0:45–1:25 | Analyze | Show Changes Requested, counts, and read-only evidence. |
| 1:25–2:05 | Human review | Edit one owner, exclude Redis, and emphasize human control. |
| 2:05–3:10 | Confirm and generate | Show rendered/raw minutes and two mock ADO items. |
| 3:10–3:35 | Close | State real versus mocked scope and no multi-round behavior. |

Hard stop at 3:35. Do not show environment setup, code, a second review round, optional LLM mode,
or every output field.

## What is real and what is mocked

### Real in the PoC

- Loading local synthetic SI and transcript content.
- Validating one-round review metadata and results with Pydantic.
- Distinguishing SI evidence from transcript evidence.
- Mapping findings to SI sections where supported.
- Showing findings, decisions, risks, actions, questions, and missing information.
- Editing and removing proposed review items in the session.
- Explicit human confirmation before output generation.
- Generating deterministic structured output and minutes from the reviewed record.
- Generating local JSON-ready mock ADO action work items.
- Automated validation and transformation tests.

### Mocked or simulated

- The SI resembles content normally held in Confluence but is loaded locally.
- The transcript resembles Teams output but is loaded locally.
- Deterministic analysis returns a curated fixture for the bundled pair.
- ADO action work items are previews and are never submitted.
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
| SI or transcript does not load | Refresh once, reload both samples, and restart the take if needed. |
| Deterministic input mismatch | Reload both bundled inputs without editing them before Analyze. |
| Analysis fixture fails validation | Stop; align models and fixture before recording. |
| An edit is lost | Stop; repair session-state behavior before making the human-review claim. |
| Confirmation is blocked | Restore the rehearsed valid edit or reanalyze; never bypass validation. |
| Outputs ignore the edit | Stop; fix generation from reviewed state before recording. |
| Optional LLM fails | Return to deterministic mode; the primary path never depends on it. |
| Layout hides evidence | Restore rehearsed zoom and collapse unrelated sections. |
| Runtime approaches 3:35 | Stop and record a shorter take; preserve evidence and confirmation steps. |
| Network disconnects | Continue; deterministic mode is offline. |

## Recording checklist

### Content

- [ ] SI, transcript, people, ticket, and dates are synthetic.
- [ ] Only one review round—round 2—is shown.
- [ ] **Load Sample Review** populates both source tabs and metadata.
- [ ] Changes Requested is shown.
- [ ] At least one finding maps to an SI section.
- [ ] One confirmed decision is visible.
- [ ] One risk is visible.
- [ ] Two actions are visible.
- [ ] The Redis question is visible before exclusion and absent from generated minutes.
- [ ] SI and transcript evidence are both demonstrated.
- [ ] The human edit persists.
- [ ] Outputs remain hidden until reviewed-record confirmation.
- [ ] Generated outputs reflect the edit.
- [ ] ADO content is clearly labeled mock.

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
- [ ] Narration states synthetic data, deterministic analysis, human control, and mock outputs.
- [ ] Final video is shorter than four minutes.
- [ ] Exported video is played through once before submission.
- [ ] Submission requirements and 22 July 2026 deadline are confirmed.
