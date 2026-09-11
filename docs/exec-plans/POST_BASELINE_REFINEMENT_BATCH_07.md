# Post-baseline refinement Batch 07 — deployment-policy foundation

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R9a` (foundation phase of R9 only)

Approval boundary: The user approved splitting R9 into policy foundation now and live production
acceptance later. The user subsequently approved all section 2 decisions, implementation, full verification,
and commit/push on completion.

Baseline revision: `7baa0d9fb71aa71ef2c7e8584994c54a3a9ddbdb`

Current phase: `COMPLETE`

## 1. Scope and non-goals

Centralize deployment-level synthetic capability policy, validate configuration, enforce it before
workflow rendering and operations, and invalidate incompatible session state. Preserve the default
deterministic offline demonstration and mandatory human confirmation with evidence traceability.

Do not add live Confluence, AIF, Teams, Azure DevOps, authentication, roles, an administrative UI,
a database, RAG, agent frameworks, OpenSpec, Spec Kit, credentials, or confidential data. Do not
activate or certify production capabilities. Do not change fixture content or provider semantics.

## 2. Approved product decisions

### Profiles and explicit configuration

- Add `AGC_DEPLOYMENT_PROFILE` with `demo`, `development`, `test`, and `production` values.
  Resolve an immutable validated policy at application entry from process environment. Operators
  change configuration by restarting the process; add no in-app policy editor or remote refresh.
- With neither profile nor fake opt-in configured, default to `demo`: Offline review and synthetic
  drafting remain available without credentials or network. Training uses a separate demo deployment.
- `development` and `test` permit Offline and allow Internal fake only with the existing explicit
  `AGC_INTERNAL_FAKE_ENABLED` opt-in. Neither profile enables fake implicitly.
- Preserve existing launch commands: an absent profile plus a true legacy fake flag resolves to
  development, with a visible development/synthetic environment label. Explicit `demo` or
  `production` plus a true fake flag is a configuration error, not a silently ignored flag.
- Parse booleans strictly: accept 1/true/yes/on and 0/false/no/off case-insensitively; absent means
  false. Reject blank or unrecognized explicit profile/boolean values. Preserve the existing fake
  provider identity setting and default; reject an explicitly blank identity when fake is enabled.
- `production` permits no currently implemented provider. It renders an unavailable environment
  status and operator correction guidance; it exposes no synthetic selector, source loading,
  analysis, draft generation, confirmation, export, or fake delivery controls. There is no live mode
  placeholder that can be mistaken for an executable capability.
- Invalid configuration stops application workflows with a concise configuration error. Valid
  production without accepted live capabilities is an unavailable state, not a parser error.
  Never print environment dumps or credential values in diagnostics.

### Workflow and capability enforcement

- Retain the two peer workflows and the independent fourth delivery step in allowed environments.
  Show the resolved environment and continuous synthetic/no-network labels where applicable.
- Hide a mode selector when exactly one review mode is allowed; show its truthful capability status.
  Development/test with both modes retains explicit selection. Switching remains a human action.
- Enforce policy at shared application entry before route rendering or redirects, and at runtime
  construction and delivery capability resolution. Direct page URLs and stored widget values must
  not bypass it. Gate synthetic drafting as well as review so production cannot enter via drafting.
- When an existing selected mode becomes disallowed, revoke its bound workflow state and require an
  explicit allowed-mode selection or restart action. Do not silently replace it with Offline.
  A fresh demo session may initialize its configured default; this is not failure fallback.
- Do not add exception handlers that substitute synthetic results after provider failures. Test
  fail-closed behavior and absence of alternative provider calls rather than inventing live output.

### State and history

- Store a deterministic policy identity alongside session state. Compare it before using state on
  every rerun, including direct routes; tolerate a restart restoring no prior session at all.
- Invalidate incompatible source packages, manifests, analyses, human confirmations, outputs,
  delivery selections, previews, and confirmations. Preserve compatible independent workflow state
  when only the other workflow's eligibility changes. A transition to production invalidates both
  currently synthetic workflows and prevents stale output download or submission.
- Retain existing correlation-indexed operation facts and known IDs across invalidation/migration.
  They are session-local reconciliation facts, not reusable delivery permission or a durable audit.
  Under a blocked production policy, do not expose synthetic operation controls to ordinary users.
- Bind provider identity changes through existing manifest and preview invalidation. Avoid resetting
  compatible work on every rerun or merely because an irrelevant environment variable changed.
- Add a session-schema migration only if the final state representation requires it; migration must
  not erase protected publication history or convert stale mode state into an implicit fallback.

## 3. Dependencies and blockers

R2 workflow separation, R5 source manifests, and R7 capability/operation history are verified.
Real live integration is not a dependency for this foundation. Section 2 was explicitly approved before implementation. Any newly discovered material product decision requires user review.

R9b remains deferred: accepted live adapters, target/identity authorization, end-to-end failure and
reconciliation acceptance, and explicit release authority must exist before production activation.
No authentication or release switch is fabricated in this batch.

## 4. Affected components

- `runtime_dependencies.py`: policy resolution and provider/capability eligibility; a small dedicated
  policy module is acceptable if it improves separation without introducing a framework.
- `ui_support.py`: policy identity, scoped invalidation, migration, and explicit recovery state.
- `app.py`: shared entry guard, environment status, selector visibility, and correction actions.
- `pages/`: retain thin route entry points; verify every route passes the common guard.
- `tests/test_runtime_dependencies.py`, `tests/test_ui_support.py`, `tests/test_app.py`: focused
  contracts and rendered routes; add a dedicated policy test file if a module is introduced.
- `README.md`, `SPEC.md`, `DEMO.md`: configuration matrix, compatibility, unavailable production,
  and clear distinction between foundation verification and live release acceptance.
- This plan and the refinement register: actual progress and R9a/R9b lifecycle only.

## 5. Ordered implementation and stage gates

1. Complete prerequisite reading of maintained product docs, related application modules, all
   relevant tests, and the Streamlit skill. Record user approval and baseline Git synchronization.
2. Implement pure validated policy and runtime/capability gates. Pass focused configuration/runtime
   tests before beginning state integration.
3. Implement policy identity and scoped invalidation, retaining operation facts. Pass focused
   support tests before UI changes.
4. Add shared route enforcement, labels, selector behavior, and explicit recovery. Pass AppTests
   for all profiles and direct routes before documentation and browser acceptance.
5. Synchronize maintained documentation, run full repository acceptance, then real-browser desktop
   and narrow acceptance. Fix and retest any failed stage before continuing.
6. Mark R9a Verified and this plan COMPLETED_VERIFIED only after acceptance; retain parent R9
   Accepted and R9b Deferred, clear active pointer, and commit/push the current branch after user
   approval includes that completion action. Never force-push or rewrite history.

## 6. Acceptance criteria

- Default launch preserves offline drafting/review and existing human-confirmed artifacts.
- Legacy explicit fake opt-in remains usable through the documented development resolution.
- Explicit policies enforce their full matrix without hidden fallback or route/session bypass.
- Invalid configuration and valid-but-unavailable production are clearly distinct and safe.
- Disallowed providers are not constructed or called; no fake delivery gateway is invoked by a
  production route or stale confirmation. Both workflow entry paths are covered.
- Compatible state survives reruns; incompatible work loses eligibility before render or submit;
  known operation facts remain protected through migration and reset.
- No real connector, secret, fixture, dependency-list, or production-readiness claim is introduced.

## 7. Automated and browser verification

Focused tests cover the full profile/flag matrix, unknown/blank values, provider identities, legacy
compatibility, runtime denial, no implicit fallback, stale widgets, all direct routes, policy
transitions, independent workflow preservation, source/output invalidation, protected success and
unknown histories, and unchanged human-review/traceability behavior.

From the repository root run:

```bash
uv sync
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Use isolated local server processes for profile changes. Do not interfere with existing user
servers. At desktop (1440 × 1000) and narrow (390 × 844), verify default demo end to end, explicit
fake review and guarded delivery, truthful single/multiple-mode presentation, production-unavailable
and invalid-configuration screens, direct review/drafting/delivery routes, and explicit recovery
from a disallowed mode where session continuity is testable. Exercise keyboard controls and light
styling under light/dark host preferences. Use AppTest to inject stale session states that a process
restart does not preserve; distinguish those tests from actual browser evidence. Inspect screenshots,
console errors, overflow, and application exceptions. Keep browser artifacts outside Git.

