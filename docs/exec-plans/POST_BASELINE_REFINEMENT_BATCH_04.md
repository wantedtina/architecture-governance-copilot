# Post-baseline refinement Batch 04 — deterministic drafting source package

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R1`

Approval boundary: The user accepted R1-R10 as future implementation intent, authorized
sequential planning after each verified batch, and explicitly approved this plan and every product
decision in section 2 on 2026-09-10.

Baseline revision: `33d21b4087e0ba885742b4e3913c73fbd1314025`

Current phase: `COMPLETE`

## 1. Scope

Replace the drafting workflow's inclusion checkboxes with a deterministic, production-shaped source
acquisition and confirmation contract:

1. discover exact resources only from one bundled authorized synthetic inventory;
2. select the governed template, repository revision, and supporting evidence through typed UI
   controls rather than boolean inclusion flags;
3. show structured governance metadata and exact resource provenance;
4. validate and explicitly confirm one immutable `Selected Source Package` manifest; and
5. bind draft generation and stale-result detection to both the canonical drafting payload and the
   exact confirmed manifest/provider configuration.

The batch prepares the UI and contracts for a future approved discovery adapter without adding any
network, authentication, or enterprise capability.

## 2. Proposed product decisions requiring plan approval

Approval of this plan resolves every material open decision currently recorded for R1 as follows.

### Source inventory and selection

- This batch is synthetic UI and contract preparation only. The application reads the existing
  local fixtures and performs no repository scan, clone, upload, URL resolution, authentication,
  or external API call.
- The one bundled project is an authorized synthetic workspace. Opening it loads a deterministic
  inventory whose resources have stable IDs, display names, source types, canonical references,
  versions or revisions, SHA-256 content fingerprints, and local validation status.
- The governed SI template is selected by default and is required. Its canonical reference and
  version remain visible and previewable.
- Repository selection uses controlled organization, project, repository, and revision selectors.
  The current inventory exposes one repository and the exact `main` revision required by the
  deterministic provider. Manual URLs and typed repository identifiers are out of scope; they
  would add validation and authorization behavior without a second legitimate inventory choice.
- The UI contract permits branch, tag, or commit revision kinds, but the bundled inventory claims
  only the available `main` branch. It does not pretend to browse an actual repository.
- Supporting evidence uses a multi-select control over authorized, previewable resources. The
  inventory currently contains one `Supporting context package`, selected by default and required
  by the bundled deterministic drafter. The UI explains that provider compatibility makes it
  required for this scenario instead of describing it as generally optional.
- User-authored notes, file uploads, arbitrary paths, additional evidence types, and externally
  verified evidence are deferred. Bundled evidence is labelled as synthetic local evidence, never
  as independently or externally verified.

### Governance metadata and provider compatibility

- Governance metadata contains two required, source-controlled, read-only fields for this batch:
  project name and governance work-item reference. Their origin and validation state are visible.
- No editable governance taxonomy, person selector, or fabricated owner is introduced. Such fields
  require a real approved schema or additional synthetic scenario before they can be meaningful.
- Synthetic mode and the deterministic drafter identity are derived provider/configuration facts,
  not editable governance fields.
- Resource validation and provider compatibility are separate. A resource may be locally valid yet
  incompatible with the bundled drafter. Confirmation is blocked unless the selected package is
  complete, locally validated, authorized by the inventory, and compatible with the configured
  provider.
- Unsupported selection never invokes a hidden fallback. The UI reports the blocker and keeps the
  package editable.

### Manifest, confirmation, and invalidation

- `Selected Source Package` is a strict, serializable manifest containing project and governance
  identity, selected resource roles and IDs, source references, versions/revisions, fingerprints,
  retrieval/validation status, synthetic/offline disclosure, and provider configuration identity.
- The complete manifest is displayed before confirmation. Confirmation stores an immutable copy
  and its deterministic fingerprint; it is a human confirmation of drafting inputs, not an
  architecture approval or assertion that an external source was contacted.
- Draft generation eligibility requires that the live selection still matches the confirmed
  manifest. The generated-draft fingerprint binds the canonical `SolutionIntentDraftRequest`, the
  confirmed manifest fingerprint, and the provider configuration identity.
- Any project, template, repository revision, supporting-evidence, governance identity, resource
  content/fingerprint, or provider-configuration change invalidates the confirmed source package
  and generated or confirmed draft, then returns the drafting workflow to Project Context.
- Drafting-source changes do not reset the independent governance-review workflow. Existing remote
  operation reconciliation facts, review inputs, reviewed results, and delivery receipts remain
  untouched.
- `Refresh Context` deterministically reloads and revalidates the bundled inventory. If exact
  resource facts are unchanged it retains the current selection and reports that result. If facts
  differ, it clears source-package confirmation and drafting artifacts; it never substitutes
  synthetic content silently.

## 3. Explicit non-goals

- Do not add live Confluence, Azure DevOps, Git, repository-host, identity, or other enterprise
  adapters.
- Do not add credentials, authentication, authorization services, databases, RAG, agents, uploads,
  arbitrary paths, manual URLs, or user-authored evidence.
- Do not generalize the deterministic drafter beyond the bundled scenario or change the
  `SolutionIntentDrafter` provider protocol.
- Do not implement R3 fixture expansion, R7 delivery restructuring, or R9 deployment gating.
- Do not connect a confirmed draft automatically to the independent governance-review workflow.
- Do not represent local fixture validation as external access verification or formal approval.

## 4. Dependencies and overlap boundaries

- Batch 02 is a completed prerequisite: R1 remains solely within `Draft a Solution Intent`, and its
  scoped reset/invalidation must not affect the independent governance review or remote receipts.
- Batch 03 is a completed prerequisite for consistent rendered/source previews of Markdown
  resources; repository excerpts remain verbatim text.
- R3 may later add realistic inventory choices and evidence collections, but it must reuse rather
  than weaken this manifest and provenance contract.
- R7 may consume governed review actions but has no dependency on this drafting manifest.
- The current deterministic drafter requires the exact bundled template, repository context, and
  supporting context. This batch exposes that compatibility constraint rather than changing the
  provider or adding fallback behavior.

No unresolved blocker remains if the user approves every decision in section 2. Any requested
change to those decisions must be incorporated before implementation begins.

## 5. Affected components and files

- `src/architecture_governance_copilot/models.py` — strict resource, revision, validation, and
  selected-source-package manifest models.
- `src/architecture_governance_copilot/ui_support.py` — deterministic inventory loading, selection
  projection, manifest validation/fingerprinting, confirmation, refresh, and scoped invalidation.
- `app.py` — authorized selectors, provenance/status presentation, previews, manifest review, and
  explicit confirmation UX.
- `src/architecture_governance_copilot/si_drafting.py` — expected to retain its provider boundary;
  only explicit provider identity/compatibility metadata may be exposed if tests show it cannot be
  derived safely at the UI-support boundary.
- `tests/test_models.py`, `tests/test_ui_support.py`, `tests/test_app.py`, and
  `tests/test_si_drafting.py` — strict contract, state, UI, and provider-boundary coverage.
- `README.md`, `SPEC.md`, and `DEMO.md` — maintained product truth and demonstration procedure.

The existing fixtures under `samples/` remain the deterministic content contract. No fixture
content update is planned; exact fingerprints will be computed from the current files.

## 6. Implementation sequence

- [x] Confirm Batch 03 is verified, committed, pushed, and no plan remains active.
- [x] Reconcile R1 open decisions with current application code, tests, fixtures, and maintained
  documentation.
- [x] Obtain explicit user approval of this execution plan and all section 2 decisions.
- [x] Mark this plan `IN_PROGRESS`, move R1 to `In progress`, and record approval.
- [x] Add strict resource and source-package manifest models with deterministic serialization.
- [x] Replace the legacy boolean source flags with an authorized synthetic inventory and controlled
  selection state.
- [x] Implement local validation, provider compatibility, manifest construction/fingerprinting,
  refresh, confirmation, and scoped invalidation.
- [x] Build the Project Context selector, provenance, preview, blocker, and confirmation surfaces.
- [x] Bind draft eligibility and stale-result detection to the confirmed manifest without changing
  the provider protocol or adding fallback behavior.
- [x] Synchronize maintained documentation and demo instructions.
- [x] Run focused and full automated verification plus the browser acceptance matrix.
- [x] Fix every in-scope failure before marking the batch verified.
- [x] On success, mark this plan `COMPLETED_VERIFIED`, set R1 to `Verified`, clear the active
  pointer, commit, and push under the user's standing sequential-batch instruction.

## 7. Acceptance criteria

- Project Context exposes only authorized bundled resources through controlled selectors and an
  evidence multi-select; it accepts no arbitrary repository identifier, URL, path, or upload.
- Template, repository revision, evidence, governance metadata, and provider configuration show
  exact identity, source type, version/revision, fingerprint or derived identity, and truthful
  validation/compatibility status.
- The existing SI template, repository excerpt, and supporting evidence remain fully previewable
  using their purpose-appropriate rendered or exact-source views.
- The required deterministic provider package is selected by default. Removing a required resource
  gives a specific blocker and cannot generate a draft.
- One complete manifest is reviewable before an explicit human confirmation; confirmation creates
  no approval claim and no external side effect.
- Drafting cannot proceed from an unconfirmed, changed, invalid, unauthorized, or provider-
  incompatible manifest.
- Draft fingerprints include canonical request content, manifest identity, and provider identity;
  stale or changed inputs cannot reuse an old draft.
- Refresh distinguishes unchanged local facts from changed facts and invalidates only the drafting
  workflow when necessary.
- Draft reset clears the inventory selection, manifest confirmation, and draft while leaving the
  governance-review workflow and any remote-operation reconciliation facts intact.
- The deterministic offline path, human review boundary, evidence traceability, strict validation,
  light-only presentation, and existing provider protocols remain intact.

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

- strict manifest validation, stable ordering/serialization/fingerprints, duplicate or unknown
  resource rejection, blank identities, revision kinds, and tampered content fingerprints;
- inventory loading with present, missing, unreadable, empty, and changed fixture content;
- default selections, removal/reselection, exact provider compatibility blockers, and no silent
  fallback or provider invocation while blocked;
- manifest confirmation, immutable copies, input/provider binding, stale draft detection, refresh
  with unchanged/changed facts, and drafting-only reset/invalidation;
- selector options, evidence multi-select, governance read-only facts, provenance/status labels,
  previews, manifest display, disclosures, blockers, and confirmation routing;
- existing deterministic draft content and edited-draft confirmation behavior;
- independent Offline and Internal fake governance-review regressions, including preserved review
  state and publication receipts after drafting reset or source change.

Browser verification at desktop and narrow viewports must complete:

1. open the synthetic workspace and inspect the default template, repository revision, supporting
   evidence, governance metadata, offline disclosure, and exact manifest;
2. remove each required selection in turn, observe a specific blocker and disabled confirmation,
   then restore it and confirm the exact source package;
3. generate, edit, and confirm a deterministic SI draft; return to Project Context and verify that
   a material source selection change invalidates the drafting package/draft only;
4. refresh unchanged bundled facts and verify the truthful retained-selection status;
5. complete or retain Offline and Internal fake review state across drafting reset/invalidation and
   confirm no unintended external request occurs;
6. verify keyboard-accessible controls, readable provenance/manifest content, light-only styling,
   and usable stacking without horizontal overflow at a narrow viewport.

## 9. Compatibility, state, and rollback

- The drafting session schema will replace four legacy boolean selection keys with inventory,
  selection, live-manifest, confirmed-manifest, and manifest-fingerprint state. Initialization and
  scoped reset must remove obsolete keys so stale browser sessions cannot bypass confirmation.
- Existing fixture text and `SolutionIntentDraftRequest` remain canonical provider inputs. Manifest
  metadata is an upstream eligibility/audit contract and does not masquerade as semantic drafting
  content.
- Review workflow state and remote reconciliation state are outside the rollback boundary.
- If verification fails, retain R1 as `In progress`, keep this plan active, and record the exact
  failure. Do not restore no-op controls, weaken validation, or permit an implicit synthetic
  fallback.

## 10. Progress

- [x] Accepted requirement and current implementation reconciled.
- [x] Proposed product decisions consolidated.
- [x] Sole active-plan pointer assigned for review.
- [x] User approval recorded.
- [x] Implementation complete.
- [x] Automated verification passed.
- [x] Browser verification passed.
- [x] Maintained documentation synchronized.
- [x] Completion record finalized and active pointer cleared.

## 11. Decisions and important discoveries

- Batch 03 completed at `33d21b4087e0ba885742b4e3913c73fbd1314025`; the working tree was clean
  and local HEAD matched the remote branch when Batch 04 planning began.
- The current Project Context presents four inclusion checkboxes. Template and repository gate
  confirmation, supporting evidence changes the request, and governance metadata has no downstream
  effect.
- Although the UI labels supporting evidence optional, the deterministic provider accepts only the
  exact complete bundled supporting context. Omitting it permits confirmation but causes generation
  to fail. The new manifest must make this compatibility requirement explicit.
- Current draft staleness hashes only `SolutionIntentDraftRequest`; source identity, manifest
  confirmation, and provider configuration are not bound to the generated result.
- Existing fixtures already contain the one legitimate deterministic scenario. Inventing extra
  repository branches, evidence documents, governance owners, or external validation would create
  misleading capabilities rather than useful product coverage.
- The user explicitly approved this plan and every section 2 decision on 2026-09-10.
- Streamlit removes widget-owned state when a routed page is absent. Durable source-selection keys
  are therefore separate from widget keys and restore the selectors when the user returns to
  Project Context.
- A source change initially revoked confirmation one rerun after the controls changed. Immediate
  rerun after invalidation now keeps the sidebar, blocker, and control state synchronized.
- Starting a workflow after a session-schema migration initially retained the stale route error.
  Workflow start now clears that error explicitly.

## 12. Actual verification evidence

- `uv sync` completed successfully.
- Focused application and UI-support verification passed: 83 tests.
- Full automated verification passed: 392 tests in 24.49 seconds.
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed with 40 files already formatted.
- `uv build` produced the source distribution and wheel successfully.
- `git diff --check` passed.
- Desktop browser verification completed the deterministic drafting flow: inspected exact source
  identities and manifest provenance, removed and restored required evidence, confirmed the
  package, generated and edited a draft, confirmed the edited draft, refreshed unchanged facts,
  and observed immediate drafting-only invalidation after a source change.
- Routed browser verification confirmed template, repository, and evidence selections persist when
  leaving and returning to Project Context.
- Offline review state remained confirmed and analyzable across drafting reset, with no drafting
  note or state leakage.
- Internal fake browser verification completed controlled input acquisition, fake AIF analysis,
  mandatory human confirmation, exact publication preview confirmation, one fake Azure DevOps
  submission, and the deterministic `7001` read-back receipt with explicit no-network disclosure.
- Narrow browser verification at 390 by 844 pixels showed accessible source controls, blocker, and
  confirmation action with no horizontal overflow (`scrollWidth` equaled `innerWidth`).

## 13. Remaining limitations and deferred work

- The authorized inventory contains one synthetic project, one template, one repository revision,
  and one supporting evidence resource. The controls demonstrate the contract, not general
  discovery.
- No live access, external authorization, manual identifier resolution, upload, or user-authored
  evidence is available.
- No alternate deterministic provider package is supported. Broader input support requires a
  separately approved provider and fixtures.
- Editable governance taxonomies and people fields remain deferred until an approved schema and
  meaningful source exist.

## 14. Final completion record

Completed and verified on 2026-09-11. R1 is verified, the active-plan pointer is cleared, and the
remaining limitations in section 13 remain outside this batch. Commit and push follow this
completion record under the user's standing sequential-batch authorization.
