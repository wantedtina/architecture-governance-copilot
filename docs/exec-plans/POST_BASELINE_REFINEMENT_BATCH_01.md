# Post-baseline refinement Batch 01 — deliberate light-only theme

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R10`

Approval boundary: The user accepted R1-R10 as future implementation intent, authorized creation of
this first execution plan, and explicitly approved Batch 01 on 2026-09-10. Only R10 and the scope in
this plan are authorized for implementation.

Baseline revision: `6d77582713907478ad5f03eccfc8bac102b5a209`

Current phase: `COMPLETE`

## 1. Scope

Make the current Streamlit proof of concept deliberately and consistently light-only through one
project-level native Streamlit theme. Align native widgets, backgrounds, borders, status surfaces,
code blocks, and the sidebar with the existing light visual language. Remove only conflicting
global color overrides from the existing custom visual layer; retain product-specific layout,
branding, processing feedback, and component structure.

The proposed native tokens are:

| Role | Value | Existing design relationship |
| --- | --- | --- |
| Base | `light` | Locks the application to one supported color mode. |
| Primary | `#D93636` | Retains the action-red direction while meeting 4.5:1 contrast with white text. |
| Background | `#F7F8FA` | Matches the current light application canvas. |
| Secondary background | `#EEF0F2` | Provides a distinct neutral surface for native controls and code regions. |
| Text | `#061D33` | Uses the existing dark navy for strong readable text. |
| Link / blue semantic | `#0B56A8` | Uses the current accessible dark blue. |
| Green semantic | `#238500` | Uses the current dark success green. |
| Red semantic | `#D93636` | Keeps errors and primary actions consistent with the approved action color. |
| Border | `#D5DBE1` | Slightly strengthens the current `#E1E5E8` border for native-widget definition. |
| Sidebar background | `#061D33` | Matches the current branded navy sidebar. |
| Sidebar secondary background | `#0B2A47` | Adds a distinct dark control surface. |
| Sidebar text | `#FFFFFF` | Preserves the current high-contrast sidebar text. |
| Sidebar primary | `#238500` | Retains the dark green accent at approximately 4.74:1 against white. |
| Sidebar border | `#164365` | Defines native sidebar controls without relying on the global DOM selectors. |

Exact token adjustment is allowed during visual verification only when required to satisfy readable
contrast or eliminate a verified mismatch. Any material change to the action-red direction or the
light-only product behavior requires user approval and a recorded decision below.

## 2. Explicit non-goals

- Do not implement dark mode, a theme toggle, `[theme.light]` / `[theme.dark]`, conditional
  `st.context.theme` behavior, or theme-aware asset switching.
- Do not redesign the workflow, navigation, cards, forms, or content hierarchy.
- Do not implement R1-R9 or make preparatory state, provider, fixture, or integration changes.
- Do not add dependencies, remote fonts, credentials, external services, or network behavior.
- Do not replace or expand the brand asset set.
- Do not opportunistically migrate deprecated widget parameters or refactor unrelated CSS.

## 3. Dependencies and unresolved blockers

The user approved this plan on 2026-09-10. The installed Streamlit version is locked to `1.59.2`,
and the repository currently has no `.streamlit/config.toml`.

Approval of this plan resolves the remaining R10 decisions as follows:

1. retain action red as the native primary color and use the token table above;
2. add no separate settings-menu explanation unless verification shows misleading behavior;
3. verify all five current routed stages and the opt-in fake delivery path at a desktop viewport
   under both light and dark host color preferences; and
4. finish the current theme baseline now, with later UI batches responsible for repeating relevant
   light-theme regression checks after their own changes.

No other product, security, data, or interaction blocker is known for this batch.

## 4. Affected components and files

- `.streamlit/config.toml` — new authoritative single light theme.
- `app.py` — audit `_apply_visual_theme()` and remove only global/native color overrides that
  conflict with the theme; retain product-specific CSS and semantic no-network/human-review copy.
- `tests/test_theme_config.py` — focused configuration contract for a single light theme and the
  approved tokens, unless an existing focused test file is demonstrably clearer during implementation.
- `tests/test_app.py` — update only assertions affected by removal of conflicting native-theme CSS
  or add a narrowly scoped rendered-state assertion if needed.
