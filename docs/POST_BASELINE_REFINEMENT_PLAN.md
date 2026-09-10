# Post-baseline refinement register

Updated: 2026-09-10

Document status: `ACTIVE_CHANGE_REGISTER`

Execution authority: `NONE`. No application implementation batch is currently authorized.

Active execution plan: `NONE`

## 1. Purpose and authority

This document is the requirements and change-control register for findings discovered while the
user tests the implementation frozen at `submission-2026-09-14-r1`. It records change intent and
lifecycle decisions. It is not a growing implementation plan and must not accumulate detailed code
steps, test procedures, progress logs, or batch verification evidence.

Record new findings here until the user confirms that the intake is complete. Before development,
group accepted items into bounded work packages with explicit dependencies, acceptance criteria,
verification, and rollback or invalidation behavior. Put those execution details in one separate
living plan under `docs/exec-plans/` and reference it through the sole active-plan pointer above. Do
not implement a collected item merely because it appears in this register.

Preserve the deterministic offline path, human review, evidence traceability, strict validation,
and the existing provider boundaries. Do not imply live enterprise integration where only
synthetic discovery or in-memory adapters exist.

## 2. Repository truth model

Repository governance distinguishes four complementary kinds of fact. No single Markdown file is
the source of truth for all four.

| Kind of fact | Authoritative evidence | Question answered |
| --- | --- | --- |
| Current product truth | Checked-out Git revision, application code, tests, and synchronized `SPEC.md` / `README.md` | What does the system actually do now? |
| Current change intent | `Accepted` / `Ready` items in this register and the referenced active execution plan | What approved behavior should change next? |
| Current execution state | Active execution plan, Git working tree, recent history, and actual verification results | How far has the current implementation batch progressed? |
| Historical decision and evidence | Completed plans, baseline records, completed execution plans, and archived handoffs | What was done before, why, and how was it verified then? |

Future sessions must not infer current implementation scope from historical plans, baseline
records, archive material, or future/optional sections in maintained product documentation.

## 3. Document control map

| Document | Current role | Status treatment |
| --- | --- | --- |
| `AGENTS.md` | Persistent repository instructions and constraints | Active and authoritative |
| `docs/POST_BASELINE_REFINEMENT_PLAN.md` | New findings, decisions, and future bounded batches | Active requirements intake |
| `docs/exec-plans/README.md` | Stable convention for bounded execution plans | Process reference only; never active scope |
| `docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_*.md` | One approved implementation batch per file | Active only when this register names it; retain completed plans as history |
| `docs/SUBMISSION_BASELINE.md` | Immutable evidence for the verified 14 September version | Completed baseline record; do not repurpose |
| `docs/FINAL_STAGE_IMPLEMENTATION_PLAN.md` | Approved I1–I10 engineering plan and completion record | I1–I8 and I10 complete; I9 deferred |
| `docs/FINAL_STAGE_PRESENTATION_DEMO_PLAN.md` | Submission presentation, demo, and later event preparation | Separate workstream; unresolved or deferred items remain subject to user approval |
| `docs/FINAL_STAGE_DEVELOPMENT_PLAN.md` | Navigation index for the maintained plans | Active index only; not a third scope definition |
| `README.md` | Operator-facing setup, capabilities, and implemented limitations | Current product description; update only when verified behavior changes |
| `SPEC.md` | Product and technical contract for implemented behavior | Current baseline specification; revise with an approved implementation batch |
| `DEMO.md` | Demonstration procedure for the verified baseline | Current baseline demo; revise only if the approved demo path changes |
| `docs/INTERNAL_INTEGRATION_HANDOFF.md` | Bounded future live-adapter acceptance sequence | Deferred until approved internal configuration and targets exist |
| `docs/archive/*` | Historical session context | Historical reference only; never resume as current instructions |
| `video/*` | Historical/current media-production assets as individually described | Separate deliverables; not application implementation authority |

If documents conflict, use this precedence for new development decisions:

1. current explicit user direction;
2. `AGENTS.md`;
3. the sole active, explicitly approved execution plan referenced by this register;
4. `Accepted` / `Ready` items in this register;
5. current implemented contract in `SPEC.md`, `README.md`, code, and tests;
6. completed implementation plans, baseline evidence, and completed execution plans;
7. archived handoffs as context only.

The higher-ranked source controls intent or process, but it cannot make a false claim about current
product behavior: product truth must still be verified against the checked-out code and tests.

## 4. Change lifecycle

Each refinement item uses one of these states:

| State | Meaning |
| --- | --- |
| `Collected` | The issue or direction has been recorded, but consolidated scope is not approved. |
| `Needs decision` | A product, security, data, or interaction choice is required. |
| `Accepted` | The user approved the requirement, but it is not yet assigned to an implementation batch. |
| `Ready` | Dependencies and acceptance criteria are sufficient for a bounded implementation batch. |
| `In progress` | The user authorized the batch and implementation has started. |
| `Verified` | The implementation and required checks passed, with evidence recorded. |
| `Deferred` | The item remains valid but is intentionally outside the current horizon. |
| `Rejected` | The item will not be implemented; retain the reason for traceability. |

State changes must be explicit. Passing tests does not promote an item from `Collected` or
`Accepted` to `In progress`, and implementation does not become `Verified` without the defined
acceptance evidence.

## 5. Refinement items

### R1 — Production-shaped Project Context source acquisition and selection

- **State:** `Accepted`
- **Origin:** User testing after the 14 September baseline was completed.
- **Observed behavior:** Opening the single demonstration workspace loads one frozen source
  package and presents four inclusion checkboxes. The required template and repository controls
  gate continuation, supporting evidence affects the drafting payload, and the governance metadata
  checkbox currently has no material effect on the confirmed drafting package. Source identity and
  source content cannot be changed within the bundled scenario.
- **Problem:** The current controls do not clearly model how a real user would discover only
  authorized resources, choose exact sources, validate typed or pasted identifiers, inspect
  provenance, and confirm the resulting source package. A checkbox can express inclusion, but it
  cannot adequately express resource identity, authorization, version, or validation state.
- **Desired outcome:** Users can discover or load allowed sources, select exact resources, validate
  identities and access, inspect provenance, and explicitly confirm one source-package manifest.
  The external PoC must represent this with deterministic synthetic inventories until enterprise
  discovery adapters are separately approved.

