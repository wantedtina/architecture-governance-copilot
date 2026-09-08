# Final-stage presentation and demo plan

Updated: 2026-09-08

**Current execution horizon: the 14 September submission.** Prioritize the verified development
version targeted for 11 September and the four required submission artifacts due 14 September. Prepare
business evidence and material outlines alongside development. This prioritization does not itself
authorize implementation or submission, or silently remove selected requirements.

All post-submission activities are deferred until after the 14 September submission is complete:
feedback-driven development, conference-specific scripts and rehearsals, and Shark Tank pitch,
Q&A, and coaching preparation. Later dates, requirements, and detailed guidance below are retained
as reference only, not active work or prerequisites for submission. Collecting briefing information
now is appropriate; it does not activate those activities. Apply relevant storytelling and business
value guidance now only to the four-minute submission video and key-details write-up.

Status: The split structure is confirmed; presentation content remains under review.
This document does not authorize application development or external publication.

## 1. Objective, scope, and relationship to implementation

This plan owns the presentation narrative, demo actions, scripts, materials, rehearsals,
and fallback path. Code behavior, implementation steps, tests, and code-freeze gates belong
in the [Implementation Plan](FINAL_STAGE_IMPLEMENTATION_PLAN.md) and are not duplicated here.

The organizer's latest notice replaces the previous 18 September code-freeze and 19–21 September
materials-only schedule. Maintain separate development and presentation plans, with two versions:
a verified first submission and a later feedback-driven conference version. Prepare outlines,
business evidence, and diagram structure alongside development; finalize recordings and claims
against the verified code version. Retain the lightweight demonstrability check before recording.

### Organizer requirements received during planning

Sources: organizer notices supplied by the user, including the updated timeline screenshot and
answers reported after the 8 September briefing. Later clarifications govern operational details.
This is a requirements summary, not a claim that Codex attended the briefing.

| Date | Requirement |
| --- | --- |
| 11 September | Target development/material readiness and engage SPOCs; no formal checkpoint. |
| 14 September | Submit all deliverables; submissions accepted throughout the day. SharePoint link to follow. |
| 14–17 September | Judges review submitted solutions. |
| 18 September | Teams receive judge feedback. |
| Through 23 September | Refine the solution using feedback. |
| 21–23 September | On-site improvements and judging among 99 teams; live demo preferred, recording backup acceptable. |
| 23 September | Finalists announced; approximately 10–20 teams selected. |
| 24 September | Shark Tank for selected finalists. |

Continue the same pre-conference solution and problem statement. Required submissions are a
repository link, architecture diagram, four-minute working-solution demo video, and key-details
write-up. The Skills Accelerator learning materials and Shark Tank FAQ have now been supplied as local
Markdown references. The briefing confirms: use the previous repository submission method;
there is no prescribed write-up template, length, or format; follow the previous video approach
with a maximum duration of four minutes. Do not wait for new format rules before preparing material.
Verify the actual previous submission artifacts when producing deliverables rather than inventing
technical specifications. Aim to complete everything by 11 September while retaining 14 September
as the submission day; the all-day answer does not specify an exact timezone cutoff.

No updated code/video/document submission is required after feedback: demonstrate refinements
on-site. Corporate network availability was not explicitly confirmed by the answer; validate it
later if needed and retain a recording backup. Coaching will be arranged by organizers if selected
for Shark Tank; no preparation or registration task is active now. Four minutes applies to
the submitted video, not an assumed on-site presentation limit. Slides are not explicitly required.

Judging covers innovation, business value, technical implementation, demonstration and presentation.
Explain the problem, working solution, benefits to the Bank, and path to production. Engage the
Problem Statement SPOC to validate business benefits, expected savings/efficiencies/risk reduction,
productionization effort/timeline/manpower, scalability, and time to market. The user coordinates
that internal discussion; this plan does not authorize contacting anyone or submitting materials.

All materials and deliverables must be in English. Session discussion with the user should
prefer Chinese, as required by AGENTS.md.

## 2. Complete judge-feedback transcription

The following is the complete visible text from the **Team Evaluation Feedback** screenshot.
Wording is preserved as closely as the image permits.

