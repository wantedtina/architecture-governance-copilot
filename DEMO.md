# Architecture Governance Copilot — Demo Plan

## Demo objective

In less than four minutes, show one reliable path from a synthetic Teams-style architecture
review transcript to a human-approved governance record, standardized meeting minutes, and mock
Azure DevOps work-item payloads. The recording should emphasize traceability and human control,
not breadth or production readiness.

The target runtime is **3 minutes 35 seconds**, leaving 25 seconds of safety margin.

## Synthetic scenario

The planned fictional meeting reviews **Project Northstar**, a customer self-service portal.
All people, systems, dates, and statements must be obviously synthetic.

The compact scenario should contain:

- a review outcome of **approved with conditions**;
- a confirmed decision to place the public API behind Azure API Management;
- a confirmed decision to use managed identities for service-to-service access;
- a high-severity risk concerning regional failover evidence;
- action items with clearly stated owners, due dates, and priorities;
- one open question about the recovery-time objective;
- missing threat-model and failover-test evidence;
- a short source quote plus timestamp or transcript line reference for every extracted item.

At least one low-value or duplicate action should be present so the reviewer can demonstrate
removal without undermining the final record. The script should also edit one action title or due
date to prove that approved outputs come from human-reviewed data.

The exact transcript and expected JSON will be authored together in implementation phase 2.
They are placeholders at initialization time.

## Preconditions

- Use a local clean checkout containing only synthetic data.
- Complete dependency setup before recording; do not run setup on camera.
- Start the app with `uv run streamlit run app.py`.
- Select or retain **Deterministic demo mode**.
- Use a browser window and zoom level that show headings, evidence, and buttons clearly.
- Reset Streamlit session state immediately before the take.
- Close notifications, unrelated tabs, terminals containing sensitive text, and password tools.
- Confirm that no API key is needed and disconnecting the network does not break the demo path.

## Exact click-by-click workflow and expected screen state

### Step 1 — Open the application

**Action:** Navigate to the local Streamlit URL.

**Expected screen state:**

- The title **Architecture Governance Copilot** is visible.
- A short synthetic-data PoC disclaimer is visible.
- **Deterministic demo mode** is visibly selected or labeled.
- The transcript text area is empty.
- **Load Sample Transcript** is enabled.
- **Analyze** is disabled or produces a clear empty-input validation message.
- No analysis, approval, minutes, or ADO output is visible.

### Step 2 — Load the sample

**Click:** **Load Sample Transcript**.

**Expected screen state:**

- The text area contains the Project Northstar Teams-style transcript.
- Synthetic speaker names, timestamps, and meeting dialogue are readable.
- A status message confirms that the sample was loaded.
- **Analyze** is enabled.
- No extracted governance result is displayed yet.
- Approval and generated outputs remain absent.

### Step 3 — Analyze

**Click:** **Analyze**.

**Expected screen state:**

- A brief analyzing indicator may appear and resolve quickly.
- A success message identifies deterministic demo analysis.
- These six sections appear in this exact order:
  1. Review Outcome
  2. Decisions
  3. Risks
  4. Action Items
  5. Open Questions
  6. Missing Evidence
- Review Outcome shows **Approved with conditions** and its conditions.
- Each section contains the expected fixture values.
- Every outcome or item visibly exposes a source quote and timestamp or line reference.
- Editable controls and remove controls are available for the reviewed record.
- **Approve Governance Record** is available.
- Minutes and mock ADO outputs are not yet generated.

### Step 4 — Inspect evidence

**Click:** Expand one decision's evidence control if evidence is collapsed.

**Expected screen state:**

- The exact synthetic quote is visible.
- The speaker and timestamp or transcript line reference are visible.
- The evidence clearly supports the selected API Management decision.
- The transcript remains available on the page for comparison.

### Step 5 — Edit one action

**Click/type:** Edit the planned action field chosen during rehearsal, for example changing the
title from **Provide failover test** to **Provide regional failover test evidence**.