Desired behavior to refine before approval:

1. Load the governed SI template by default and expose its canonical source, version, and validation
   status. A future approved Confluence adapter may discover alternative authorized templates.
2. Represent repository selection as authorized organization/project/repository discovery with a
   searchable selector, followed by branch, tag, or commit selection. If manual URL or identifier
   entry is allowed, resolve it against the authorized inventory and reject unresolved or
   unauthorized values before confirmation.
3. Represent supporting evidence as a multi-select collection of authorized, previewable resources.
   Preserve resource identity, version or fingerprint, selected scope, and retrieval status.
   Clearly distinguish user-provided notes from externally verified evidence.
4. Represent governance metadata as structured, validated fields. Prefill values available from
   the selected project or governance work item, use controlled choices for taxonomies and people
   where possible, and visibly identify editable versus source-controlled fields.
5. Build and display one `Selected Source Package` manifest before confirmation. Bind downstream
   drafting eligibility to its exact identities, versions, fingerprints, and provider configuration.
6. Invalidate affected drafts, analysis, confirmations, previews, and outputs when the confirmed
   source package changes. Retain remote-operation reconciliation facts where applicable.
7. Keep the external PoC deterministic and offline. Before live connectors are separately approved,
   represent the interaction with synthetic inventories and explicit no-network disclosures.

Open decisions to resolve before moving R1 to `Ready`:

- Which evidence source types are required for the next iteration, and whether user-authored notes
  are in scope.
- Which governance metadata fields are required, optional, editable, or authoritative.
- Whether typed repository identifiers are needed in addition to authorized selectors.
- Whether the next batch is synthetic UI/contract preparation only or includes any separately
  approved enterprise discovery adapter. No live connector is implied by this item.
- Whether source changes invalidate only drafting and later stages or require a full workspace reset
  in specific cases.

### R2 — Separate SI drafting and governance review into two workflows

- **State:** `Verified`
- **Origin:** User acceptance testing of the Review Inputs mode switch after the 14 September
  baseline was completed.
- **Observed behavior:** The UI presents Project Context, Draft Solution Intent, Review Inputs,
  Human Review, and Generated Outputs as one linear five-stage workflow. Confirming a locally
  generated draft hands it directly to Review Inputs, while `Use Existing Solution Intent` and the
  Internal fake path bypass or clear the drafting stages. Review mode is selected only in Stage 3,
  but changing it can retroactively change how earlier stage progress is displayed.
- **Problem:** SI preparation and one governance review round are different business activities
  with different users, timing, inputs, and authoritative sources. A project team may draft and
  refine an SI before publishing it to Confluence, while a later Domain Architecture review should
  analyze a specific Confluence page version together with meeting evidence. Treating both as one
  browser-session pipeline makes the locally confirmed draft appear equivalent to the governed
  Confluence source, makes a normal review entry look like skipped work, and lets a review-provider
  choice redefine unrelated drafting progress.
- **Desired outcome:** Present `Draft a Solution Intent` and `Review a Solution Intent` as two
  peer-level, independently usable workflows. The drafting workflow prepares a human-confirmed
  draft for manual transfer. The governance review workflow begins from an explicitly selected
  authoritative SI snapshot and review evidence, then proceeds through Human Review and Generated
  Outputs. Connect the workflows through explicit source identity and user action rather than an
  automatic in-session handoff.

Confirmed direction to preserve during refinement:

1. Give each workflow its own entry point, stage labels, progress model, completion condition, and
   reset or recovery behavior. Do not number governance review as Stages 3–5 merely because the
   current implementation places drafting first.
2. Keep R1 Project Context and drafting-provider work within `Draft a Solution Intent`. Its output
   is a human-confirmed draft, not proof that a governed Confluence SI exists and not an automatic
   review input.
3. Begin `Review a Solution Intent` with selection and confirmation of an existing authoritative SI
   source plus transcript and review metadata. Entering this workflow is normal behavior, not a
   drafting bypass and not a `Skipped` state.
4. Keep workflow choice separate from source/provider configuration. Offline, fake, and any future
   approved internal adapters determine how a workflow obtains or processes data; they do not decide
   whether the other workflow was required or completed.
5. Preserve Stage 3 onward as the highest-priority real internal integration vertical slice when
   time or interface availability requires phased delivery. Describe unintegrated drafting
   capabilities as remaining scope, not as unnecessary or intrinsically optional product behavior.
6. Keep the external PoC deterministic and no-network. It may demonstrate either workflow with
   synthetic sources without implying Confluence publication, Teams retrieval, AIF drafting, or any
   other live capability.
7. Preserve human confirmation before a draft is exported for manual transfer and before a reviewed
   record generates outputs. No workflow state implies formal architecture approval.
8. Do not include Confluence page creation or update in the collected refinement scope. Reconsider
   write-back only if the user later reopens it after actual compliance, permission, target, and
   interface constraints are understood and explicitly approves that separate scope.

Open decisions to resolve before moving R2 to `Ready`:

- The exact landing page, navigation labels, and local step numbering for the two workflows.
- Whether the drafting workflow ends with copy/download only or also offers a convenience link to
  start a new review after the user separately selects the published Confluence page.
- Whether the two external synthetic demonstrations use one project at different lifecycle moments
  or deliberately distinct projects, and how either choice avoids implying automatic publication.
- Which drafting completion artifacts and provenance facts the user needs before manually creating
  or updating the Confluence SI.
- How existing session state, route guards, reset behavior, and maintained documentation migrate
  from one five-stage workflow to two bounded workflows.
- How R2 depends on R1 source acquisition and on the authoritative review-source contract in R5.

### R3 — Realistic synthetic scenario for the internal fake workflow

- **State:** `Accepted`
- **Origin:** User acceptance testing of the Internal fake path after the 14 September baseline was
  completed.
- **Observed behavior:** The primary offline fixture contains a 1,661-word SI and a 32-line review
  transcript, with three findings, one decision, one risk, two actions, one open question, and two
  missing-information items. The Internal fake fixture contains a 66-word SI and a three-line
  transcript, with one finding, one action, one missing-information item, and no decisions, risks,
  or open questions. Its minimal content is sufficient to exercise the Confluence/AIF contracts,
  evidence assignment, and legitimate empty collections, but Stage 4 presents a much thinner and
  less representative review.