> **Accelerate 3.0 Hackathon**
> Team Evaluation Feedback
>
> **TEAM NAME**
> Two Tokens One Brain
>
> **Topic:** Architecture Givernance Automation
>
> **Evaluation Comments**
>
> Lead the demo with the human-in-the-loop review stage: edit an owner, exclude a finding,
> and show the “inputs changed ? outputs invalidated” guard fire since that evidence-locked
> record is your strongest asset. Then walk the generated minutes and ADO items beside their
> cited evidence spans so a judge sees the traceability chain from source quote to work item.
>
> **Recommended improvements**
>
> An honest, well-engineered offline POC that hits all three deliverables in miniature:
> records are the deep, rigorous core (enforced schemas, mandatory evidence spans, a
> human-review path that structurally cannot invent facts), with minutes and ADO work-item
> previews generated deterministically off that validated record. The main caveat is scope:
> the “AI” is a frozen-fixture replay over a single bundled scenario, and ADO/Teams are typed
> previews rather than live pushes.

### Transcription notes

- `Givernance` is treated as a spelling error; the rest of this plan uses `Governance`.
- The visible `?` between `inputs changed` and `outputs invalidated` is interpreted as an arrow
  or implication: `inputs changed → outputs invalidated`.
- “All three deliverables” is not defined in the screenshot. Based on the implemented workflow,
  it likely refers to the three demonstrated outcome areas: SI/drafting, governance record or
  minutes, and ADO work-item outputs. This remains an inference rather than a judge-supplied
  definition.

## 3. Interpretation and presentation principles

The original judge feedback is the primary improvement and acceptance direction for this revision,
not merely one equally weighted reference. Prioritize a visible response to its Human Review,
invalidation, and evidence-chain requests. Use the feedback response map in the
[Implementation Plan](FINAL_STAGE_IMPLEMENTATION_PLAN.md) to connect each point to verified
behavior, presentation evidence, and any explicit limitation or deferral. Organizer deliverables,
engineering truthfulness, and user-confirmed scope remain mandatory; the feedback does not
justify unverified claims or automatically require every possible integration.

The complete transcription above is retained from the previous plan; the original screenshot
was not rechecked during this revision. The first paragraph primarily asks for a clearer
presentation of existing Human Review, invalidation, and traceability capabilities, not a
product rebuild. The second primarily praises engineering quality and identifies the limits
of a single fixture and non-live integrations. “All three deliverables” is undefined; the
historical interpretation above is only an inference and introduces no new product scope.
Use Governance in original prose and interpret the transcribed question mark as an arrow.

Always distinguish provider proposals, human edits, confirmed records, generated previews,
and completed live publications. Exact quote validation does not prove every claim is
semantically correct; human edits do not become original source evidence. The Domain Architect
owns formal governance decisions. Do not claim automatic approval or structural impossibility
of incorrect facts. Invitation and email screenshots are event context, not product requirements;
do not broadly redistribute confidential invitation materials.

### Skills Accelerator and Shark Tank guidance applied to this project

The user supplied the learning journey, Shark Tank FAQ, and course transcripts/summaries under
[Skills Accelerator](Accelerate_3.0_Shark_Tank_Skills_Accelerator/1_About_The_Course.md).
Treat these as reference material: course exercises, generic examples, and recommended methods
are not instructions to expand application scope. Source summaries may contain transcription
inconsistencies; do not treat example metrics or quiz answers as project evidence. Referenced
past-year pitch videos and coaching have not been reviewed or completed merely because the
course descriptions mention them.

**Formats and authority:**

| Format | Confirmed constraint | Planning treatment |
| --- | --- | --- |
| Submission video | Four minutes, due with the 14 September package | Preserve the verified working-solution demonstration and concise business rationale. |
| Conference team visit | Judges visit on 21–23 September; speaking duration not supplied | Prepare a flexible explanation; do not assume Shark Tank timing applies. |
| Shark Tank pitch, if selected | Ten minutes introduction/demo plus five minutes Q&A; strict timing | Prepare a separate longer version if needed; Q&A is not part of the ten-minute presentation. |