**Expected screen state:**

- The edited value remains visible after Streamlit reruns.
- The action's original source evidence remains visible and unchanged.
- The record is visibly unapproved.
- No generated minutes or ADO payloads are visible.
- No validation error appears for the rehearsed edit.

### Step 6 — Remove one item

**Click:** The remove control on the rehearsed low-value or duplicate action item.

**Expected screen state:**

- That item disappears from Action Items.
- Other item IDs, values, and evidence remain stable.
- The action count decreases by one.
- The record remains unapproved.
- No generated outputs appear.

### Step 7 — Approve

**Click:** **Approve Governance Record**.

**Expected screen state:**

- A success message confirms explicit human approval.
- The reviewed record is shown as approved for the current analysis.
- A **Standardized Meeting Minutes** section appears.
- A **Mock Azure DevOps Work Items** section appears.
- The minutes contain the edited action wording and exclude the removed action.
- The number of mock ADO payloads equals the number of remaining approved actions.
- A payload contains the edited action wording, owner, due date, priority, source action ID, and
  governance tags.
- Mock outputs are labeled as previews and no external submission is implied.

### Step 8 — Close on scope

**Action:** Scroll or position the page so both output headings and the mock label are visible.
No further click is required.

**Expected screen state:**

- The end-to-end result is visually clear.
- The screen still identifies deterministic mode and synthetic data.
- There is no claim of live Teams, Confluence, Azure DevOps, or production integration.

## Preliminary narration points

Use natural language rather than reading every field:

1. “Architecture reviews create decisions and actions, but turning a meeting into a traceable
   governance record is manual and inconsistent.”
2. “This hackathon PoC uses a synthetic Teams-style transcript and deterministic offline mode so
   the workflow is reliable without an LLM API.”
3. “Analysis structures the outcome, decisions, risks, actions, open questions, and missing
   evidence.”
4. “Every item retains a source quote and transcript reference, so the reviewer can verify why
   it exists.”
5. “The machine proposes; the reviewer controls the record. I’ll make one edit and remove one
   item before approval.”
6. “Only the approved, edited record generates the standardized minutes and mock work-item
   payloads.”
7. “Nothing is sent to Teams, Confluence, or Azure DevOps. This proves the controlled workflow,
   not a production integration.”

## Video structure

| Time | Segment | Visual and narration focus |
| --- | --- | --- |
| 0:00–0:20 | Problem and scope | App title; explain the manual governance problem and one-workflow PoC. |
| 0:20–0:45 | Load sample | Click the sample button; identify synthetic Teams-style input and deterministic mode. |
| 0:45–1:30 | Analyze and scan | Click Analyze; quickly scan the six required sections and outcome. |
| 1:30–2:00 | Verify evidence | Expand one decision; connect quote/reference to structured decision. |
| 2:00–2:35 | Human review | Edit the rehearsed action and remove the rehearsed duplicate/low-value item. |
| 2:35–3:15 | Approve and generate | Approve; show minutes and mock ADO payloads reflecting the reviewed record. |
| 3:15–3:35 | Close | State what is real, what is mocked, and the value demonstrated. |

Hard stop at 3:35. Do not spend recording time on setup, installation, code walkthroughs, optional
providers, or scrolling through every item.

## What is real and what is mocked

### Real in the PoC

- Loading a local synthetic transcript into the UI.
- Validating structured data with Pydantic.
- Rendering all required governance categories.
- Showing source quotes and transcript references.
- Editing and removing structured items in the local session.
- Explicit approval gating.
- Deterministically generating meeting-minutes Markdown from the approved record.
- Deterministically generating JSON-ready mock work-item objects from approved actions.
- Automated model and generator tests.

### Mocked or simulated