- **Problem:** A contract-minimal fixture is useful for isolated boundary and edge-case tests, but
  using it as the primary Internal fake demonstration weakens product realism and can make the
  integration path appear less capable than the offline path. Incidental empty categories obscure
  the Human Review and evidence-traceability value that the judge feedback prioritized. Synthetic
  data should remain safe and deterministic while still resembling a credible architecture review.
- **Desired outcome:** Give the Internal fake workflow a coherent, internally shaped synthetic
  scenario with enough SI depth, meeting discussion, participants, review categories, and grounded
  evidence to exercise a representative Human Review. Separate demo realism from minimal contract
  and empty-state coverage so the primary demonstration does not depend on an intentionally tiny
  boundary fixture.

Confirmed direction to preserve during refinement:

1. Keep all content fictional, deterministic, non-confidential, and clearly labelled as synthetic.
   Realism must come from internally consistent architecture detail and review interactions, not
   copied enterprise data or invented claims about live connectivity.
2. Expand the primary Internal fake SI and transcript together. The structured fake AIF result must
   remain traceable to exact quotes and supported SI sections, speakers, and timestamps.
3. Provide representative nonempty coverage across findings, decisions, risks, actions, open
   questions, and missing information unless a deliberately empty category serves a clear demo
   purpose. Do not add items merely to inflate counts or weaken validation standards.
4. Preserve minimal, zero-item, and malformed-response coverage in dedicated contract tests or
   purpose-specific fixtures instead of making the main demo scenario carry every edge case.
5. Align the scenario with the `Review a Solution Intent` workflow under R2 and the authoritative
   review-source contract under R5. If the drafting and review demonstrations share one synthetic
   project, represent the Confluence publication boundary explicitly rather than passing local draft
   session state directly into review.

Open decisions to resolve before moving R3 to `Ready`:

- Whether to expand the current Synthetic Order Routing Service scenario or replace it with another
  clearly distinct internally shaped scenario. Reusing the offline fixture would not demonstrate a
  genuinely non-bundled provider path.
- The appropriate SI sections, transcript length, participant roles, and representative item counts
  for a credible demo without creating excessive review workload.
- Whether every review collection must be nonempty in the primary demo or whether one intentional
  empty state should remain visible.
- Which existing minimal inputs should remain as dedicated contract fixtures and which should be
  replaced by the realistic primary demo package.
- How fixture changes will remain synchronized across the Confluence storage response, canonical SI,
  transcript, metadata, fake AIF response, runtime wiring, and validation tests.

### R4 — Show pending human-review changes before confirmation

- **State:** `Verified`
- **Origin:** User acceptance testing of editable fields in Stage 4 after the 14 September baseline
  was completed.
- **Observed behavior:** Stage 4 lets the reviewer edit the proposed outcome and item fields or
  exclude proposed items, but it does not identify which current values differ from the analyzed
  proposal. The normalized field-change and exclusion summary is built only after the reviewer
  confirms the record and is shown in Stage 5.
- **Problem:** While editing a nontrivial review, users cannot quickly distinguish untouched
  provider proposals from pending human overrides, assess changes across tabs, or notice an
  unintended edit before confirmation. The Stage 5 summary remains valuable as the confirmed
  record, but it arrives too late to support the Stage 4 review task itself.
- **Desired outcome:** Give Stage 4 lightweight, immediate awareness of unconfirmed human edits and
  exclusions while retaining Stage 5 as the authoritative summary of changes that were actually
  confirmed and used to generate outputs.

Confirmed direction to preserve during refinement:

1. Mark a field or item when its current editable value differs materially from the analyzed
   proposal. Use wording such as `Modified`, `Human override`, or `Excluded`, and make clear that
   the change remains unconfirmed.
2. Provide a concise page-level and/or tab-level pending-change count so users can locate edits
   without expanding a full before-and-after report beside every field.
3. Remove a pending-change marker when the user restores the analyzed value. Use the same
   normalization semantics as the confirmed Stage 5 summary so whitespace, blank optional values,
   enums, and dates do not create inconsistent or misleading results.
4. Distinguish a modified valid value from an invalid in-progress value. Stage 4 may help users
   identify both, but only successful reviewed-record validation may produce confirmed outputs.
5. Keep the indication visually restrained and accessible. Do not present normal human overrides
   as errors, rely on color alone, emit a notification for every keystroke, or use fragile DOM
   targeting merely to recolor native widgets.
6. Preserve the complete confirmed before-and-after and exclusion summary in Stage 5. The Stage 4
   surface describes pending edits; it is not an audit record and must not imply that changes were
   saved, confirmed, published, or formally approved.

Open decisions to resolve before moving R4 to `Ready`:

- The exact combination of field badges, item-level markers, tab counts, and page-level summary
  that provides sufficient awareness without making the review form visually noisy.
- Whether excluded cards remain fully visible but de-emphasized or collapse to a compact retained
  evidence view before confirmation.
- How temporarily invalid dates or other incomplete values contribute to pending-change and
  validation indicators.
- Whether the existing normalized comparison can be reused safely for live drafts or needs a
  separate tolerant comparison that does not require constructing a fully valid reviewed result.
- How pending indicators persist across routed Back/Return navigation without altering the
  confirmed snapshot or the existing source-input invalidation rules.

Resolution: implemented and verified through
`docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_03.md`.

### R5 — Authoritative SI and user-provided transcript intake for governance review

- **State:** `Verified`
- **Origin:** User acceptance testing and product-boundary review of the Stage 3 inputs after the
  14 September baseline was completed.
- **Observed behavior:** Offline Review Inputs exposes editable SI and transcript text areas and can
  receive the locally confirmed Stage 2 draft directly. Internal fake loads a versioned synthetic
  Confluence snapshot into a read-only SI field but supplies the transcript from bundled runtime
  configuration; the transcript remains editable without an explicit imported, edited, or confirmed
  provenance state. The MVP has no transcript upload path.
