# Post-baseline refinement Batch 06 — governed work-item delivery

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R7`

Approval boundary: On 2026-09-11, the user explicitly approved this execution plan and all
section 2 product decisions, including implementation, verification, and commit/push after
success. The user also required a pause for discovered issues or further review. Execution is
resumed after the user approved the correlation-identity repair on 2026-09-11.

Baseline revision: `849de071dd249a59cfb7f92ba749f1134fa456f1`

Current phase: `COMPLETE`

## 1. Scope

Separate Azure DevOps delivery from local artifact generation by adding a conditional fourth route,
`Work Item Delivery`, to the Review a Solution Intent workflow:

1. keep Generated Outputs complete and usable independently of delivery;
2. assess every confirmed action against explicit source, target, field, identity, parent, priority,
   and due-date requirements before request preparation;
3. present a reviewed-action delivery list with per-action readiness and prior operation status;
4. preserve single-item, exact-request preview, separate confirmation, at-most-once submission,
   correlation reconciliation, and GET verification; and
5. move the current Internal fake delivery interaction into the dedicated route with clearer
   task-oriented labels and synchronized human-readable and technical request views.

## 2. Approved product decisions

User approval on 2026-09-11 resolved the product decisions recorded for R7 as follows.

### Workflow position and completion semantics

- Use `Work Item Delivery` as the final user-facing step name. It is review step 4, not a global
  stage number and not part of the independent drafting workflow.
- Always show the fourth step in review progress so the delivery boundary is discoverable. Treat it
  as a conditional completion branch: the local governance workflow is complete when Generated
  Outputs exists, while delivery separately reports `Ready`, `Not applicable`, `Unavailable`, `In
  progress`, `Succeeded`, `Failed`, or `Needs reconciliation`.
- Add a thin `pages/work_item_delivery.py` route and a `Continue to Work Item Delivery` action from
  Generated Outputs. Keep meeting minutes, provider-neutral previews, downloads, change summary,
  and `Start New Review` on Generated Outputs regardless of delivery status.
- Permit the delivery route only when a confirmed reviewed result and Generated Outputs exist.
  Normal Back navigation returns to Generated Outputs without clearing delivery state.

### Capability and reviewed-action list

- Reuse the existing opt-in Internal fake target and in-memory gateway. Do not add an equivalent
  target to Offline mode. Offline outputs may open Work Item Delivery, which truthfully reports that
  no delivery provider is configured for that review package.
- Resolve capability from the confirmed review package, configured target/provider, and exact
  source identity rather than from the visible analysis-mode label. The current fake capability
  accepts only its configured synthetic page/ticket lineage and remains no-network.
- Show all confirmed actions as a reviewed delivery list, but retain one-action-at-a-time request
  preparation and Create. Each action independently shows reviewed owner, resolved assignee, due
  date, priority, parent mapping, readiness blockers, and any correlation-indexed operation status.
- Use a separate durable delivery-action selection key; changing the evidence-to-output comparison
  selector must not change which action is prepared for delivery.
- Retain one current preview and confirmation while keeping per-correlation operation history. A
  succeeded or unknown action remains protected from resubmission, while another ready action may be
  selected and processed independently.
- If the reviewed result contains no actions, show `Not applicable` and no request action. If the
  package has actions but no configured capability, show `Unavailable` without blocking or hiding
  Generated Outputs.

### Mapping and correction policy

- Keep Human Review owner entry flexible and separate from Azure DevOps identity. Do not constrain
  review ownership to the target inventory and do not silently rewrite it.
- In this batch, resolve delivery assignees only through the target's pre-authorized stable identity
  mapping. Do not add an assignee override or administration surface. An unmapped reviewed owner
  blocks only that action, names the owner and action, and provides a direct Back to Human Review
  correction path.
- Keep the governance parent source-controlled from confirmed review metadata and the approved
  target mapping. Do not expose raw numeric parent entry or an invented parent selector.
- Display target project, work-item type, API version, parent mapping, classification, identity
  resolution, and priority mapping as read-only readiness facts. Configuration remains outside the
  UI and repository contains only the existing synthetic target.
- Replace Human Review's free-text action due-date field with a nullable `st.date_input` initialized
  from the analyzed value. `None` remains genuinely unset; no past-date or delivery-horizon rule is
  added because no approved business rule exists. Use the installed Streamlit session-persistence
  contract or separate durable state so routed navigation does not silently reset dates.

### Request presentation and recovery

- Replace `Prepare exact Create preview`, `Confirm exact preview`, and
  `Submit once to fake Azure DevOps` with `Preview Azure DevOps request`, `Confirm request`, and
  `Create work item`. Keep exact Create, JSON Patch, endpoint, correlation, and fingerprints in the
  technical detail text.
- Present each prepared request through peer `Work item summary` and `Request JSON` tabs. Derive the
  readable summary from the immutable prepared request and target mapping; show action, target,
  title, reviewed owner, resolved assignee, due date, priority, parent, classification, tags, and
  any mapping difference. The technical tab shows endpoint, content type, exact JSON Patch,
  correlation, and all binding fingerprints.
- Continue to reconcile by correlation before Create and verify a known ID with GET. Distinguish not
  prepared, prepared, confirmed, submitting, succeeded, definitely failed, and unknown-result
  states in the delivery surface.
- Recovery remains session-local and honest. Reset retains correlation-indexed operation facts but
  never treats a process restart as evidence that no remote result exists. No database or
  exactly-once claim is added. Unknown results expose the correlation and known remote identifier,
  if any, and prohibit automatic or direct retry.

### Approved correlation-identity repair

The user approved this addition after the pre-implementation reproduction in section 12.
Preserve the original analyzed action position through human exclusions as a local delivery
binding. Keep the current compact output indices unchanged. Use the original position for
correlation; bind the compact position and original position to each exact request. Continue
checking retained legacy correlations for earlier compact positions before submission and during
reconciliation, so existing successful or unknown operations cannot lose protection during
migration. Never infer action identity from an editable title or owner.

Add regression coverage for success, unknown result, exclusions, restoration, legacy history,
and stale original-position bindings before proceeding to capability/readiness implementation.

## 3. Explicit non-goals

- Do not add live Azure DevOps, Confluence, Teams, AIF/LLM, identity, authentication, credentials,
  network, database, audit-store, RAG, or agent functionality.
- Do not implement bulk Create, automatic retry, Azure DevOps Update, governance-ticket update,
  Confluence write-back, or cross-session recovery.
- Do not add unrestricted assignee, project, work-item-type, parent, priority, classification, or
  endpoint entry.
- Do not change reviewed evidence, source content, or Human Review owner merely to make delivery
  eligible.
- Do not move or hide the provider-neutral work-item previews from Generated Outputs.
- Do not implement R9 deployment profiles or imply production readiness.

## 4. Dependencies and overlap boundaries

- Batch 02 is a completed prerequisite: R7 extends the independent Review a Solution Intent route
  hierarchy and consumes the authoritative review-input manifest from R5.
- Batch 03 is a completed prerequisite: the delivery route reuses pending-change semantics and the
  rendered-versus-exact presentation contract from R4 and R6.
- Batch 05 is a completed prerequisite: both Internal fake actions now have explicit transcript
  owners and safe `.invalid` target mappings, allowing per-action readiness and sequential delivery
  verification.
- Batch 04 drafting state remains independent and outside delivery invalidation.
- R9 remains readiness-gated. This batch adds no live capability or production visibility policy.

No unresolved blocker remains if the user approves every decision in section 2. Any requested
change to workflow completion, Offline availability, queue depth, assignee resolution, parent
selection, date rules, preview layout, or recovery scope must be incorporated before implementation.

## 5. Affected components and files

- `app.py` — fourth-step progress, route guard, Generated Outputs navigation, readiness list,
  request-summary/JSON tabs, task labels, and operation feedback.
- `pages/work_item_delivery.py` — thin file-backed route entry point.
- `src/architecture_governance_copilot/publication.py` — strict capability/readiness models and pure
  preflight assessment while preserving exact request and coordinator boundaries.
- `src/architecture_governance_copilot/runtime_dependencies.py` — explicit fake delivery capability
  descriptor bound to the configured synthetic source/target, without a live transport.
- `src/architecture_governance_copilot/ui_support.py` — delivery route/stage, durable selection,
  per-action operation projection, preview invalidation, and reviewed due-date state.
- `tests/test_publication.py`, `tests/test_runtime_dependencies.py`, `tests/test_ui_support.py`, and
  `tests/test_app.py` — preflight, route, state, date, readiness, request, recovery, and rendered-flow
  coverage.
- `README.md`, `SPEC.md`, and `DEMO.md` — maintained product truth and demonstration instructions.

The strict `SolutionIntentDrafter`, `GovernanceExtractor`, review-input manifest, evidence models,
fixture content, and provider-neutral output generators are not expected to change.

## 6. Implementation sequence

- [x] Confirm Batch 05 is verified, committed, pushed, and no plan remains active.
- [x] Reconcile R7 decisions with current routes, state, publication contracts, tests, and
  maintained documentation.
- [x] Verify the installed Streamlit contract supports nullable dates and session-persistent widget
  state.
- [x] Create this sole proposed plan and move R7 to `Ready` without treating it as implementation
  authorization.
- [x] Obtain explicit user approval of this execution plan and every section 2 decision.
- [x] Mark this plan `IN_PROGRESS`, move R7 to `In progress`, and record approval.
- [x] Repair stable action identity and verify retained legacy-operation protection.
- [x] Add strict capability and per-action readiness assessment with actionable blockers.
- [x] Add the guarded fourth route, workflow progress, navigation, and state isolation.
- [x] Replace free-text action due dates with nullable date inputs and focused state tests.
- [ ] Build the reviewed-action delivery list and synchronized readable/technical request views.
- [ ] Preserve and expose separate confirmation, single-submit, reconciliation, and read-back state
  with task-oriented labels.
- [ ] Synchronize maintained documentation and demo instructions.
- [ ] Run focused and full automated verification plus the browser acceptance matrix.
- [ ] Fix every in-scope failure before marking the batch verified.
- [ ] On success, mark this plan `COMPLETED_VERIFIED`, set R7 to `Verified`, clear the active
  pointer, commit, and push under the user's standing sequential-batch instruction.

## 7. Acceptance criteria

- Review progress contains Review Inputs, Human Review, Generated Outputs, and Work Item Delivery;
  drafting progress remains unchanged.
- Generated Outputs remains locally complete and usable before, during, and after any delivery
  state, including unavailable, failed, and unknown.
- Work Item Delivery is guarded by confirmed reviewed outputs and reports `Not applicable` for no
  actions or `Unavailable` for no configured package capability.
- Every action displays readiness before request preparation, including the reviewed owner, mapped
  identity, due date, priority, parent, target, and a precise action-specific blocker.
- An unmapped owner, missing required owner/date/parent, or unmapped priority cannot prepare a
  request and directs the user back to Human Review without changing the reviewed record.
- Human Review uses a nullable date picker for action due dates; blank stays `None`, ISO dates remain
  deterministic, and no unapproved temporal rule is enforced.
- Action selection is independent from the Generated Outputs comparison selector and persists across
  normal Back/Return navigation.
- Prepared request summary and technical JSON are derived from the same immutable preview and expose
  every material outgoing field plus correlation and binding identities.
- Each ready action may be processed one at a time. Succeeded and unknown actions cannot be directly
  resubmitted; other ready actions remain independently selectable.
- Internal fake completes the full no-network path for both synthetic actions with distinct
  correlations and verified receipts; Offline truthfully reports delivery unavailable.
- No route, status, receipt, or label implies formal architecture approval, live connectivity,
  exactly-once delivery, or durable audit storage.

## 8. Required verification

Automated commands from the repository root:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Focused tests must cover:

- strict readiness/capability models, stable ordering, mapped and unmapped identities, missing
  values, target/source mismatch, parent and priority mapping, no actions, and unavailable provider;
- route guards, four-step progress, local-output independence, separate selector persistence,
  Back/Return navigation, reset, source/result invalidation, and retained operation history;
- nullable date initialization, change, clear, normalization, validation, route persistence, and
  unchanged pending/confirmed change summaries;
- readable request-summary equality with exact JSON Patch fields and fingerprints;
- independent per-action preview/confirmation/correlation/history, stale binding revocation,
  succeeded and unknown resubmission protection, second-action delivery, and GET verification;
- Offline, Internal fake, drafting, provider-boundary, and evidence-traceability regressions.

Browser verification at desktop and narrow viewports must complete:

1. finish Offline review, inspect local Generated Outputs, open Work Item Delivery, and observe an
   actionable `Unavailable` state without losing downloads or outputs;
2. in Internal fake, confirm that both reviewed actions show `Ready` before preparation with exact
   owner, assignee, date, priority, parent, and target facts;
3. change an action owner to an unmapped value in Human Review, regenerate outputs, and verify the
   named blocker and correction path before restoring the mapped owner;
4. clear and restore a due date with the nullable picker and verify pending-change and readiness
   behavior without a default-to-today substitution;
5. select an action independently from the evidence comparison, preview its request, inspect both
   readable and technical tabs, confirm it, create once, and verify its receipt/read-back;
6. select the second action, verify independent readiness and correlation, and complete its guarded
   submission without altering the first receipt;
7. exercise Back/Return navigation and confirm local outputs plus delivery history persist; verify
   direct access without outputs is guarded;
8. verify keyboard-accessible controls, sentence-case labels, light-only styling, readable stacked
   content, and no horizontal overflow at a narrow viewport.

## 9. Compatibility, state, and rollback

- Increment the session schema for the new delivery stage and durable selection/date state. Remove
  obsolete delivery widget values during migration without erasing correlation-indexed operation
  history that remains safe to reconcile.
- Keep `AdoPublicationPreview`, confirmation, request fingerprints, coordinator, and gateway
  protocols backward compatible unless a stricter readiness contract requires an additive field.
- A reviewed-result, source, target, mapping, or selected-action change revokes only the current
  preview and confirmation. It does not erase Generated Outputs or terminal operation history.
- Existing output-action comparison state remains independent from delivery selection.
- Rollback removes the route and readiness presentation, restores the prior date widget, and
  returns fake delivery to its previous Generated Outputs location as one coherent unit while
  preserving the already verified publication coordinator.
- If verification fails, retain R7 as `In progress`, keep this plan active, and record the exact
  failure. Do not bypass readiness, weaken confirmation, retry an unknown result, or hide Generated
  Outputs.

## 10. Progress

- [x] Accepted requirement and current implementation reconciled.
- [x] Proposed product decisions consolidated.
- [x] Installed Streamlit date/state behavior verified.
- [x] Sole active-plan pointer assigned for review.
- [x] User approval recorded.
- [x] Preflight and capability contracts implemented.
- [x] Fourth route and state lifecycle implemented.
- [x] Nullable date interaction implemented.
- [x] Delivery list and request views implemented.
- [x] Automated verification passed.
- [x] Browser verification passed.
- [x] Maintained documentation synchronized.
- [x] Completion record finalized and active pointer cleared.

## 11. Decisions and important discoveries

- Batch 05 completed at `849de071dd249a59cfb7f92ba749f1134fa456f1`; the working tree was clean
  and local HEAD matched the remote branch when Batch 06 planning began.
- The existing publication coordinator already provides exact binding fingerprints, correlation
  lookup before Create, one-submit protection, explicit success/failure/unknown states, retained
  known IDs, and GET read-back verification. This batch should expose those controls rather than
  replace them.
- Delivery currently appears only below Generated Outputs, derives selection from the unrelated
  evidence-comparison selector, performs readiness validation only after preparation is clicked,
  and checks Internal fake mode directly in the renderer.
- The current Human Review action due date is free text parsed only during form validation. The
  installed Streamlit `st.date_input` accepts `value=None` and `persist_state="session"`, so the
  approved nullable-date behavior requires no dependency change or current-date substitution.
- The current Internal fake package has two mapped action owners and one source-controlled parent
  ticket, providing deterministic ready cases. Offline has no configured delivery target and is the
  truthful unavailable case.

## 12. Actual verification evidence

Pre-implementation inspection on 2026-09-11:

- Read `AGENTS.md`; checked status, branch, HEAD, remotes, recent history, and fetched origin.
  HEAD and the remote branch both resolve to `849de071dd249a59cfb7f92ba749f1134fa456f1`.
  Initial changes were limited to this proposed plan and the refinement register.
- A pure in-memory reproduction using `uv run python` confirmed an existing correlation defect:
  publish reviewed action 2, exclude action 1 through `build_reviewed_result`, then prepare and
  publish the unchanged remaining action with the original operation history retained.
  The same action changed correlation from `agc-bc401e06e9db6ce44e159e38` to
  `agc-a23e5754336cb3e4e07a06b4`; both operations succeeded, with receipt IDs 7001 and 7002
  and two fake Create calls. No network request or repository application mutation occurred.
- Cause: `_correlation_id` in `publication.py` includes the compacted reviewed action index.
  Excluding an earlier action changes that index without changing the surviving action or evidence.
- This violates the Batch 06 requirement that a succeeded or unknown action stay protected from
  resubmission after reviewed-result changes. The earlier assumption that existing correlation
  protection could be reused unchanged is therefore incomplete.
- Requested review: preserve a stable original analyzed action identity through exclusions for
  correlation and operation-history projection, while keeping the complete reviewed result and
  exact request bound to preview/confirmation fingerprints. Add success and unknown-result
  exclusion regressions before continuing the planned sequence. Keep existing protected operation
  facts safe during migration; do not simply replace correlation hashes and lose their protection.
- Execution is paused under the user's explicit instruction to stop for discovered issues.
  Application implementation, phase tests, full acceptance, and browser acceptance have not begun.
  Prerequisite reading of related application/tests is not yet complete; finish it on resumption.
  No commit or push has been performed. Planned checks in section 8 remain unexecuted.

The user subsequently approved this repair. Prerequisite reading was completed and the
implementation resumed; the pause above is historical evidence.

### Implementation verification after repair approval

- Stable correlation and legacy-alias protection: 21 publication tests passed.
- Capability and preflight: 38 publication/runtime tests passed; strict source/provider/package
  checks, per-action owner/date/parent/priority blockers, unavailable and empty cases covered.
- Route/state foundation: 82 existing AppTest/support checks passed on the initial run; the
  relocated old renderer exposed comparison-widget cleanup. Switched it to independent durable
  delivery selection and verified the fake end-to-end test again. All 49 support tests passed.
- Ruff lint and formatting passed for these changes. No live adapters or fixture edits added.

- Nullable date phase: all 88 AppTest/support tests passed, covering null/change/restore,
  routed persistence, deterministic ISO normalization, and matching change summaries.

- Browser discovery: native date input accepts `None` in Python, but deleting its displayed date
  and blurring restores the previous value and the calendar exposes no clear control. Added an
  explicit native `Clear due date` button with a pre-rerun state callback to fulfill the already
  approved nullable-date requirement; the AppTest now clicks that real control.

- Final application acceptance after the clear-control change: `uv run pytest` passed all 433
  tests (39.17 seconds); `uv run ruff check .`, `uv run ruff format --check .` (42 files),
  `uv build`, and `git diff --check` passed. `uv sync` and a fresh local Streamlit startup
  also passed. No dependency, synthetic-fixture, or provider-boundary changes were needed.

### Real-browser acceptance

- Used headed Chrome through the installed Playwright CLI fallback because the Browser plugin
  was unavailable. Test scripts, browser state, and screenshots stayed under `/tmp`, outside Git.
  Tested a dedicated fresh Streamlit process at `http://localhost:8502`; the existing server on
  port 8501 was left untouched.
