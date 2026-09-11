# Batch 15 — Preserve Human Review tab selection

Document status: `COMPLETED_VERIFIED`
Included refinement: R18
Baseline: bb458d9
Approval: User approved retaining the current category through edits and dynamic count changes.

## Scope and implementation sequence

1. Inspect tab identity and rerun behavior; preserve selection with native Streamlit controls.
2. Verify continuous edits, exclusions, invalid dates and revert across all six categories.
3. Update maintained documentation and focused tests. Run full repository checks and desktop/narrow
   real-browser acceptance. Close the dedicated browser and server.
4. Complete register lifecycle, commit and push the existing branch.

## Boundaries, dependencies and compatibility

No blockers or unresolved product decisions. No provider, schema, fixture or dependency changes.
Preserve all field keys, comparison semantics, immutable evidence, confirmation and invalidation.
No new integrations or additional approval steps. Browser presentation state is not review authority.
Affected files: app.py, focused tests, maintained docs and the refinement register.

## Progress

- [x] Native tab identity correction and focused verification.
- [x] Full tests, Ruff checks, build and diff check.
- [x] Desktop/narrow browser acceptance and cleanup.
- [x] Documentation, lifecycle and Git handoff.

## Discoveries and verification

Existing tabs have dynamic labels and no stable identity. Previous browser checks explicitly
reselected categories after edits, masking this regression. Acceptance now must assert selection
before any further click.

The first browser probe reproduced the reset even with a fixed tab key. Native stateful tabs
plus rebinding the selected category to its current count-bearing label preserve selection.
Tab switches rerun the page; all six editors still render, preserving field state and review data.
Clearing review widget state resets selection for a new analysis. No migration is required.
Focused AppTest and six-category state tests: 7 passed.

## Completion and limitations

Completed 2026-09-11. R18 Verified and active pointer cleared.

- uv sync passed; full pytest: 504 passed in 54.10 seconds.
- Ruff check and format check passed; uv build and git diff --check passed.
- Actual Chromium via Playwright CLI, dedicated agc-acceptance session and demo server port 8509.
- All six categories at 1440x1000 and 390x844: first edit, second edit, revert, exclusion and
  reinclusion retained aria-selected without reselecting the category. Findings invalid date and
  correction also retained selection. Evidence quotes remained unchanged. Confirmation reached outputs.
- Desktop and narrow screenshots inspected. Temporary scripts/screenshots remain outside Git in /tmp.
- An intermediate browser attempt encountered source-reload invalidation during implementation;
  reloaded the synthetic package and repeated the full acceptance successfully against final code.
- Dedicated browser closed and server stopped. User services and windows preserved.
- Existing branch used for commit/push. Existing offline and mandatory review boundaries unchanged.