- **Problem:** A governance review should use the SI actually maintained in Confluence rather than a
  local drafting-session value that may never have been published. Until Teams retrieval exists,
  users need a transparent manual transcript path, but unrestricted editable text must not be
  represented as an unmodified Teams record. The current two review modes expose inconsistent source
  semantics and do not let users confirm one clearly identified review-input package.
- **Desired outcome:** Start `Review a Solution Intent` from one explicitly selected, versioned,
  read-only Confluence SI snapshot plus a user-provided review transcript and validated review
  metadata. Preserve the provenance and exact content used for analysis, label manual or edited
  transcript content truthfully, and require explicit confirmation of the complete review package
  before analysis.

Confirmed direction to preserve during refinement:

1. Treat the selected Confluence page snapshot as the authoritative SI review source. Display its
   page identity, space, URL, version, retrieval time, canonicalizer version, content fingerprint,
   and validation status; allow selection or refresh but not direct SI body editing in Review Inputs.
2. Bind analysis eligibility to the exact SI page ID, version, canonicalizer version, content
   fingerprint, review metadata, transcript content, and provider configuration. A changed or
   refreshed source must invalidate affected analysis, confirmation, preview, and outputs while
   retaining remote-operation reconciliation facts where required.
3. Until a Teams adapter is separately approved, accept a transcript through explicit user input.
   Support paste and consider bounded file upload without implying Teams retrieval. Clearly label
   the source as user-provided and indicate when imported content has been edited.
4. Bind transcript evidence to the exact user-confirmed transcript snapshot analyzed by the
   provider. Preserve enough import and edit provenance to avoid presenting modified text as the
   untouched Teams export; provider-supplied evidence references remain untrusted.
5. Recommend a canonical utterance structure such as `[timestamp] Speaker: text` for precise
   locator validation, while defining truthful degraded behavior when timestamps or speakers are
   absent. Do not invent unavailable locators.
6. Build and display one confirmed governance-review input manifest before Analyze. Keep the
   deterministic external path and internal fake no-network while representing the same source
   roles and trust boundaries.
7. Do not pass a locally confirmed drafting result directly into governance review as though it
   were the Confluence source of truth. Any convenience handoff from the drafting workflow must
   require separate selection and validation of the published page snapshot.

Open decisions to resolve before moving R5 to `Ready`:

- How users discover or identify the Confluence SI page, which fields are source-controlled, and
  whether typed page IDs or URLs are accepted in addition to authorized selection.
- Whether the first bounded transcript intake supports paste only or also file upload, and which
  formats are accepted. File upload is outside the current MVP contract and requires explicit scope.
- Whether uploaded or pasted raw content is retained alongside an editable normalized transcript,
  and what minimum provenance can be supported without introducing a database or durable audit log.
- Whether transcript edits require a reason, a separate confirmation, or only an `Edited after
  import` disclosure in the external PoC.
- Which metadata values come from Confluence, an ADO governance item, user input, or controlled
  configuration, and how authoritative versus editable values are distinguished.
- How source-package confirmation, refresh, and invalidation interact with the two-workflow
  navigation and reset model in R2.

### R6 — Purpose-driven Markdown presentation across the workflows

- **State:** `Verified`
- **Origin:** User acceptance testing of inconsistent rendered and source Markdown presentation
  after the 14 September baseline was completed.
- **Observed behavior:** Stage 1 presents the SI template and supporting-document Markdown as raw
  code. Stage 2 presents the confirmed template sources and the full editable SI draft as raw text
  areas without a rendered preview. Stage 3 also presents the full SI in a text area, including
  when the Internal fake source is read-only, while the transcript remains plain editable text.
  Stage 4 presents exact supporting-evidence quotes as read-only code. Stage 5 renders the review
  record and Azure DevOps descriptions for reading, provides an explicitly labelled raw Markdown
  view of the review record, exposes exact JSON separately, and retains verbatim evidence quotes.
- **Problem:** The current mixture is only partly intentional. Raw presentation correctly protects
  editable content, verbatim evidence, and machine payloads, but long reader-facing Markdown in
  Stages 1–3 is difficult to scan and does not provide the document hierarchy, tables, or lists that
  the markup is intended to express. The UI does not consistently explain whether a view exists for
  reading, editing, exact-source inspection, or machine verification. In future non-synthetic
  inputs, unescaped Markdown control characters in user or source content could also alter the
  apparent structure of a rendered output and weaken evidence fidelity.
- **Desired outcome:** Apply one purpose-driven presentation policy across both workflows:
  reader-facing Markdown defaults to a rendered view; editable Markdown retains an exact source
  editor with an accessible rendered preview; evidence, transcripts, logs, and machine payloads
  remain verbatim; and generated documents provide both clearly labelled rendered and exact-source
  views. Rendering must not obscure source identity, editability, or evidence provenance.

Confirmed direction to preserve during refinement:

1. Present reader-facing SI templates, supporting documents, and authoritative SI snapshots as
   rendered Markdown by default, with a clearly labelled source view where exact inspection is
   useful. A rendered view must not imply that the source is editable or locally authoritative.
2. Keep SI drafting in an exact Markdown editor and add a rendered preview through tabs, a split
   view, or another comparably clear interaction. Preserve the user's raw edits as the value used
   for confirmation and any later export.
3. Under R5, present the read-only Confluence SI snapshot as a rendered document by default and
   provide an exact source-snapshot view for locator and evidence checks. Do not add SI body editing
   to the governance-review workflow.
4. Keep user-provided transcripts as editable plain text rather than interpreting them as Markdown.
   Preserve explicit source, import, edit, and confirmation disclosure from R5.
5. Keep Stage 4 supporting-evidence quotes read-only and verbatim. Markdown punctuation contained in
   quoted evidence must not change its displayed meaning or apparent structure.
6. Preserve the Stage 5 rendered/raw review-record views, rendered human-readable Azure DevOps
   previews, exact JSON representations, and downloads. Use unambiguous labels such as `Rendered`,
   `Markdown source`, and `JSON` rather than relying on visual styling alone.
7. Escape or otherwise safely delimit user-controlled and source-controlled text when composing
   rendered Markdown so headings, lists, links, and emphasis cannot be introduced accidentally.
   Retain the exact original value in the traceable source or payload representation.
8. Preserve accessible keyboard navigation, readable long-line wrapping, and clear read-only versus
   editable states. Do not make users compare two views merely to determine which content will be
   analyzed, confirmed, downloaded, or included in an output.
