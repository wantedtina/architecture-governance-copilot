# Architecture Governance Copilot — Demo Plan

## Demo objective

In less than four minutes, demonstrate one reliable Solution Intent review round: load a
synthetic SI and its review transcript, produce a source-backed review proposal, let a human
Domain Architect edit and approve the record, and generate review minutes plus mock Azure DevOps
outputs.

The target runtime is **3 minutes 35 seconds**, leaving a 25-second safety margin. The demo does
not show a second review round.

## Synthetic scenario

The fictional **Project Northstar** team has prepared version **0.4** of the **Northstar Customer
Portal Solution Intent**. Its status is `under_review`, and this is review round 1. A fictional
Domain Architect reviews the SI with the Product Owner and development team in a Teams-style
meeting.

The synthetic SI should contain concise sections for:

- Conceptual Design
- Deployment Design
- Resilience and Recovery
- Security
- Observability
- Data Design

The review scenario must yield:

- a **Changes Requested** outcome;
- one high-severity finding mapped to **Resilience and Recovery** because regional failover is
  incomplete;
- one confirmed decision to put the public API behind Azure API Management;
- one risk that regional failover has not been demonstrated;
- two actions:
  - document the regional failover sequence and attach evidence;
  - update the Security section with the agreed managed-identity flow;
- one unresolved governance item asking the business to confirm the recovery-time objective;
- missing failover-test evidence; and
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

### Step 1 — Open the application

**Action:** Open the local Streamlit URL.

**Expected state:**

- **Architecture Governance Copilot** and **Solution Intent Review** are visible.
- The page states that the PoC uses synthetic data.
- Deterministic demo mode is clearly identified.
- SI and transcript areas are empty.
- No analysis or outputs are displayed.

### Step 2 — Load the Solution Intent

**Click:** **Load Sample Solution Intent**.

**Expected state:**

- The SI area contains the Northstar SI with visible section headings.
- Review metadata identifies Project Northstar, SI version 0.4, status `under_review`, and round
  1.
- The SI is visually the primary object under review.
- No result is displayed yet.

### Step 3 — Load the review transcript

**Click:** **Load Sample Review Transcript**.

**Expected state:**

- The transcript area contains one synthetic Domain Architecture review meeting.
- Synthetic speakers and timestamps or references are visible.
- Both inputs are now present.
- **Analyze Review** is enabled.

### Step 4 — Analyze the review

**Click:** **Analyze Review**.

**Expected state:**

- Analysis completes quickly in deterministic mode.
- These sections appear in order:
  1. Review Outcome
  2. Review Findings
  3. Decisions
  4. Risks
  5. Action Items
  6. Open Questions
  7. Missing Information
- Outcome shows **Changes Requested**.
- The failover finding shows **Resilience and Recovery** as its SI section.
- One decision, one risk, two actions, and the unresolved recovery objective are visible.
- Every required item offers supporting evidence.
- No minutes or ADO outputs appear before approval.

### Step 5 — Inspect both evidence sources

**Click:** Expand the failover finding's evidence.

**Expected state:**

- One quote is labeled **Solution Intent** with section **Resilience and Recovery**.
- One quote is labeled **Meeting Transcript** with a speaker and timestamp.
- The evidence supports the finding without implying a live Confluence or Teams connection.

### Step 6 — Perform human review

**Action:** Edit the first action title to the rehearsed wording:
**Document regional failover and attach test evidence**.

**Expected state:**

- The edited wording persists.
- Evidence remains visible and unchanged.
- The record remains unapproved.
- The page identifies the Domain Architect as the human approver.

Optionally remove one low-value duplicate proposal only if the finalized fixture contains one.
Do not add this interaction if it risks exceeding the time budget.

### Step 7 — Approve the review record

**Click:** **Approve SI Review Record**.

**Expected state:**

- The UI confirms human approval of the review record.
- It does not claim that an AI approved the Solution Intent.
- A **Structured SI Review Record** section appears.
- **Review Meeting Minutes** appears.
- **Mock Azure DevOps Outputs** appears.
- The minutes contain the edited action wording.
- The mock ADO parent update references the synthetic governance ticket.
- Two mock action work items are shown and linked to the parent ID where available.
- Relevant work items show SI-section and acceptance-criteria context.
- Nothing is sent to an external service.