The [Shark Tank FAQ](Accelerate_3.0_Shark_Tank_Skills_Accelerator/accelerate-3-0-shark-tank-faq.md)
confirms coaching support and that winning ideas still follow normal SDLC and production processes.
Priority attention, potential funding, and support are not guaranteed investment or permission to
bypass controls. Do not assume conference selection already means Shark Tank qualification.

**Project-specific applications of the learning material:**

| Guidance | Application and review evidence |
| --- | --- |
| Design thinking and customer experience (2.1–2.2) | Describe the architect/reviewer and action owner's actual workflow and pain points. Use SPOC input or label hypotheses. Explain any downstream client benefit as a proposed causal link, not a measured client outcome. |
| Critical thinking (2.3) | Distinguish facts, assumptions, synthetic demonstrations, estimates, and validated outcomes. Test the case against manual working and existing tools instead of claiming no alternatives exist. |
| Product value and business cases (3.1–3.2) | Translate generated minutes and tickets into expected reductions in preparation/re-entry effort and clearer accountability. Explain differentiation through the human-controlled evidence chain, with costs, limitations, and alternatives. |
| Performance measures (3.3) | Propose a small set of measurable pilot outcomes with definitions, baseline, collection method, owner, and period. Do not introduce a KPI platform or copy an organization-wide measurement program. |
| Technical communication and influence (4.1–4.3) | Use plain English and a concrete review scenario; explain why each demonstrated control matters. End with a specific next-step request agreed with the user, not an invented funding amount. |
| Visual storytelling (5.1) | Use readable evidence-to-action comparisons and an accurate architecture diagram. Show actual capabilities separately from production proposals; avoid decorative or unsupported benefit charts. |
| Executive presence and pitching (5.2–5.3) | Lead with the point, give evidence, acknowledge limits, and explain the next action. Rehearse objections, concise answers, delivery pace, and recovery. |

Source references: [critical thinking](Accelerate_3.0_Shark_Tank_Skills_Accelerator/2.3_think_smarter_critical_thinking_summary.md),
[business cases](Accelerate_3.0_Shark_Tank_Skills_Accelerator/3.2_building-business-cases-and-plans-summary.md),
[measures](Accelerate_3.0_Shark_Tank_Skills_Accelerator/3.3_key-performance-indicators-course-notes.md),
[visual storytelling](Accelerate_3.0_Shark_Tank_Skills_Accelerator/5.1_infographics-the-power-of-visual-storytelling-summary.md),
and [pitch structure](Accelerate_3.0_Shark_Tank_Skills_Accelerator/5.3_getting-your-pitch-heard.md).

**Narrative:** Keep the first substantive product demonstration at Human Review, as requested by
judges. A short problem/value statement can accompany that opening screen. Follow the demonstrated
human edit/exclusion, evidence chain, and invalidation with the business implication, production
path, and agreed next-step ask. Do not replace working behavior with a long introductory deck.
The four-minute video and conditional Shark Tank version share the same facts; the longer version
adds evidence, alternatives, feasibility, and discussion depth rather than speculative features.

**Candidate pilot measures, not achieved results or newly approved targets:**

- Human effort from review inputs to confirmed minutes/actions, including verification and rework;
  distinguish hands-on time from total elapsed time and compare equivalent tasks.
- Time to locate the supporting evidence for a selected action, using the same retrieval task.
- Proportion of applicable actions with resolvable source evidence, with an explicit denominator;
  this does not measure semantic correctness. Pair it with human checks of claim support and
  missed actions so that fewer extracted actions do not misleadingly improve the measure.

Agree measurement definitions and feasible targets with the user/SPOC before presenting numerical
claims. Synthetic benchmark results must be labelled and cannot establish Bank-wide savings.
Use a small manual measurement exercise if feasible; no new application telemetry is required.

**Pitch and Q&A rehearsal:** For Shark Tank, target an internal rehearsal of at most 8 minutes
30 seconds to preserve the existing 15% margin within the ten-minute slot; the official limit
remains ten minutes. Practice a separate five-minute Q&A. Prepare direct answers about why existing
meeting summaries are insufficient, evidence limits, human accountability, actual live connections,
permissions/data handling, cost and adoption assumptions, scalability, SDLC, and the proposed pilot.
Unknown facts receive an explicit follow-up, not an invented answer. Use coaching if arranged;
its availability does not prove a session has been booked. Confirm the next-step ask with the user
(e.g. a bounded pilot and sponsor support); do not promise funding, staffing, or production dates.