9. Give long rendered documents an explicit preview boundary so their internal Markdown headings do
   not compete visually with application sections such as `Generated review record` and
   `Azure DevOps work-item previews`. Place the rendered and source views inside a labelled,
   read-only document-preview region with a restrained border, spacing, and background treatment.
   Preserve the document's content and heading semantics; do not rewrite its Markdown merely to fit
   the surrounding application hierarchy.

Open decisions to resolve before moving R6 to `Ready`:

- Whether drafting uses side-by-side editing and preview, tabs, or a responsive combination of both.
- Which Stage 1 source types warrant a rendered/source pair and which should remain code, plain text,
  or structured metadata only.
- Whether the Stage 3 authoritative SI source view displays canonical Markdown, Confluence storage
  representation, or both, and which exact representation evidence locators reference.
- The escaping and literal-quote rules required when structured fields and evidence are composed
  into review-record and Azure DevOps Markdown.
- Whether rendered previews update continuously or only on an explicit preview action for large
  documents, while remaining deterministic and accessible.
- Whether long document previews remain full-height or use a bounded scroll region. Prefer the
  simplest bordered full-document view unless user testing shows that page length materially hides
  later workflow content; any nested scrolling must remain keyboard accessible and usable on narrow
  screens.
- How R6 is packaged with the two-workflow presentation changes in R2 and the authoritative SI
  intake contract in R5 without expanding into Confluence write-back or live integration.

Resolution: implemented and verified through
`docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_03.md`.

### R7 — Separate governed Azure DevOps work-item delivery step

- **State:** `Accepted`
- **Origin:** User acceptance testing of the mode-specific `Prepare exact Create preview` control
  after the 14 September baseline was completed.
- **Observed behavior:** Stage 5 always shows provider-neutral Azure DevOps work-item previews and
  downloadable JSON. Only Internal fake mode additionally exposes an exact Create sequence:
  prepare a target-specific JSON Patch request, inspect it, confirm it separately, submit it once
  to an in-memory fake gateway, and verify the synthetic result. The UI renders that sequence below
  Generated Outputs and gates it directly on the selected review mode and the presence of an
  Internal fake Confluence snapshot. Offline mode has no exact Create sequence because its runtime
  does not supply a source snapshot or target and field mappings.
- **Problem:** Generating local review artifacts and creating records in an external system have
  different authority, reversibility, failure, reconciliation, and audit boundaries. Nesting the
  guarded Create interaction beneath Generated Outputs makes an important integration capability
  easy to miss and can blur the difference between a provider-neutral content preview, an exact
  target-bound request, and an executed external write. Coupling delivery availability to the
  analysis-mode label also makes an AIF or source-provider choice appear to control an independent
  Azure DevOps capability. Delivery eligibility is currently evaluated only after the user selects
  `Prepare exact Create preview`; for example, an action owner edited during Human Review may have
  no approved Azure DevOps identity mapping, but the UI provides no advance status and returns only
  a generic blocking error without naming the affected action, current owner, or correction path.
- **Desired outcome:** Add a distinct governed work-item delivery step after Generated Outputs in
  the `Review a Solution Intent` workflow. The step demonstrates and, only in a separately approved
  live environment, performs the controlled transition from human-confirmed actions to exact Azure
  DevOps Create requests. Keep locally generated outputs available regardless of delivery outcome,
  and expose delivery based on explicit source, action, target, mapping, and connector eligibility
  rather than the analysis-provider mode name.

Confirmed direction to preserve during refinement:

1. Treat this as the fourth step of the governance-review workflow defined by R2, not as a global
   `Stage 6` appended to the obsolete five-stage linear model. Use a purpose-oriented label such as
   `Work Item Delivery` or `Create ADO Work Items`; finalize the user-facing name before readiness.
2. Keep Generated Outputs local, inspectable, and downloadable before delivery begins. A failed,
   unavailable, cancelled, or unknown delivery must not invalidate the confirmed reviewed record,
   meeting minutes, or provider-neutral work-item previews.
3. Do not equate `Prepare exact Create preview` with the whole delivery step. Preserve an explicit
   sequence covering eligible-action selection, target and mapping validation, exact request
   preparation, request inspection, separate human confirmation, single Create submission, GET
   verification, and receipt or reconciliation status.
4. Make delivery availability capability-based. Require a confirmed reviewed result, eligible
   action, validated source snapshot or manifest, approved Azure DevOps target and mappings, and a
   configured delivery provider. Changing any bound source, action, target, mapping, or reviewed
   content must revoke the current preview and confirmation.
5. Evaluate and display delivery eligibility before request preparation. Give every selected action
   a concise status such as `Ready` or `Needs identity mapping`, show the current owner and other
   unmet mappings, and provide a direct correction path. Disable the preparation action when it
   cannot succeed rather than relying on a generic error after the click; retain a precise blocking
   message for race, invalidation, and server-side revalidation failures.
6. Keep the human-reviewed action owner distinct from the Azure DevOps assignee identity. Editing an
   owner must remain legitimate review work and must not silently select, guess, or create an ADO
   identity. Resolve delivery through an authorized identity selector or explicit approved mapping,
   and make any different delivery assignee visible without rewriting the reviewed evidence.
7. Use stable approved identity identifiers behind user-facing display names. Do not use fuzzy name
   matching, silently normalize two distinct people into one identity, or expose an unrestricted
   free-text assignee as though it were validated. The deterministic external demo must use a
   coherent synthetic identity inventory and clearly identify unmapped test values.
8. Distinguish at least not prepared, prepared, confirmed, submitting, succeeded, definitely failed,
   and unknown-result states. Prevent direct resubmission after success or an unknown result, retain
   known remote identifiers, and reconcile by correlation before any separately authorized retry.
9. Represent non-applicable and unavailable cases truthfully. A review with no confirmed actions
   should state that there are no work items to create; missing connector or mapping configuration
   should identify the unmet eligibility without blocking access to Generated Outputs.
10. Keep the external demonstration deterministic and no-network while showing the complete guarded
   delivery interaction against a clearly labelled synthetic target and in-memory gateway. Do not
   imply that a fake receipt proves live Azure DevOps connectivity.