- `README.md` and `SPEC.md` — document the verified light-only PoC decision and operator behavior.

## 5. Implementation steps

- [x] Reconfirm the branch, working tree, active-plan pointer, and baseline before application work.
- [x] After explicit approval, set this plan to `IN_PROGRESS` and R10 to `In progress`.
- [x] Add one `.streamlit/config.toml` with `[theme]`, `base = "light"`, the approved main and
  sidebar tokens, native borders, and no light/dark variants or remote font dependency.
- [x] Compare native-theme ownership with `_apply_visual_theme()` and remove only conflicting
  background, text, sidebar, native-button, native-input-focus, native-tab, and native-metric color
  overrides. Keep branded structural classes, responsive layout, and the processing overlay.
- [x] Add focused configuration tests that parse the TOML, assert the single-theme contract and
  required tokens, and reject accidental light/dark variant sections.
- [x] Update `README.md` and `SPEC.md` with the implemented contract; retain them in the active
  uncommitted batch until final visual verification succeeds.
- [x] Run the automated and build verification commands and record actual results below.
- [x] Run rendered browser verification for the required matrix, capture concise evidence, and
  correct any verified contrast or consistency defects within the approved token direction.
- [x] On success, mark this plan `COMPLETED_VERIFIED`, mark R10 `Verified`, clear the active-plan
  pointer, and record the final completion evidence. Do not commit or push without separate user
  instruction.

## 6. Acceptance criteria

- The application uses one project-level `[theme]` with `base = "light"` and no alternate theme.
- Native Streamlit surfaces remain light when the host/browser preference is light or dark.
- Native and custom surfaces form one coherent light hierarchy without mixed dark native controls.
- Primary, secondary, focus, disabled, status, form, code, Markdown, and sidebar states remain
  readable and distinguishable without relying on color alone.
- The current action-red treatment remains the primary action language unless an approved contrast
  correction is recorded.
- Existing product-specific branding and responsive structure remain intact.
- The deterministic Offline path and opt-in Internal fake path behave exactly as before; no silent
  fallback, network call, provider-boundary change, or weakening of human confirmation occurs.
- Operator documentation states that the PoC is deliberately light-only and does not imply that
  dark mode is permanently excluded from future approved scope.

## 7. Required automated and browser verification

Planned automated commands from the repository root:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Planned browser matrix at a desktop viewport:

| Host preference | Path and critical states |
| --- | --- |
| Light | Project Context; drafting source/editor controls; Review Inputs partial and ready states; Human Review default and invalid date; Generated Outputs; opt-in fake request preview/confirmation/receipt. |
| Dark | Repeat the same path and confirm that the app remains light-only with equivalent contrast, focus, disabled, warning, error, success, code, Markdown, and sidebar presentation. |

Use the available browser automation surface for rendered checks. If host preference cannot be
emulated reliably, record the limitation and complete the missing preference check manually before
verification; do not infer visual success from configuration parsing alone.

## 8. State invalidation, compatibility, and migration

This batch changes presentation configuration only. It must not change session-state keys,
fingerprints, routes, drafting or review input identities, analysis eligibility, review confirmation,
output generation, or publication reconciliation. Existing sessions may require a Streamlit server
restart or browser refresh for configuration to apply; this is presentation reload behavior, not a
workflow migration. Remote-operation reconciliation facts must remain untouched.

## 9. Progress

- [x] R1-R10 intake reviewed against the current revision, code, tests, and maintained documentation.
- [x] Dependency and overlap assessment completed.
- [x] R10 selected as the smallest independent first batch.
- [x] Execution plan created and linked as the sole active plan.
- [x] User approved the execution plan on 2026-09-10.
- [x] Implementation started.
- [x] Automated verification passed.
- [x] Browser verification and final user visual acceptance passed within the available environment.
- [x] Maintained documentation synchronized in the active uncommitted batch.
- [x] Completion record finalized and active pointer cleared.

## 10. Decisions and important discoveries

- `6d77582713907478ad5f03eccfc8bac102b5a209` is the actual planning baseline; it follows governance
  commit `b8a7d31` and records R1-R10 without application changes.
- The checked-out branch is `codex/final-stage-i2-review-summary`, and the working tree was clean at
  plan creation.