## 4. Lightweight demonstrability check before code freeze

- **Objective:** Find interface problems that would block the final demonstration while code
  changes are still possible.
- **Input:** Working offline capabilities from the implementation plan.
- **Actions:** Prepare Human Review through the normal workflow. Check one owner edit, finding
  exclusion, confirmation, evidence comparison, and real input invalidation. Check text and
  controls at 1920×1080.
- **Acceptance:** Key behavior is visible, evidence associations are correct, and controls are
  unobstructed. Return defects to the corresponding implementation acceptance criteria.
- **Boundaries and risks:** Do not expand this into a complete UI redesign or add product
  capabilities solely to satisfy presentation preferences.
- **Out of scope:** Finished narration, formal recording, and final slides.

## 5. Presentation paths and candidate demo actions

Both paths begin at Human Review. Prepare the page through normal loading and analysis in
advance; do not inject state or bypass validation. Project Context and SI drafting remain
available and may be mentioned briefly without occupying the opening story.

Candidate actions still require confirmation; silence does not approve them:

- Change the first action owner from Alex Chen to Taylor Kim.
- Exclude the actual sample finding: Undefined production support ownership.

After exclusion, Confirmed production support ownership remains under Missing Information,
and Changes Requested remains unchanged. Explain that the finding was excluded from this
reviewed record, not that the support issue was resolved. The first action has only transcript
evidence: use transcript-line-15 and do not invent an SI section.

### Offline path: mandatory and complete

1. At Human Review, explain how governance records can become separated from evidence and
   identify the active mode as fixture-backed.
2. Open the first action's original quote, speaker, timestamp, and reference.
3. Edit the owner and exclude the selected finding, leaving evidence unchanged.
4. Explicitly confirm the reviewed record and generate outputs.
5. Show the change summary and source quote → reviewed action → minutes → ADO preview comparison.
6. Explain that Alex's original quotation is unchanged and Taylor is a human override; both
   action previews use confirmed values.
7. Return to Review Inputs and make a substantive SI or transcript edit to trigger the real guard.
8. Show Inputs changed → outputs invalidated and that previous outputs cannot be reopened.
9. Close on human accountability and actual product scope.

Verify recovery during rehearsal; it need not consume presentation time. Restore bundled inputs,
reanalyze, and reconfirm. The deterministic analyzer must reject substantively edited inputs;
do not demonstrate successful arbitrary-input analysis in offline mode.

### Internal integration path: eligible only after the implementation live gate

- Also begin at prepared Human Review. Use the source summary to establish the versioned
  Confluence snapshot, explicitly supplied synthetic transcript/metadata, and AIF analysis.
  Loading remains preparation before the opening.
- Perform the same human edits, exclusion, and evidence comparison.
- At outputs, show the exact ADO publication preview, separately confirm creation of one test
  Work Item, and display its verified receipt.
- Trigger invalidation through a rehearsed Confluence refresh/version change or an explicitly
  identified local transcript edit.
- State that local invalidation does not undo a Work Item already created remotely.
- Never label fake adapters as live or silently switch to fixtures after a failure while
  continuing to call the result AIF output.

Choose the path before the judged story starts, using implementation acceptance records and
verification in the event environment. If live operation fails during the presentation, explain
it and switch to a prepared separate offline session or backup materials. Do not retry Create
when a previous publication result is unknown.

### Teams transcript source and demonstration treatment

Teams is an important source of meeting evidence. Automatic Teams retrieval is not required for
this demonstration: manual transcript input is the baseline when time or internal permissions
prevent API integration. Judge feedback prioritizes Human Review, invalidation, and the evidence
chain; it does not establish a requirement for a live Teams connector.

- If permitted, prepare a synthetic architecture-review meeting in Teams and export its transcript.
  Otherwise use clearly labelled synthetic meeting text; do not claim it was exported from Teams.
  Keep company meeting material and identities out of external repository fixtures.