- The transcript resembles Teams output but is not fetched from Microsoft Teams.
- Deterministic analysis loads a curated expected result; it does not call or imitate an LLM.
- A future real LLM provider is optional and should not be used for the recorded path.
- ADO work-item payloads are previews only and are not sent to Azure DevOps.
- Meeting minutes are displayed locally and are not published to Confluence or another system.
- User identity, permissions, audit history, persistence, and production operations do not exist.

## Deterministic demo mode

- It is the default and the only required mode for the final recording.
- It recognizes the bundled normalized transcript and returns the validated bundled expected
  result.
- It requires no API key, network, model SDK, or external service.
- It must fail clearly rather than return misleading results if the transcript no longer matches
  the bundled sample.
- The recording should explicitly disclose that deterministic mode is fixture-backed.
- The mode proves review, traceability, approval, and generation behavior; it does not claim
  general extraction intelligence.
- If an optional real provider exists, do not switch to it during the primary take.

## Demo failure fallbacks

| Failure | Immediate fallback |
| --- | --- |
| App is not running | Keep a prepared terminal with `uv run streamlit run app.py`; restart, reset session state, and begin a new take. |
| Sample does not load | Refresh once; if still broken, stop the take and restore the known-good commit rather than pasting unverified text. |
| Analyze reports transcript mismatch | Click **Load Sample Transcript** again and analyze without editing the transcript; if it persists, stop and validate fixture alignment. |
| Optional LLM provider fails | Return to deterministic mode and reload the sample. The primary script must never depend on the optional provider. |
| Edit is lost on rerun | Stop the take; do not claim human review. Fix session-state behavior and rerun its smoke test before recording again. |
| Validation blocks approval | Restore the rehearsed valid edit or reload/reanalyze the sample. Do not bypass validation. |
| Outputs do not reflect the edit/removal | Stop the take. This invalidates the core claim and must be fixed before recording. |
| Browser layout hides evidence or buttons | Use the rehearsed resolution/zoom and collapse unrelated sections; restart the take if needed. |
| Recording approaches 3:35 before approval | Stop and record a new take using the shorter narration; do not accelerate past evidence or approval. |
| Network disconnects | Continue in deterministic mode; the demo path is designed to be offline. |

Screenshots or prerecorded output are not substitutes for the working end-to-end path. A backup
screen recording of a successful rehearsal may be retained in case the recording tool, rather
than the application, fails.

## Final video recording checklist

### Content and behavior

- [ ] The transcript and all names, systems, and dates are synthetic.
- [ ] Deterministic mode works with network access disabled.
- [ ] The fixture validates against the current models.
- [ ] All six required result sections appear in the planned order.
- [ ] Every outcome and item has visible evidence.
- [ ] The rehearsed edit persists.
- [ ] The rehearsed removal affects both final outputs.
- [ ] Approval is explicit and outputs do not appear before it.
- [ ] Minutes contain the edited value.
- [ ] Mock ADO item count equals approved action count.
- [ ] Outputs are clearly labeled local/mock.

### Technical rehearsal

- [ ] `uv sync` has completed successfully in the recording environment.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check .` passes.
- [ ] `uv run ruff format --check .` passes.
- [ ] `uv run streamlit run app.py` starts the app.
- [ ] The browser is at the rehearsed resolution and zoom.
- [ ] Session state is reset and the transcript area begins empty.
- [ ] The exact click path has completed successfully twice before recording.

### Recording quality and safety

- [ ] Target script is 3:35 or shorter in a timed rehearsal.
- [ ] Notifications and unrelated applications are closed.
- [ ] No terminal, environment file, API key, account name, or confidential data is visible.
- [ ] Cursor movement and scrolling are slow enough to follow.
- [ ] Text is legible in the captured resolution.
- [ ] Microphone level is clear and background noise is acceptable.
- [ ] The recording includes disclosure of synthetic data, deterministic analysis, and mock ADO.
- [ ] The final exported video is shorter than four minutes.
- [ ] The exported video is played back once from start to finish before submission.
- [ ] The submission file name, format, audio, and deadline (22 July 2026) are confirmed.