- The existing app injects a large custom light visual layer, including native-widget color
  overrides, but has no project-level Streamlit theme. This explains the mixed host-dark behavior
  while keeping the approved fix bounded.
- The current action-dark token `#E13B3B` has approximately 4.29:1 contrast against white and does
  not meet the 4.5:1 target. The proposed `#D93636` preserves the red direction at approximately
  4.63:1; the existing dark green `#238500` is approximately 4.74:1 against white.
- R10 does not depend on the workflow, input, fixture, delivery, or deployment-policy decisions in
  R1-R9. Later UI work must repeat relevant theme checks after modifying screens.
- The user explicitly approved Batch 01 and its four readiness decisions on 2026-09-10.
- The available in-app browser and connected Chrome session both reported
  `prefers-color-scheme: dark = false`. Their supported automation surfaces expose viewport
  control but no reliable color-scheme emulation, so the required dark-host pass cannot be claimed
  from this session without changing the user's host appearance or obtaining a dark-preference
  browser session.

## 11. Actual verification evidence

Automated verification from the repository root on 2026-09-10:

- `uv sync` completed successfully (`54` packages resolved and `51` audited).
- `uv run pytest` passed: `370 passed in 15.48s` on the final pre-commit rerun.
- Focused theme and UI tests passed: `75 passed in 15.02s` across
  `tests/test_theme_config.py`, `tests/test_app.py`, `tests/test_ui_support.py`, and
  `tests/test_runtime_dependencies.py`.
- `uv run ruff check .` passed after Ruff corrected the new test's import block.
- `uv run ruff format --check .` passed: `38 files already formatted`.
- `uv build` produced the source distribution and wheel successfully.
- `git diff --check` passed with no output.
- `uv run streamlit config show` reported `base = "light"` and the approved main/sidebar tokens.

Rendered verification at a desktop viewport with a light host preference:

- The rendered app reported `prefers-color-scheme: dark = false`; computed colors included the
  `rgb(247, 248, 250)` application background, `rgb(217, 54, 54)` primary button, and
  `rgb(6, 29, 51)` sidebar background in the in-app browser.
- The Offline path completed Project Context, SI drafting, Review Inputs partial and ready states,
  Human Review, and Generated Outputs without a mixed dark native surface or workflow regression.
- Entering action due date `2026-99-99` produced the expected inline error and generated no output;
  restoring `2026-07-24` allowed the human-confirmed output flow to complete.
- The opt-in Internal fake path loaded the synthetic Confluence snapshot, ran local fake AIF
  analysis, required Human Review confirmation, generated the exact Create preview, required a
  separate exact-preview confirmation, submitted once to the in-memory fake Azure DevOps gateway,
  and returned receipt `7001` with `Verified: Yes` after GET read-back.
- The Streamlit main menu exposed no theme choice, so no extra settings-menu explanation was
  required by the approved decision.

The equivalent rendered pass under a dark host preference remains outstanding. Configuration
parsing and light-preference rendering are not being treated as substitutes for that acceptance
evidence.

On 2026-09-10, the user reviewed the reported limitation, accepted the implemented result without
requesting a further dark-host rerun, and explicitly authorized continuation to later batches. This
user acceptance closes the Batch 01 visual gate without misrepresenting the unavailable automated
dark-preference evidence.

## 12. Remaining limitations and deferred work

- R1-R9 remain accepted but outside this active batch.
- Dark-mode support remains a possible separately approved future refinement.
- Later workflow and presentation batches must rerun light-theme regression checks for their changed
  screens.
- This batch does not alter the current custom CSS beyond conflicts with the approved native theme;
  broader visual redesign remains out of scope.
- The browser automation surfaces available during implementation could not emulate a dark host
  preference. That evidence limitation remains recorded above; the user explicitly accepted the
  implementation and closed the visual gate.

## 13. Final completion record

Completed and verified on 2026-09-10. The project now has one deliberate native Streamlit light
theme, conflicting global native-color overrides are removed, focused and full automated checks
pass, the Offline and Internal fake browser paths preserve their safety boundaries, and the user
accepted the remaining visual evidence limitation. R10 is `Verified`; the active-plan pointer is
cleared. No R1-R9 application scope was included in this batch.
