# Architecture Governance Copilot — Demo Procedure

Document role: `CURRENT_DEMO_PROCEDURE`. This describes the candidate workflow. The 14 September
recordings under `video/` are historical; their six-category review screens are not the current
acceptance target. Verification evidence belongs in the active/completed execution plan.

## Demonstration objective

Show one coherent review: acquire an authoritative synthetic SI, transcript and metadata; confirm
the exact manifest; Analyze Review; inspect finding/action candidates and complete human review;
generate consistent records; then use the already-configured Delivery capability where available.
Briefly show the independent SI-drafting entry point. The Domain Architect retains formal
architecture authority throughout.

Analysis supplies candidate descriptions and source IDs only. It does not choose business values or
approve the SI. Decisions, Risks, Open Questions and Missing Evidence are not extracted in this
version. Their exclusion does not mean the source contains none.

## Preparation

1. Run `uv sync`, then `uv run streamlit run app.py` for Offline. To rehearse Internal fake use
   `AGC_DEPLOYMENT_PROFILE=development AGC_INTERNAL_FAKE_ENABLED=1 uv run streamlit run app.py`.
2. Use synthetic data only. Internal fake is entirely in memory and makes no network requests.
   Production remains an unavailable capability screen and must not fall back to synthetic work.
3. Preserve another running server by selecting an available dedicated port when necessary.
4. Rehearse the full workflow at the recording resolution before timing a take. Required human
   fields now start blank; allow time to complete them instead of relying on old fixture defaults.
5. Use **Start New Review** for an ordinary review reset. For repeated fake Create demonstrations,
   use the separately confirmed **Start new demo run** only in development/test Internal fake.
   It clears simulated results; ordinary resets retain reconciliation facts.

## Current synthetic packages

| Mode | Authoritative SI | Canonical candidates | Follow-up actions described by source |
| --- | --- | --- | --- |
| Offline | Digital Payment Notification Service, version 1.2 | Three findings, two actions | Alex Chen updates resilience/design by 24 July 2026; Priya Shah confirms RTO/RPO by 25 July 2026. |
| Internal fake | Synthetic Order Routing Service, version 0.8 | Three findings, two actions | Riley Chen documents retry controls by 18 September 2026; Avery Patel schedules/documents failover exercise by 21 September 2026. |

Candidate counts belong to these synthetic fixtures, not a runtime requirement. The model contract
also accepts zero items, finding-only results, and different valid candidate counts. Complete source
text includes decisions, risks and other discussion even though those categories are not extracted.

## Main click-through

1. At the landing page, point out **Draft a Solution Intent** and enter **Review a Solution Intent**.
   Review and drafting are independent; a confirmed local draft never silently becomes the review SI.
2. Load the synthetic transcript, metadata and authoritative SI snapshot in any order. Inspect the
   SI's page/version/source identity. Sources remain independent; loading one preserves the others.
3. Inspect and select **Confirm review input manifest**. Analyze is unavailable until the exact
   source/transcript/context/provider package is confirmed.
4. Select **Analyze Review**. Successful analysis opens Human Review with candidate text, original
   source evidence and the extraction-scope disclosure. No minutes or work items are generated.
5. Inspect one finding's SI and transcript evidence. Open the complete sources to inspect surrounding
   discussion, including later classification. Explain that traceability does not certify a model
   interpretation. Required selectors and optional owner/date fields are initially blank.
6. For each retained finding, supply a short title and explicitly select severity and status. Edit
   the description if appropriate. For each retained action, inspect/edit its text and explicitly
   select priority. Enter owners and dates from the source if they should appear in the final record;
   the application does not silently parse them from candidate text.
7. Select the review outcome explicitly, such as **Changes Requested** for the canonical scenario.
   This is a human-completed record field, not automatic architecture approval.
8. Demonstrate one human correction: edit candidate text or reclassify finding/action. Complete the
   newly relevant required fields. Evidence and stable identity remain unchanged. Restore the kind
   when appropriate for the scenario. Alternatively exclude an out-of-scope proposal. An excluded
   incomplete item does not block confirmation and remains visible during review.
9. Select **Confirm Reviewed Record & Generate Outputs**. Missing required fields must prevent
   completion. With valid fields, full domain and original-source evidence validation run, and the
   app advances to Generated Outputs with minutes and one preview per retained action.
10. Show the structured JSON, rendered minutes, and evidence-to-output comparison. Confirm that
    human values agree across outputs. The four excluded categories say **Not extracted in this
    version; no conclusion about whether such items exist.** JSON carries typed scope metadata,
    and work-item descriptions retain scope and the formal-governance authority note.
11. Download the local records if desired. Offline is complete here; Delivery reports unavailable
    because no provider is configured. No-action records report Delivery not applicable.

For the Internal fake canonical demonstration, a convenient explicit human-completion rehearsal is:

| Field | Source-supported rehearsal value |
| --- | --- |
| Outcome | Changes Requested |
| Finding titles | Retry controls; Regional failover evidence; Retention approval |
| Finding severity/status | Reviewer selects suitable values after inspecting the evidence. |
| Action priorities | Reviewer selects suitable values; no default is supplied. |
| Retry action owner/date | Riley Chen / 2026-09-18 |
| Failover action owner/date | Avery Patel / 2026-09-21 |

These are operator-entered rehearsal values, never automatic application defaults. Choosing not to
enter optional owner/date values is valid for local outputs, but configured Delivery stays blocked.

## Internal fake Delivery

1. From completed outputs, select **Continue to Work Item Delivery**.
2. Inspect each retained action's owner, mapped simulated assignee, due date, priority and parent.
   Missing owner/date/parent blocks request preparation. Use **Back to Human Review**, correct the
   draft and reconfirm outputs. Free-form nonblank owner/ticket values use deterministic local
   simulated mappings, never enterprise identity or parent verification.
3. Select one ready action and choose **Preview Azure DevOps request**. Compare **Work item summary**
   with **Request JSON**. No request has been sent at this point.
4. Select **Confirm request**, then **Create work item**. Inspect the fake receipt and GET read-back.
   Succeeded, submitting and uncertain operations must not allow direct repeat Create.
5. Deliver the other ready action separately. Verify that Back/Return preserves receipts and local
   outputs. Excluding or reclassifying another candidate must not shift the surviving action into
   an unprotected identity. Changed evidence IDs, candidate wording or order do not prove a new action.
6. End with local artifact completion, separate Delivery status and human accountability visible.
   No real Azure DevOps record has been created by this checkout.

## Targeted acceptance rehearsals

- **Incomplete completion:** try confirming before outcome/severity/status/priority/title selection;
  expect localized corrections and no eligible outputs. Excluded incomplete items are ignored.
- **Unknown optional fields:** keep owner/date blank; local records retain unknown values, while
  configured Delivery names the missing requirements.
- **Human semantic correction:** replay a synthetic five-finding/two-action candidate response with
  the two extra findings corresponding to alert thresholds and support roster. It is structurally
  valid and reaches review. Inspect the later explicit source clarification, exclude those two
  candidates and retain the three findings/two actions. This is a constructed quality test, not a
  transcription of a live golden response. Do not hard-code topics or target counts in the parser.
- **Edited transcript:** preserve the bundled SI, edit transcript/valid metadata, reconfirm the
  manifest and Analyze. Current literal finding/action evidence is used; unmatched lines remain in
  complete context. Structured owner/date/business values remain blank for human entry.
- **Stale or failed analysis:** change inputs/provider binding or fail a same-input Analyze retry;
  old analysis cannot remain eligible. Direct navigation must not recover old outputs.
- **Pending and failed confirmation:** unsubmitted edits preserve the last confirmed snapshot with
  a pending-edit disclosure. An explicit invalid reconfirmation revokes old output eligibility.
- **Empty analysis:** zero or all-excluded candidates still require explicit outcome and confirmation;
  outputs do not imply the four excluded categories are absent.
- **State and delivery:** ordinary reset retains reconciliation history. Only the confirmed fake
  new-demo-run command can discard local simulated records. Production/non-fake state is protected.
- **Separate drafting:** save custom synthetic evidence, confirm Context, generate/edit/confirm a
  draft and download it. Review state does not become populated from that draft.

Check desktop and narrow layouts for readable source evidence, visible validation errors, primary
controls, route identity and console errors. Programmatic tests cover malformed envelopes, unknown
IDs, provider failures, reanalysis identity drift and unknown delivery outcomes.

## Suggested narration

“The application starts with a confirmed SI, transcript and review context. Analysis proposes only
findings and explicitly stated follow-up actions. Each candidate points back to original evidence,
and I can inspect the full discussion. I correct the interpretation and enter the required review
fields myself. Only my valid confirmation produces the complete record and consistent action
outputs. Categories outside this extraction scope are disclosed. Delivery has its own exact
request preview, confirmation and reconciliation. The Domain Architect retains formal authority.”

## Internal live demonstration

The user's photographed AIF probe supports feasibility of a single tool response. It showed five
findings and two actions, including two out-of-scope findings and action dates weakened to “the
proposed date.” It is not raw replay evidence or an app end-to-end pass.

The [migration guide](docs/ANALYZE_REVIEW_CANDIDATE_MIGRATION.md) defines separate internal acceptance:
preserve existing Confluence/AIF/ADO connection code, use the implementation-generated request,
click the real Analyze Review button, verify exactly one model call, complete human review, inspect
all outputs and exercise only already-authorized Delivery. Record semantic quality separately from
successful human correction and workflow completion. Do not activate missing enterprise capabilities
or production solely to complete this demo.