11. Permit real Azure DevOps creation only in separately approved internal scope after the actual
   endpoint, authentication, permissions, target project, work-item type, field and identity
   mappings, correlation behavior, and controlled test target have passed their acceptance gates.
   Do not add credentials, internal identities, or real target details to this repository.
12. Keep single-item Create, explicit confirmation, immutable evidence traceability, source and
   request fingerprints, single-submit protection, and post-create verification as the minimum
   safety baseline. Bulk publication, automatic retries, ADO Update, and Confluence write-back are
   not implied by this item.
13. Use schema-appropriate controls for user-visible delivery fields. Prefer searchable controlled
   selectors for values that must resolve to approved identities, work-item types, projects,
   priorities, parent work items, or other target taxonomies; show both human-readable labels and
   stable identifiers where disambiguation matters. Keep narrative titles and descriptions as text
   inputs subject to explicit target constraints rather than forcing them into artificial choices.
14. Do not constrain the Human Review action owner to the Azure DevOps identity inventory merely to
   make publication succeed. Preserve the reviewed owner value and its mapping status, then use a
   strict authorized selector for the delivery assignee when resolution is required. Any deliberate
   difference between reviewed owner and delivery assignee must be visible and separately confirmed.
15. Replace free-text date entry with a nullable date picker for user-authored due dates unless an
   accessibility or source-preservation requirement justifies exact text entry. An empty date picker
   must remain genuinely unset rather than defaulting to today. Apply business date bounds only when
   they come from an approved rule, and retain deterministic ISO dates in models and payloads.
16. Use sentence case and task-oriented language for delivery controls. Replace constructions such
   as `Prepare exact Create preview` and `Confirm exact preview` with concise verb-led labels such as
   `Preview Azure DevOps request`, `Confirm request`, and `Create work item`. Identify a synthetic
   target through the surrounding status and confirmation text instead of mixing API-operation
   capitalization into the button label. Retain exact HTTP method, JSON Patch, endpoint, and
   fingerprint terminology in the technical request details where it helps verification.
17. Present every prepared request through two synchronized layers. Default to a human-readable
   work-item summary and field-mapping view that shows the selected action, target project and type,
   title, reviewed owner, resolved assignee, due date, priority, parent, classification, tags, and
   any blocking or override status. Keep the exact endpoint, content type, JSON Patch operations,
   correlation, and binding fingerprints in a clearly labelled technical view. The technical JSON
   remains the immutable request being confirmed; the readable view must be derived from that same
   request and must not omit a material outgoing field or imply that a summarized value is the
   payload itself.

Open decisions to resolve before moving R7 to `Ready`:

- The final step name and whether the navigation presents delivery as a required conditional step,
  an explicit completion branch, or a separately resumable activity after output generation.
- Whether the next external demo reuses the existing Internal fake target or gives the Offline demo
  an equivalent synthetic source manifest and delivery provider without collapsing their distinct
  analysis contracts.
- Whether the first implementation retains single-action delivery or supports a reviewed queue of
  multiple actions with individual eligibility, confirmation, receipt, and reconciliation state.
- Which target and mapping readiness facts are visible to the reviewer and which require a separate
  operator or administrator configuration surface.
- Whether an unmapped action owner must be resolved by returning to Human Review, can be mapped to
  an authorized ADO identity within Work Item Delivery, or may produce an explicitly unassigned
  work item under approved target rules; none of these choices may silently alter the reviewed
  action owner.
- Whether Human Review owner controls use only known review participants, an authorized people
  inventory with an explicit unmapped value, or controlled suggestions plus new-entry support. ADO
  delivery assignee selection remains strict even if review ownership permits a new value.
- Which date rules, if any, disallow past dates or impose delivery horizons, and whether those rules
  differ between review findings and publishable action items.
- Whether the governance parent is always source-controlled from review metadata or can be selected
  from an authorized ADO inventory in Work Item Delivery; avoid an unrestricted raw numeric ID when
  a verified selector is available.
- Whether the human-readable request preview uses compact cards plus a field table, peer
  `Work item` and `Request JSON` tabs, or an equivalent responsive layout, and which technical
  identifiers remain visible without opening secondary details.
- How users resume or reconcile a prior succeeded or unknown operation after session reset without
  adding a database or overstating exactly-once guarantees.
- How R7 depends on the R2 workflow split, the R5 authoritative source manifest, and the R6
  rendered-versus-exact-request presentation policy.

### R8 — Order-independent Review Inputs acquisition and visible readiness feedback

- **State:** `Verified`
- **Origin:** User acceptance testing of the `Use Existing Solution Intent` shortcut followed by
  `Load Sample Transcript & Metadata` after the 14 September baseline was completed.
- **Observed behavior:** `Use Existing Solution Intent` in Stage 1 changes the active route to
  Review Inputs but does not load, select, or confirm an SI. The transcript-and-metadata button is
  nevertheless enabled. Its state helper rejects the click when the current SI is blank because it
  was designed to preserve an already confirmed or entered SI. The resulting error is rendered only
  at the bottom of the page below the input tabs, while the action-area status remains `Waiting for
  a review package`; in a normal desktop viewport the button therefore appears to do nothing. The
  existing focused application test covers the successful order in which the SI is entered first,
  but not this shortcut-to-failed-action experience.
- **Problem:** The shortcut label implies that the user is beginning work with an existing SI, but
  the destination neither acquires that source nor makes the missing prerequisite prominent. An
  enabled action that cannot succeed is a false affordance, and distant stale status or error text
  does not provide observable action feedback. More fundamentally, requiring an SI before a user
  can import an independently available transcript or metadata package imposes an unnecessary input
  order that conflicts with the explicit review-input manifest planned in R5.
- **Desired outcome:** Let users acquire the authoritative SI, transcript, and review metadata in a
  clear order of their choosing, show the state of each input immediately where actions occur, and
  gate analysis only on one complete, validated, explicitly confirmed review-input manifest. Every
  click must produce visible localized progress, success, or actionable failure feedback.

Confirmed direction to preserve during refinement:

1. Replace the legacy drafting shortcut with an explicit entry into the independent `Review a
   Solution Intent` workflow defined by R2. Use task-oriented wording such as `Review an existing
   Solution Intent`; entering the workflow must not imply that an SI has already been found, loaded,
   published, or confirmed.