## 8. Compatibility and rollback

Preserve zero-configuration demo and the existing fake opt-in launch command. Invalid explicit
configuration now fails closed instead of treating an unrecognized boolean as disabled. Document
this intentional validation change. Keep provider-specific behavior behind existing boundaries.

Rollback policy/configuration, route guards, and policy-state additions as one coherent change;
retain publication reconciliation facts. Do not roll back via history rewriting or fixture deletion.

## 9. Progress

- [x] User-approved two-phase scope recorded.
- [x] Initial runtime, route, and state behavior inspected.
- [x] Proposed decisions and acceptance contract prepared.
- [x] Execution plan approved.
- [x] Prerequisite reading completed and baseline rechecked.
- [x] Policy/runtime tests passed.
- [x] State lifecycle tests passed.
- [x] UI and direct-route tests passed.
- [x] Maintained documentation synchronized.
- [x] Full repository acceptance passed.
- [x] Desktop/narrow browser acceptance passed.
- [x] Completion lifecycle updated; authorized Git handoff recorded below.

## 10. Discoveries and decisions

Current runtime always includes Offline; fake visibility is driven by a permissive environment
boolean parser. Review Inputs replaces an unavailable mode with Offline. That UI-local fallback
cannot serve as deployment enforcement. Shared entry must protect every route before workflow code.
Drafting is synthetic too, so production denial must cover both workflows without redefining their
independent business meaning. Existing source/provider fingerprints and retained publication history
provide the basis for scoped invalidation.

