# Batch 14 — Visible reviewer edits

Document status: `COMPLETED_VERIFIED`
Included refinement: R17
Baseline: 2b2134d
Approval: User approved the three-layer edit-awareness proposal. No unresolved product decisions.

## Scope and sequence

1. Reuse PendingReviewChanges for edited/excluded/invalid card styling and explicit ownership labels.
2. Show Changed beside affected fields, short before/after values inline and long comparisons in
   expanders. Include outcome changes. Keep literal source values safe and evidence read-only.
3. Show distinct edited/excluded/needs-correction counts in tab labels; add a compact change summary
   to the existing fixed confirmation area. Reverting normalized values removes markers.
4. Update existing AppTests and docs; run full tests, Ruff, build, diff check and desktop/narrow
   browser checks for edits, exclusions, invalid values, revert, navigation and confirmation.
5. Close test browser/server and complete lifecycle/Git handoff.

## Boundaries and compatibility

No state/schema/provider/fixture change. Stable card/widget keys avoid remounting edits. Original
analysis remains immutable; source-change invalidation and publication guards remain unchanged.
No new modes or integrations. Long text comparison is optional, not an additional approval step.

## Progress and acceptance

- [x] Item/field/page indications distinguish reviewer edits from source evidence.
- [x] Revert, invalid values, exclusions and routing retain existing semantics.
- [x] Automated/browser checks passed; test instances cleaned up.
- [x] Documentation and lifecycle synchronized.

## Verification and completion

Completed 2026-09-11. R17 Verified; active pointer cleared.

- Focused edit/exclusion and pending-awareness tests: 2 passed. Full repository: 498 passed.
- Existing awareness test verifies edited/excluded tab counts, ownership marker, original/new
  owner comparison, footer count, invalid date, route retention, and removal of markers on revert.
- uv sync, Ruff check, Ruff format check, uv build, and git diff --check passed.
- Actual Chromium via Playwright CLI (dedicated Browser plugin unavailable), fresh demo server
  port 8509, agc-acceptance session. Desktop 1440x1000 and narrow 390x844 screenshots inspected.
- Verified blue edited card border/background, adjacent owner comparison, fixed footer counts,
  excluded card treatment, keyboard checkbox control, invalid-date treatment, revert cleanup,
  expandable long question comparison, immutable source quotes, and confirmation to outputs.
- No application exceptions. Comparison values render as text, never HTML. Stable card keys
  preserve widget state; existing PendingReviewChanges remains the sole comparison source.
- Browser automation used the visible field's full date label and keyboard interaction with the
  native checkbox after pointer hit-testing of its styled input was unsuitable.
- Closed the test browser and stopped its server; user instances retained. Artifacts in /tmp.
- Existing branch used for commit and push. No provider, fixture, dependency or schema changes.

Existing offline demo and mandatory human review limits remain unchanged.