2. Permit SI selection, transcript paste or upload, and review-metadata acquisition in any order.
   Loading one component must preserve other valid components, truthfully update its provenance,
   and invalidate only the affected analysis or later state. Do not require an SI merely to store a
   transcript that is independently available.
3. Display a compact readiness manifest near the input actions with separate states for SI,
   transcript, and metadata, followed by the overall analysis state. Distinguish `Missing`, `Loaded`,
   `Edited`, `Invalid`, and `Confirmed` where those terms apply; do not rely on the currently selected
   tab to reveal whether an action succeeded.
4. Keep Analyze unavailable until the complete package satisfies R5 and has been explicitly
   confirmed. Explain every unmet requirement beside the disabled action without treating a normal
   partial package as an application error.
5. Show action feedback in or immediately below the control that triggered it. On success, identify
   exactly what was loaded and what remains missing. On failure, name the failed component and a
   direct correction path; do not place the only message after long off-screen content.
6. Preserve the deterministic offline path and make its controls semantically distinct: loading the
   full bundled review package, loading only synthetic transcript and metadata, and entering or
   selecting an SI must not appear interchangeable. Apply the same input roles and readiness model
   to Internal fake without implying live Confluence or Teams access.
7. Keep partial-input state recoverable across normal routed navigation and make reset scope clear.
   A mode, source, or provider change must retain or clear components only according to their actual
   dependency and provenance, with existing stale-analysis and output protections preserved.
8. Add focused state and rendered-flow coverage for both load orders, shortcut entry with an empty
   SI, partial readiness, localized success and failure feedback, tab-independent observability,
   Analyze gating, and later invalidation. A successful helper test alone is not sufficient UI
   acceptance evidence.

Open decisions to resolve before moving R8 to `Ready`:

- Whether review metadata remains bundled with transcript intake or becomes a separately visible
  source/control with its own provenance and confirmation state.
- Whether successful transcript loading changes focus to the transcript view or leaves the current
  view unchanged while relying on the readiness manifest and localized confirmation.
- The final workflow-entry and input-action labels after R2 removes the global Stage 1–5 model.
- Whether partial review packages persist only in the Streamlit session or may be exported and
  resumed without adding a database.
- How R8 shares source selection, confirmation, refresh, and invalidation behavior with R5 without
  duplicating the authoritative review-input contract.

### R9 — Deployment-controlled visibility for synthetic review modes

- **State:** `Accepted`
- **Origin:** User acceptance discussion about the role of Offline and Internal fake after live
  enterprise integration is complete.
- **Observed behavior:** The current application always exposes `Offline demo` as the safe default
  review mode. `Internal fake · no network` is hidden unless explicitly enabled with
  `AGC_INTERNAL_FAKE_ENABLED`, after which both technical modes are presented in the Review Inputs
  UI. These modes are currently necessary for the hackathon demonstration, deterministic
  regression, integration-contract rehearsal, and a no-network fallback demonstration.
- **Problem:** Once the real Confluence, AIF, and Azure DevOps capabilities are implemented and
  accepted, ordinary production users should not have to select among implementation providers or
  see synthetic modes that are irrelevant to their work. Permanently removing those paths would,
  however, discard valuable deterministic test, training, troubleshooting, and demo capabilities.
  Automatically falling back from a failed live provider to synthetic analysis would be more
  dangerous because users could mistake fabricated results for enterprise-derived results.
- **Desired outcome:** Make review-mode availability and visibility easy to control by deployment
  profile or equivalent validated configuration. A production profile should expose only accepted
  live capabilities to ordinary users, while controlled demo, development, and automated-test
  profiles can retain Offline and Internal fake without code edits. Hidden synthetic modes must
  remain clearly separated from live behavior and must never become an implicit fallback.

Confirmed direction to preserve during refinement:

1. Separate user workflow choice from provider or connector selection. In a production profile,
   present the review workflow and truthful source/capability status rather than a technical
   Offline/Internal fake/live mode selector.
2. Support explicit deployment-level visibility policy with safe, documented profiles or an
   equivalent centralized configuration: production exposes accepted live capabilities; demo or
   training may expose the deterministic Offline path; development and automated tests may also
   enable Internal fake.
3. Keep the configuration convenient to change without editing application code, but validate it
   at startup and default safely. A missing, contradictory, or incomplete live configuration must
   not accidentally expose or select a synthetic mode in a production deployment.
4. Never silently degrade a live request to Offline or Internal fake. If a required live capability
   is unavailable, stop the affected action and show a clear, actionable service-status message.
   Any deliberate synthetic session must be explicitly enabled and continuously labelled as
   synthetic and no-network.
5. Retain the deterministic Offline implementation and Internal fake contracts for regression,
   controlled demonstration, integration development, and failure-path testing after live
   integration is introduced. Hiding them from ordinary users is not authorization to delete their
   code, fixtures, provider boundaries, or tests.
6. Gate production hiding on end-to-end acceptance of the relevant live path, including source
   retrieval, validated analysis, human review, delivery preview and confirmation, Create behavior,
   verification, and recoverable failure handling. Connecting an endpoint alone is not sufficient.
7. Ensure route state, saved session state, direct navigation, and stale browser state cannot expose
   or continue using a mode that the active deployment policy disallows. Mode-policy changes must
   invalidate incompatible source, analysis, confirmation, and delivery state according to the
   existing provenance boundaries.
8. Add focused configuration and rendered-UI tests for each supported deployment profile, safe
   startup failure, direct-route access, stale session state, explicit synthetic labelling, and the
   prohibition on automatic synthetic fallback.

Open decisions to resolve before moving R9 to `Ready`:

- The exact deployment-profile model and configuration source, including whether policy is fixed at
  process startup or can be changed through an access-controlled administrative surface.
- Which authenticated roles, if any, may access a controlled demo or diagnostic mode in an
  otherwise production deployment; authentication and authorization remain outside current scope.
- The live-capability acceptance checklist and release authority that permit synthetic controls to
  be hidden from the production UI.
- Whether training is a separate deployment profile or a separately hosted deterministic
  application, and what synthetic-data banner and environment identity it requires.