## 11. Actual verification evidence

Planning inspection: read AGENTS.md and execution-plan conventions, inspected runtime dependency
wiring, relevant mode/state helpers, route guards and test coverage locations. Branch is
`codex/final-stage-i2-review-summary`, HEAD is the baseline above, and the initial working tree was
clean. Application changes and test runs have not started. Planning checks are not implementation
acceptance; record subsequent commands and results here as execution proceeds.

Implementation evidence: 31 runtime tests passed, followed by 90 combined runtime/support tests.
State tests cover compatible policies, removed fake mode, production denial, provider identity
changes, success/unknown history retention, and migration without fallback. Initial focused test
failures identified a test field-name error and incomplete provider-change clearing; both were
corrected before beginning UI integration.

UI verification: the 42 existing AppTests passed initially. New direct-page tests showed that
AppTest can run thin page files without main(), so the same policy guard now runs first in all
seven stage renderers. All 19 focused profile/route/recovery tests passed after this correction.

Final verification on 2026-09-11:

- Baseline branch and fetched origin both matched `7baa0d9fb71aa71ef2c7e8584994c54a3a9ddbdb`;
  initial uncommitted changes were limited to this plan and the register. Maintained product
  documentation, related runtime/state/route code and tests, Streamlit skill and state/routing
  references were reviewed. No dependency or fixture change was required.
- `uv sync` passed. The first full run passed 485 tests. After adding explicit policy identity
  comparison and a compatible-state regression, final `uv run pytest` passed **486 tests in
  48.73 seconds**. `uv run ruff check .`, `uv run ruff format --check .` (42 files), `uv build`
  (source distribution and wheel), and `git diff --check` all passed.
- State policy identity is additive; no schema bump was needed. Existing migration is tested with
  pre-migration selected-mode inspection, so it cannot silently convert a disallowed fake mode to
  Offline. Explicit recovery, provider identity changes, compatible independent work, and retained
  success/unknown operation facts are covered. A fake timeout test observed exactly one fake call,
  no Offline extractor call, no analysis result, and a visible error.
- Browser plugin not available; used the existing headed Chrome Playwright CLI fallback with scripts
  and artifacts under `/tmp`. Dedicated Streamlit processes on ports 8503–8506 represented demo,
  development with fake opt-in, production, and contradictory production-plus-fake configuration.
  Existing user servers on 8501/8502 were left untouched.
- Final fresh-process browser runs at **1440 × 1000** and **390 × 844** completed demo review through
  confirmed outputs and unavailable delivery; both downloads remained available. Fake review
  completed exact preview, separate confirmation, one Create, and verified GET receipt. Neither
  workflow rendered an application exception. Page title and route matched the application, and
  document scroll width equaled viewport width in all measured cases.
- At both widths, independent demo drafting completed Open Demonstration Project, Confirm Context,
  Generate SI Draft, Confirm SI draft, and one available Markdown download. Keyboard focus plus
  Enter activated each operation. Human confirmation and unpublished/synthetic disclosures remained.
- At both widths, all seven entry routes under production and invalid configuration (28 cases)
  showed the corresponding unavailable/error screen without synthetic workflow controls or
  application exceptions. Single-mode demo had status without a selector; enabled development
  exposed explicit Offline/Internal fake selection. Light styling remained readable under a dark
  host preference. Policy changes with retained state were tested through AppTest rather than
  misrepresented as cross-process browser session persistence.
- Screenshots inspected include `/tmp/b07-1440-demo.png`, `/tmp/b07-390-fake.png`,
  `/tmp/b07-1440-8505.png`, `/tmp/b07-390-8506.png`, and `/tmp/b07-390-draft.png`.
- Browser-script corrections: receipt text appears in both action and history views, requiring a
  scoped locator. A code hot reload during testing invalidated an old process's session; final
  browser acceptance was repeated after restarting the dedicated test processes. Console inspection
  found expected connection errors during that restart and route-relative Streamlit bootstrap 404
  probes on deep links; root bootstrap recovered and every guard rendered correctly. No unresolved
  application error remains on final fresh-process runs.

## 12. Limitations and deferred work

This foundation provides deployment controls, not authentication or authorization for individual
users. Deployment operators control environment settings. Production remains unavailable until
separately approved real capabilities exist. No live availability, actual enterprise failure, or
cross-session durable reconciliation can be certified using the synthetic test paths.

## 13. Final completion record

Batch 07 completed and verified on 2026-09-11. R9a is Verified, parent R9 remains Accepted,
and R9b remains Deferred. The active-plan pointer is NONE. README, SPEC, and DEMO describe the
implemented foundation and its unavailable production boundary. No unresolved product decision or
blocking verification finding remains. The authorized completion commit is made on
`codex/final-stage-i2-review-summary`; the session handoff records its commit ID and push result.
No production release or live enterprise operation is part of this completion.
