# Post-baseline refinement Batch 02 — independent workflows and review-input manifest

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R2`, `R5`, `R8`

Approval boundary: The user accepted R1-R10 as future implementation intent, authorized continued
sequential planning after Batch 01, and explicitly approved this Batch 02 plan on 2026-09-10. Only
R2, R5, R8, and the scope in this plan are authorized for implementation.

Baseline revision: `e3a957ef032436b356a61e4943e9dc2469db9cf5`

Current phase: `COMPLETE`

## 1. Scope

Replace the current global five-stage pipeline with two peer workflows:

1. `Draft a Solution Intent`: `Project Context` -> `Draft Solution Intent`.
2. `Review a Solution Intent`: `Review Inputs` -> `Human Review` -> `Generated Outputs`.

The drafting workflow ends with a human-confirmed Markdown draft and provenance summary for manual
transfer. It does not send that draft to governance review or imply Confluence publication. The
review workflow begins independently and analyzes only one explicitly confirmed review-input
manifest containing an authoritative, read-only synthetic SI snapshot, an explicit transcript
snapshot, validated review metadata, and the selected provider configuration.

Review-input components may be acquired in any order. Each component has visible local readiness
and provenance, and analysis remains disabled until the exact complete package is explicitly
confirmed. The deterministic Offline and opt-in Internal fake paths retain the same source roles,
validation rules, provider boundaries, and no-network disclosures.

## 2. Proposed product decisions requiring plan approval

Approval of this plan resolves the material open decisions in R2, R5, and R8 as follows.

### Workflow structure and navigation

- The root page becomes a task-oriented landing page with two peer actions named exactly
  `Draft a Solution Intent` and `Review a Solution Intent`.
- Each workflow has its own progress display and local numbering. Drafting uses two steps; review
  uses three steps. Neither workflow displays the other as `Skipped`, `Complete`, or required.
- Confirming a draft keeps the user in the drafting workflow and reveals download plus provenance
  controls. A `Start a separate review` action opens an empty Review Inputs workflow and transfers
  no SI body, source identity, confirmation, or downstream state.
- `Start New Review` resets only review-workflow inputs and results. Each workflow also exposes a
  clearly named workflow-scoped reset. A separate landing-page `Reset all local demo state` action
  remains available for a full reset.
- Existing pre-Batch-02 browser sessions have no durable migration requirement. A state-schema
  version mismatch safely clears obsolete monolithic navigation/input state and returns to the
  landing page while preserving remote-operation reconciliation facts.

### Synthetic scenarios and drafting completion

- The Offline drafting and review demonstrations continue to use the fictional Digital Payment
  Notification Service at different lifecycle moments. The review workflow loads its own named,
  versioned authoritative synthetic snapshot; it never consumes the local drafting result.
- Internal fake continues to use the distinct Synthetic Order Routing Service scenario. Expanding
  that fixture remains R3 and is outside this batch.
- Draft completion provides the human-confirmed Markdown file, project identity, confirmed source
  package fingerprint, drafter/provider identity, and a clear `Not published to Confluence`
  disclosure. Clipboard-specific functionality is not added; the editable draft remains selectable
  and the download is the supported transfer artifact.
- R1 source discovery remains deferred. The current deterministic Project Context package is
  retained inside the drafting workflow and is not presented as production-shaped discovery.

### Authoritative SI and transcript intake

- This batch uses authorized synthetic SI selectors only. It does not accept typed Confluence page
  IDs or URLs and does not add live discovery. Offline and Internal fake selectors expose exact
  source identity, synthetic space, page ID, URL, version, retrieval time, canonicalizer version,
  content fingerprint, validation state, and refresh behavior.
- The SI body is read-only in Review Inputs. Changing or refreshing the selected source invalidates
  manifest confirmation and downstream review state without clearing independent valid transcript
  or metadata input.
- Transcript intake is paste-only for this batch; file upload and Teams retrieval remain out of
  scope. The deterministic demo may load a clearly labelled bundled synthetic transcript into the
  same editable field.
- Transcript content is retained only in the Streamlit session. The initial loaded/pasted
  fingerprint and current fingerprint are kept so the UI can disclose `Edited after load`; no raw
  duplicate, edit reason, database, or durable audit log is added.
- Transcript edits require reconfirmation of the review-input manifest but no separate reason.
  Recommended `[timestamp] Speaker: text` formatting is shown; missing speakers or timestamps are
  preserved truthfully and never synthesized.

### Metadata, readiness, confirmation, and invalidation

- Review metadata is a separately visible component rather than being implicitly bundled with
  transcript intake. Synthetic convenience actions may load transcript and metadata together, but
  the readiness manifest reports and validates them independently.
- SI title, version, prior status, and source identity come from the selected SI snapshot and are
  read-only. Review round, review date, Domain Architect, and governance ticket remain explicit
  editable review metadata with `Synthetic sample` or `User entered/edited` provenance.
- Successful component loading does not force a tab change. A compact readiness manifest and
  localized success message identify what changed and what remains missing.
- Component states are `Missing`, `Loaded`, `Edited`, `Invalid`, and `Confirmed` where applicable.
  Analyze remains disabled until all three components are valid and the exact manifest is confirmed;
  unmet requirements appear next to the disabled action as normal readiness guidance.
- The confirmed manifest fingerprint includes SI source identity/version/canonicalizer/content,
  transcript content and provenance, review metadata, review mode, and provider identity.
- Editing any confirmed component revokes manifest confirmation and invalidates analysis,
  human-confirmed outputs, request previews, and unsubmitted publication state. Existing
  remote-operation reconciliation facts remain preserved.
- Changing review mode clears provider-owned SI state and any bundled component owned by that mode,
  while preserving genuinely user-pasted transcript and user-entered metadata. It always revokes
  manifest confirmation and downstream state. Partial packages remain session-only and cannot be
  exported or resumed in this batch.

## 3. Explicit non-goals

- Do not implement R1 source discovery, R3 fixture expansion, R4 pending-edit comparison, R6 broad
  Markdown redesign, R7 delivery-step restructuring, or R9 deployment gating.
- Do not add Confluence write-back, transcript file upload, Teams retrieval, live enterprise
  connections, AIF/LLM calls, databases, authentication, RAG, or an agent framework.
- Do not add typed or arbitrary external page/repository identifiers.
- Do not redesign the brand system or alter the verified light-only theme beyond regression fixes.
- Do not change evidence validation, provider trust boundaries, or formal-approval disclaimers.

## 4. Dependencies and overlap boundaries

- R2, R5, and R8 are one batch because workflow separation, authoritative source identity,
  order-independent acquisition, confirmation, routing, and invalidation share one state contract.
- R1 is not a prerequisite for the navigation split: this batch keeps the existing deterministic
  drafting package and explicitly defers production-shaped drafting discovery.
- R3 depends on the review-input contract created here; its richer fake fixture must not be mixed
  into this batch.
- R4 and R6 should target the post-Batch-02 Human Review and document surfaces.
- R7 depends on the confirmed review workflow and remains unchanged here.
- R9 cannot become ready without separately approved live capabilities.

No unresolved blocker remains if the user approves every decision in section 2. Any requested
change to those decisions must be incorporated before implementation begins.

## 5. Affected components and files

- `app.py` — landing page, independent workflow shells, local progress, input controls, readiness,
  confirmation, completion, and reset presentation.
- `pages/*.py` — retain thin route entry points; add or rename a thin route only if required for the
  landing contract without duplicating renderers.
- `src/architecture_governance_copilot/ui_support.py` — workflow identity, state-schema version,
  component provenance/readiness, confirmed manifest fingerprint, scoped reset, route guards, and
  invalidation behavior.
- `src/architecture_governance_copilot/models.py` — strict manifest/source/provenance models only if
  they represent reusable application contracts rather than UI-only display state.
- Existing deterministic providers and integration adapters — consume the confirmed manifest
  through their current boundaries; no provider-specific behavior may leak into shared workflow
  logic.
- `tests/test_ui_support.py`, `tests/test_app.py`, and focused model/provider tests as needed.
- `README.md`, `SPEC.md`, `DEMO.md`, and maintained integration documentation whose current stage
  names or handoff assumptions become inaccurate.
- Existing `samples/` only if a source-identity sidecar is required; any fixture change must update
  validation tests in the same batch.

## 6. Implementation sequence

- [x] Confirm Batch 01 is verified, committed, pushed, and no plan remains active.
- [x] Reconcile R2, R5, and R8 dependencies, overlap, and open decisions against current code/tests.
- [x] Obtain explicit user approval of this execution plan and all section 2 decisions.
- [x] Mark this plan `IN_PROGRESS`, move R2/R5/R8 to `In progress`, and record approval.
- [x] Introduce the independent workflow and state-schema contract with focused state tests first.
- [x] Add authoritative synthetic SI snapshot and component provenance/readiness models.
- [x] Implement order-independent review acquisition, explicit manifest confirmation, Analyze
  gating, localized feedback, and dependency-aware invalidation.
- [x] Update the routed Streamlit shell, landing page, independent progress displays, drafting
  completion, scoped reset controls, and review workflow.
- [x] Update maintained documentation and demo instructions to match implemented behavior.
- [x] Run focused and full automated verification plus the complete browser acceptance matrix.
- [x] Fix every in-scope failure before marking the batch verified.
- [x] On success, mark the plan `COMPLETED_VERIFIED`, set R2/R5/R8 to `Verified`, clear the active
  pointer, then commit and push only under the user's standing instruction for sequential batches.

## 7. Acceptance criteria

- The landing page exposes two peer workflows with independent progress and reset semantics.
- Draft confirmation never becomes or populates an authoritative governance-review SI.
- Drafting ends with a human-confirmed downloadable Markdown artifact and traceable provenance.
- Review Inputs uses one read-only, versioned, validated synthetic SI source in both Offline and
  Internal fake modes.
- SI, transcript, and metadata can be loaded or edited in either order without false affordances or
  loss of unrelated valid input.
- Each component and the overall package have visible, localized readiness and provenance.
- Analyze is impossible before explicit confirmation of the exact complete manifest.
- Any relevant edit, refresh, provider change, or mode change revokes confirmation and all affected
  downstream state without losing preserved remote reconciliation facts.
- Human Review, evidence traceability, reviewed-output generation, and guarded fake publication
  continue to operate only after the mandatory confirmation boundaries.
- Offline remains deterministic and zero-configuration; Internal fake remains opt-in and
  no-network; no silent synthetic fallback is added.
- The deliberate light-only theme remains coherent on every changed screen.

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

- both workflow entries, route guards, local numbering, and workflow-scoped/full reset;
- draft confirmation/export without review-state transfer;
- SI-first, transcript-first, and metadata-first acquisition;
- partial, invalid, edited, confirmed, and stale manifest states;
- localized success/failure feedback and tab-independent readiness;
- explicit confirmation and Analyze gating;
- SI refresh, transcript edit, metadata edit, provider/mode change, and state-schema migration;
- preservation of remote-operation reconciliation facts;
- Offline and Internal fake evidence binding through the existing providers.

Browser verification at a desktop viewport must complete:

1. landing -> drafting -> human-confirmed draft download/provenance -> separate empty review entry;
2. Offline review with transcript-first and SI-first order, manifest confirmation, analysis, Human
   Review, and Generated Outputs;
3. Internal fake review through exact Create preview, separate confirmation, single fake submit, and
   verified read-back;
4. partial/invalid input, edit-after-load disclosure, stale-confirmation revocation, disabled
   Analyze guidance, route recovery, scoped resets, and the verified light-theme regression.

## 9. Compatibility, migration, and rollback

- Introduce an explicit session-state schema version. Obsolete monolithic session state is reset to
  the landing page on first rerun; no persistent user data exists to migrate.
- Keep remote-operation reconciliation keys outside destructive workflow resets and preserve the
  current uncertainty/retry safeguards.
- Do not rename provider protocols or weaken strict Pydantic/evidence validation.
- If verification fails, keep R2/R5/R8 `In progress`, retain this plan as active, and record the
  exact failing state. Do not partially restore the old five-stage semantics or silently bypass the
  manifest confirmation.

## 10. Progress

- [x] Accepted requirements and current implementation reconciled.
- [x] Proposed product decisions consolidated.
- [x] Sole active-plan pointer assigned for review.
- [x] User approved Batch 02 on 2026-09-10.
- [x] Implementation complete.
- [x] Automated verification passed.
- [x] Browser verification passed.
- [x] Maintained documentation synchronized.
- [x] Completion record finalized and active pointer cleared.

## 11. Decisions and important discoveries

- Batch 01 completed at `e3a957ef032436b356a61e4943e9dc2469db9cf5`; the working tree was clean
  when Batch 02 planning began.
- The current route and sidebar progress model derive from one global `ACTIVE_STAGE_KEY`, and review
  mode affects how earlier drafting stages are labelled. Workflow identity must therefore precede
  route eligibility rather than being inferred from stage or provider mode.
- Current Review Inputs combines SI, transcript, and metadata readiness into one condition and
  allows a transcript action that can fail below the viewport when SI is empty. Component-level
  state and confirmation belong in shared state support, not ad hoc renderer branches.
- The current fake Confluence snapshot already contains the source identity needed to shape the
  authoritative SI contract. Offline requires an equivalent synthetic descriptor, not a new live
  adapter.
- The current drafting confirmation automatically initializes Review Inputs. That handoff must be
  removed rather than relabelled.
- The user explicitly approved this plan and every section 2 decision on 2026-09-10.
- Streamlit forbids rewriting a widget-owned session key after that widget is instantiated. Draft
  confirmation and transcript editing therefore update durable business state without redundantly
  assigning the live widget key during the same rerun.
- The confirmed manifest includes the source retrieval timestamp as well as the required source,
  content, provenance, mode, metadata, and provider facts. Refreshing a source always requires a
  fresh human confirmation, even when its canonical content is unchanged.

## 12. Actual verification evidence

Completed on 2026-09-10 from the repository root:

- `uv sync` — passed; 54 packages resolved and 51 packages checked.
- `uv run pytest` — passed; 376 tests.
- `uv run ruff check .` — passed.
- `uv run ruff format --check .` — passed; 39 files already formatted.
- `uv build` — passed; source distribution and wheel built.
- `git diff --check` — passed.
- Streamlit `AppTest` and pure-state coverage passed for peer workflow entry, route guards, local
  numbering, scoped/full reset, state-schema migration, three acquisition orders, readiness,
  explicit confirmation, edit invalidation, drafting isolation, and both provider modes.
- Chrome desktop acceptance passed for landing and light-theme presentation; complete drafting to
  confirmed Markdown/provenance; a separate empty review; transcript-first and SI-first Offline
  acquisition; confirmation gating; edit-after-load revocation; Human Review and Generated
  Outputs; deep-link recovery; review-scoped reset; and Internal fake exact Create preview,
  separate confirmation, one fake submission, and verified GET read-back.

## 13. Remaining limitations and deferred work

- Drafting source discovery remains R1.
- The realistic Internal fake scenario remains R3.
- Pending human-edit comparison and broader Markdown presentation remain R4/R6.
- Governed delivery restructuring remains R7.
- Deployment-controlled synthetic-mode visibility remains R9 and live-capability gated.
- Transcript upload, durable resume, Confluence write-back, and live enterprise adapters remain out
  of scope.

## 14. Final completion record

Batch 02 completed and passed every acceptance criterion on 2026-09-10. R2, R5, and R8 are
`Verified`; the refinement register active-plan pointer and execution authority are `NONE`. The
implementation remains deterministic Offline by default, retains mandatory human confirmation and
evidence validation, keeps Internal fake opt-in and no-network, and adds no live enterprise
connector or credential path.