- Completed Offline review at 1440 × 1000 and 390 × 844: local outputs complete, both downloads
  retained, delivery explicitly unavailable, and Back navigation usable.
- Completed Internal fake review at both widths: both actions initially ready with reviewed owner,
  resolved assignee, date, priority, and source-controlled parent; unmapped owner and cleared date
  produced named blockers; returning to Human Review retained the null date. Restoring Riley Chen
  and September 18 restored the original record without pending changes.
- At both widths, changed the evidence comparison independently, prepared action 1, inspected both
  request tabs, confirmed the exact request, navigated Back/Return, and created once. Selected and
  separately confirmed action 2. Receipts 7001 and 7002 had distinct correlations and successful
  GET verification; protected actions could not be submitted again. Both receipts and the two
  downloads survived Back/Return navigation.
- Fresh direct delivery navigation without outputs returned to Review Inputs at both widths.
  Keyboard Enter activated the clear-date control; keyboard action selection worked. Narrow
  document width and scroll width were both 390 pixels. Light styling remained readable under
  a dark browser preference; stacked controls, summaries, blockers, and receipts were inspected.
- Representative screenshots inspected: `/tmp/b06-desktop-outputs.png`,
  `/tmp/b06-desktop-receipts.png`, `/tmp/b06-desktop-request-json.png`,
  `/tmp/b06-narrow-request-summary.png`, `/tmp/b06-narrow-blockers.png`,
  `/tmp/b06-narrow-receipts.png`, and `/tmp/b06-narrow-unavailable-final.png`.