- Supply the transcript through the existing text-input workflow before the judged story begins.
  A new upload feature is not required. Start at Human Review as planned, and explain the source
  when showing the original quote, available speaker/time information, and resulting action.
- For manual input, use: "The meeting transcript is supplied manually in this demo; automatic
  Teams retrieval is not connected." Label the source as Teams-exported only if that is true.
- In diagrams, label the actual input path "Teams transcript — manual import" when using a Teams
  export, or "Synthetic meeting transcript — manual input" otherwise. Any optional API path must
  be marked "Planned" until implemented and accepted. Do not describe the complete flow as automated.
- Manual input can accompany validated live AIF analysis and ADO creation. For the offline path,
  separately disclose fixture-backed analysis; manually supplying text does not make it live AI.
- If the optional internal Teams assessment leads to an accepted connector before freeze, update
  the source label and preparation steps to match actual behavior. Retain manual input as fallback
  and do not spend the opening demonstration on authentication or meeting discovery.

This source discussion does not add automatic SI-body revision to the product. The planned core
uses SI and transcript evidence for governance analysis, human review, and confirmed outputs.

## 6. Presentation, demo, and materials work packages

### P1 — Lock the story and demo values

- **Objective:** Cover the judge's explicit requests through one source-to-output story.
- **Files:** This document and DEMO.md.
- **Behavior:** Apply the Skills Accelerator narrative and evidence guidance above. Confirm
  candidate actions, the four-minute video structure, and eligible capabilities;
  define the opening, core demonstration, and closing.
- **Dependencies:** Verified implementation for final claims; user confirmation of exact demo values.
  Outline work can start earlier. On-site duration remains pending.
- **Validation:** Owner edit, finding exclusion, invalidation, and evidence comparison each
  have a corresponding visible action.
- **Risks and boundaries:** Exclusion is not resolution; provider output is not approval.
- **Out of scope:** Adding application features to accommodate narration.

### P2 — Produce and synchronize written materials

- **Objective:** Make all narration consistent with frozen code.
- **Files:** DEMO.md, video/DEMO_ACTIONS.md, video/NARRATION_SCRIPT.md,
  video/STORYBOARD.md, video/ON_SCREEN_TEXT.md, and relevant checklists. If recording tools are
  reused, synchronize actions and assertions in video/tools/record_demo.js.
- **Behavior:** Prepare full and compressed scripts, the offline version, and an integrated
  version only for accepted capabilities. Replace the old Redis-exclusion action in current
  scripts. Mark July submission requirements as historical; they do not determine September
  timing, and synthetic sample dates remain unchanged.
- **Dependencies:** P1 for outlines; verified submission baseline for final recording and capability claims.
  Produce the required four-minute video, architecture diagram, and key-details write-up; slides
  remain optional unless later guidance requires them.
- **Validation:** Narration, button labels, screenshots, subtitles, and recorded actions agree.
  Keep the submitted video at or below four minutes, following the previous video approach. Reserve at least 15% timing margin for the live script once its limit is known.
- **Risks and boundaries:** Do not distribute confidential invitations. Keep media work separate
  from application changes.
- **Out of scope:** Rebuilding every historical video or committing large generated media by default.

### P3 — Verify the submission recording; defer conference rehearsals

- **Objective:** Before 14 September, verify the recorded submission story and artifact consistency.
  Conference-environment rehearsals below are deferred until after submission.
- **Inputs:** Frozen code, finished materials, and confirmed presentation duration.
- **Behavior:** Before submission, check the selected recording path from a clean session and
  verify the final video plays correctly and meets the four-minute requirement. After submission,
  complete at least two offline conference rehearsals from clean sessions. If using live
  operation, verify it repeatedly in the event environment. Check windows, zoom, notifications,
  account exposure, network, click pacing, subtitle obstruction, and backup playback.
- **Validation:** Full and compressed scripts complete the essential actions; the live script
  retains the 15% margin when its limit is known; verify the submitted video duration separately. Live failure permits an honest offline switch, and unknown publication
  results never trigger blind retries.
