# Post-baseline refinement register

Updated: 2026-09-10

Document status: `ACTIVE_CHANGE_REGISTER`

Execution authority: `NONE` while items remain `Collected`.

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

- **State:** `Collected`
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

## 6. Register maintenance and execution handoff

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
6. After explicit batch approval, create the smallest coherent execution plan using
   `docs/exec-plans/README.md`, set the active-plan pointer at the top of this register, and move the
   included items to `In progress` only when implementation actually starts.
7. Keep component details, implementation steps, detailed tests, progress, discoveries, and
   verification evidence in that execution plan rather than this register.
8. On successful completion, mark the plan `COMPLETED_VERIFIED`, update the included items to
   `Verified`, clear the pointer, and retain the completed plan as historical evidence.
9. Stop a batch if a product decision is unresolved or verification fails. Record the exact state
   in the execution plan; do not infer completion from a clean test run or the end of a session.

No code, fixture, dependency, environment, or live-integration change is part of the current
requirements-intake update.