- No application exception remained on fresh runs. Console inspection found connection errors
  during the intentional development-server restart and two route-relative Streamlit bootstrap
  404 probes on direct deep links; root bootstrap recovered and the route guard worked. During
  development, stale imported modules required that restart after adding the clear-date helper;
  final acceptance used the restarted process.

## 13. Remaining limitations and deferred work

- Delivery remains an opt-in, in-memory, no-network fake and is not evidence of live Azure DevOps
  connectivity or production authorization.
- Identity, project, type, field, priority, classification, and parent mappings remain static
  synthetic configuration; no administrator surface exists.
- Recovery history is session-local and is not a durable audit record. Process restart cannot prove
  that a real Create did not occur.
- Bulk delivery, automatic retry, Update operations, cross-session reconciliation, and real
  enterprise targets remain deferred.
- R9 remains readiness-gated until live capabilities and release authority are separately approved.

## 14. Final completion record

Batch 06 implementation and verification completed on 2026-09-11. R7 is `Verified`; the
refinement register active-plan pointer is `NONE`. All approved product decisions and the
separately approved stable action-identity repair are implemented. Full repository acceptance and
real-browser desktop/narrow acceptance passed. README, SPEC, DEMO, and the register are synchronized.
No unresolved product decision or blocking finding remains. Publication is still an explicit
human-confirmed, in-memory synthetic operation. This completion record is included in the authorized
Batch 06 commit on `codex/final-stage-i2-review-summary`; the session handoff records its resulting
commit ID and push verification.
