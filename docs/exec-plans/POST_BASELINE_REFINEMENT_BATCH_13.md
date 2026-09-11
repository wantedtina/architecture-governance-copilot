# Batch 13 — Visible Human Review evidence

Document status: `COMPLETED_VERIFIED`
Included refinement: R16
Baseline: 8c25e57
Approval: User explicitly requested default-expanded evidence for all items and Review Outcome.

## Scope and sequence

1. Change the shared evidence renderer default to expanded. Every Human Review collection and
   outcome uses this renderer; output comparison already explicitly expands evidence.
2. Extend the existing human-edit AppTest with visibility assertions. Synchronize maintained docs.
3. Run automated checks and desktop/narrow browser validation, then clean up test instances.

## Boundaries and compatibility

Presentation-only default; manual collapse remains available. Source quotes and metadata remain
read-only. Empty evidence retains its explicit message. No state, fixture, provider or dependency
changes; no migration or unresolved product decision.

## Progress and acceptance

- [x] Outcome and all item evidence expanded, with original source and quotes preserved.
- [x] Automated and desktop/narrow browser checks passed, including manual collapse and confirmation.
- [x] Documentation/lifecycle synchronized; test browser/server closed.

## Verification and completion

Completed 2026-09-11. R16 Verified; active pointer cleared.

- Full repository: 498 tests passed. Existing human-edit/exclusion test now asserts all evidence
  expanders are initially expanded before exercising reviewed-output generation.
- uv sync, Ruff check, Ruff format check, uv build, and git diff --check passed.
- Actual Chromium via Playwright CLI (dedicated Browser plugin unavailable), fresh demo server
  port 8509, agc-acceptance session. Inspected desktop 1440x1000 and narrow 390x844 screenshots.
- Verified outcome evidence and all six item tabs start expanded, manual collapse/reopen works,
  source labels/location/quotes remain visible, narrow layout has no horizontal overflow, and
  record confirmation reaches Generated Outputs without application exceptions.
- Closed the test browser and stopped its server; user instances retained. Artifacts in /tmp.
- Existing branch used for commit and push. No source-state, provider or fixture changes.

Existing offline provider and mandatory human confirmation boundaries remain unchanged.