- **Dependencies:** P2; path eligibility comes from the Implementation Plan gates. Include the
  separate Shark Tank rehearsal and Q&A only if that presentation is needed.
- **Risks and boundaries:** Preserve the submitted version. After 18 September feedback, make
  bounded verified refinements and update conference materials together with the code version.
- **Out of scope:** Unverified last-minute changes or silently replacing submitted artifacts.

### P4 — Business case, submission package, and feedback revision

- **Objective:** Deliver all four required artifacts by 14 September, then prepare an accurate
  conference revision based on the 18 September feedback.
- **Files/artifacts:** Existing demo/script/diagram sources where suitable; an English key-details
  write-up and submission checklist in a user-selected location. Final video and large binaries
  remain external deliverables by default. Do not produce or upload artifacts during planning.
- **Behavior:** Explain the unchanged problem and implemented workflow; map evidence traceability,
  human review, minutes, and work items to business pain points. Obtain SPOC input through the user.
  Distinguish observed measurements, estimates with assumptions, and unvalidated claims. For any
  savings estimate record baseline activity time, expected assisted time, volume, human-review
  effort, and measurement basis; do not invent percentages, costs, staffing, or delivery dates.
  Describe production dependencies, roles/effort ranges, staged timeline, scalability constraints,
  and time-to-market assumptions without expanding hackathon implementation scope.
- **Architecture:** Clearly separate implemented offline/fake/live paths from future production
  components. Label manual transcript input accurately. Keep the diagram consistent with the video.
- **Dependencies:** P1–P3, identified submission code version, SPOC input, SharePoint link/access,
  repository reviewer access, and the previous submission method. No mandatory write-up template or new media specification
  was prescribed. Use the learning material for communication guidance. Draft known sections
  now; flag missing evidence rather than blocking all material preparation.
- **Validation:** Checklist covers repo link and access, diagram legibility, four-minute video
  playback/duration and working behavior, write-up completeness, consistent version/capabilities,
  and traceable estimate assumptions. Record submission receipt only after an authorized upload
  succeeds; preparation alone does not mean submitted.
- **Feedback round:** Preserve submitted artifacts; triage feedback on 18 September, link selected
  changes to verification, and update conference materials through 23 September. No resubmission
  is required; preserve the original package and demonstrate the revised version on-site. Rehearse the version used at 21–23 September judging.
- **Risks:** Late SharePoint access, unsupported benefit claims, mismatched artifact
  versions, and optional integration work crowding out the required submission.
- **Out of scope:** Changing the problem statement, invented business validation, unsolicited
  outreach, unauthorized publication, or building production infrastructure solely for estimates.

## 7. Definition of done

- Each applicable original feedback point has a recorded response and actual verification or
  demonstration evidence; remaining limitations and agreed deferrals are explicit.

- The demo begins at Human Review, with normal preparation steps documented.
- Live owner editing, finding exclusion, human confirmation, the summary, evidence comparison,
  and invalidation are clearly visible.
- Evidence, human overrides, preview/live status, and formal governance responsibility are distinct.
- Exact demo values are confirmed; the required video meets the four-minute requirement.
  Apply the 15% live timing margin once the on-site limit is known.
- The offline fallback is rehearsed. Live uses only implementation-accepted capabilities that
  also passed checks in the event environment.
- All four submission artifacts agree with the recorded submission version and are ready by
  14 September; actual submission requires access and authorization. Business claims have evidence
  or labelled assumptions. Preserve the original package when preparing the conference revision.

## 8. Open decisions

1. Whether to use the candidate owner edit and actual finding exclusion above.
2. SharePoint link remains an organizer delivery dependency, not an unresolved submission policy.
   Use the previous repository method; no prescribed write-up template; video must not exceed four minutes.
3. The specific pilot/support ask and SPOC-validated benefit evidence and productionization
   assumptions. Missing figures must remain labelled, not invented.
4. Deferred until after submission: conference speaking duration, actual network availability,
   final rehearsal arrangements, and whether the team is selected for 24 September Shark Tank.
   Selection/coaching will be handled by organizers; no renewed clarification is needed now.

These decisions do not block development of generic product behavior. This plan remains open
for further revision.