- How R9 composes with the R2 workflow split, R5 input-source manifest, and R7 delivery capability
  without coupling one provider choice to unrelated workflow steps.

### R10 — Deliberate light-only application theme

- **State:** `Verified`
- **Origin:** User acceptance testing of the application while the browser or operating system is
  using Dark mode.
- **Observed behavior:** The application has no project-level Streamlit theme configuration, so its
  native widgets can follow or expose a dark presentation. The custom visual layer in `app.py` was
  designed with fixed light surfaces, dark text, light borders, and light-mode brand treatments.
  Combining dark native controls with those light custom regions produces inconsistent contrast,
  hierarchy, and component appearance.
- **Problem:** Properly supporting both Light and Dark modes would require a separate palette,
  systematic replacement or adaptation of hard-coded colors, asset review, and visual regression
  coverage across the full workflow. That work has low value for the time-limited PoC compared with
  completing the confirmed workflow, review, evidence, and enterprise-integration refinements.
- **Desired outcome:** Make the application intentionally and consistently Light-only for the
  current PoC, using Streamlit's native project theme configuration as the authoritative base. The
  result should remain light and readable regardless of the browser or operating-system preference,
  without presenting an unsupported in-app Dark mode choice.

Confirmed direction to preserve during refinement:

1. Add one project-level Streamlit `[theme]` configuration with `base = "light"`; do not define
   separate `[theme.light]` and `[theme.dark]` variants while this requirement remains active.
2. Define the native background, secondary background, text, primary, border, and sidebar colors
   needed to align Streamlit controls with the existing light visual language. Treat the native
   theme as the base and keep custom styling limited to product-specific layout and identity.
3. Do not implement a second Dark mode palette, theme-aware asset switching, or conditional
   `st.context.theme` styling in the current refinement scope.
4. Do not use additional CSS to override Streamlit's theme mechanism. During later implementation,
   review existing hard-coded custom colors only as needed to remove conflicts with the authoritative
   Light theme and preserve current product-specific presentation.
5. Keep status, warning, success, error, focus, disabled, code, Markdown, form, and sidebar content
   readable with adequate contrast. Fixing the base mode does not waive accessibility or interaction-
   state checks.
6. Verify the full application in at least one browser with both light and dark operating-system
   preferences and confirm that the application remains visually consistent and Light-only. Add a
   focused configuration assertion where practical, while treating rendered visual inspection as
   required acceptance evidence.
7. Document the Light-only product decision for demo and deployment operators. Reconsider dual-theme
   support only as a separately approved future refinement if the application moves beyond the PoC;
   do not imply that Dark mode is permanently prohibited.

Readiness decisions proposed in Batch 01 and subject to approval with that plan:

- Retain the existing action-red treatment as the native primary action color, while using the
  current light neutral, navy, blue, green, and border palette as the basis for exact theme tokens.
- Rely on the single `[theme]` configuration to remove the unsupported mode choice; add no separate
  settings-menu explanation unless rendered verification reveals misleading behavior.
- Verify the current routed workflow at a desktop viewport under both light and dark host color
  preferences, covering the initial context screen, drafting controls and editor, Review Inputs,
  Human Review including validation states, Generated Outputs, and the guarded fake delivery flow.
- Complete R10 against the current UI rather than blocking it on R2. Every later UI batch must rerun
  its own light-theme regression checks, so future restructuring cannot rely only on Batch 01
  evidence.

## 6. Accepted intake and dependency sequencing

The user accepted R1-R10 as subsequent implementation intent on 2026-09-10. Acceptance does not
resolve the open decisions recorded above, make every item ready, or authorize application changes.
The following sequence is the smallest currently coherent grouping assessment. Completed batches
retain their execution plans as verification evidence; later rows remain candidates that require a
new explicit decision and sole active plan.

| Sequence | Refinements | Rationale and readiness |
| --- | --- | --- |
| Batch 01 | R10 | Completed and verified in `docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_01.md`. |
| Batch 02 | R2, R5, R8 | Completed and verified in `docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_02.md`. |
| Batch 03 | R4, R6 | Completed and verified in `docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_03.md`. |
| Candidate 04 | R1 | Drafting-source discovery and manifest work is bounded to the drafting workflow after R2 establishes its independent navigation and reset model. Source-type and metadata decisions remain. |
| Candidate 05 | R3 | The realistic Internal fake fixture must align with the authoritative review-source contract and revised review workflow from Candidate 02. Scenario-content decisions remain. |
| Candidate 06 | R7 | Governed work-item delivery depends on the review workflow, authoritative source manifest, confirmed actions, and the rendered-versus-exact presentation policy. Delivery queue, mapping, and recovery decisions remain. |
| Readiness-gated | R9 | Deployment policy remains accepted but cannot become ready until separately approved live capabilities and their release authority exist; no live connector is authorized by this intake. |

## 7. Register maintenance and execution handoff

During the current user-testing period:

1. Add each new finding as a uniquely numbered item with observed behavior, desired outcome, and
   unresolved decisions.
2. Do not silently fold a finding into R1 unless it shares the same source-selection contract and
   acceptance boundary.
3. Record contradictions with the baseline specification explicitly instead of overwriting the
   historical acceptance evidence.
4. When intake is complete, review priorities and dependencies with the user, then mark selected
   items `Accepted`.
5. Promote an item to `Ready` only when its material product decisions and dependencies are
   sufficiently resolved for execution planning.
6. After accepted-scope planning is authorized, create the smallest coherent execution plan using
   `docs/exec-plans/README.md` and set the active-plan pointer at the top of this register. Keep the
   plan in `PROPOSED_AWAITING_USER_APPROVAL` and its items no higher than `Ready` until the user
   explicitly approves the plan; move included items to `In progress` only when implementation
   actually starts.
7. Keep component details, implementation steps, detailed tests, progress, discoveries, and
   verification evidence in that execution plan rather than this register.
8. On successful completion, mark the plan `COMPLETED_VERIFIED`, update the included items to
   `Verified`, clear the pointer, and retain the completed plan as historical evidence.
9. Stop a batch if a product decision is unresolved or verification fails. Record the exact state
   in the execution plan; do not infer completion from a clean test run or the end of a session.

No code, fixture, dependency, environment, or live-integration change is part of the current
requirements-intake update.