### Step 8 — Close on scope

**Action:** Position the page so the approved outputs and mock labels are visible.

**Expected state:**

- The complete one-round workflow is clear.
- Synthetic data, deterministic mode, and mock integrations remain visible.
- There is no review history, second round, SI diff, or automatic finding resolution.

## Preliminary narration

1. “A Solution Intent is the project's detailed architecture design. Domain Architects review it
   over one or more rounds, but this PoC deliberately proves one round.”
2. “I’ll load a synthetic SI first, then the supporting review transcript and metadata.”
3. “Deterministic offline analysis combines both sources into a structured review proposal.”
4. “This finding maps back to the SI's Resilience and Recovery section, and its evidence includes
   both the document and the meeting.”
5. “The machine proposes the record; the Domain Architect remains responsible for review and
   formal approval.”
6. “I’ll edit one action before approving the record.”
7. “Only the approved, edited state generates review minutes and mock ADO updates.”
8. “There is no live Confluence, Teams, or Azure DevOps integration and no multi-round workflow
   in this MVP.”

## Video structure

| Time | Segment | Focus |
| --- | --- | --- |
| 0:00–0:20 | Problem and scope | SI governance problem, one-round PoC, human accountability. |
| 0:20–0:50 | Load inputs | Load SI, transcript, and identify review metadata. |
| 0:50–1:35 | Analyze | Show Changes Requested and scan the seven result sections. |
| 1:35–2:10 | Trace evidence | Expand the mapped finding and show both evidence sources. |
| 2:10–2:35 | Human review | Edit one action and emphasize Domain Architect control. |
| 2:35–3:15 | Approve and generate | Show structured record, minutes, and mock ADO outputs. |
| 3:15–3:35 | Close | State real versus mocked scope and no multi-round behavior. |

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
- Explicit human approval gating.
- Generating deterministic structured output and minutes from the approved record.
- Generating local JSON-ready mock ADO updates.
- Automated validation and transformation tests.

### Mocked or simulated

- The SI resembles content normally held in Confluence but is loaded locally.
- The transcript resembles Teams output but is loaded locally.
- Deterministic analysis returns a curated fixture for the bundled pair.
- ADO governance updates and work items are previews and are never submitted.
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
| App is not running | Restart with the planned `uv` command and begin a new take. |
| SI or transcript does not load | Refresh once, reload both samples, and restart the take if needed. |
| Deterministic input mismatch | Reload both bundled inputs without editing them before Analyze. |
| Analysis fixture fails validation | Stop; align models and fixture before recording. |
| An edit is lost | Stop; repair session-state behavior before making the human-review claim. |
| Approval is blocked | Restore the rehearsed valid edit or reanalyze; never bypass validation. |
| Outputs ignore the edit | Stop; fix generation from approved state before recording. |
| Optional LLM fails | Return to deterministic mode; the primary path never depends on it. |
| Layout hides evidence | Restore rehearsed zoom and collapse unrelated sections. |
| Runtime approaches 3:35 | Stop and record a shorter take; preserve evidence and approval steps. |
| Network disconnects | Continue; deterministic mode is offline. |

## Recording checklist

### Content

- [ ] SI, transcript, people, ticket, and dates are synthetic.
- [ ] Only review round 1 is shown.
- [ ] The SI loads before the transcript.
- [ ] Changes Requested or Conditionally Approved is shown.
- [ ] At least one finding maps to an SI section.
- [ ] One confirmed decision is visible.
- [ ] One risk is visible.
- [ ] Two actions are visible.
- [ ] One unresolved governance item is visible.
- [ ] SI and transcript evidence are both demonstrated.
- [ ] The human edit persists.
- [ ] Outputs remain hidden until approval.
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
- [ ] Narration states synthetic data, deterministic analysis, human approval, and mock outputs.
- [ ] Final video is shorter than four minutes.
- [ ] Exported video is played through once before submission.
- [ ] Submission requirements and 22 July 2026 deadline are confirmed.
