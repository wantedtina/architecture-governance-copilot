# Batch 17 — Human-selected outcome evidence

Document status: `COMPLETED_VERIFIED`
Included refinement: R21
Baseline: 733e601
Approval: User approved the outcome evidence correction.

## Scope, sequence and acceptance

1. Resolve selected current transcript lines to immutable source evidence when the analyzed outcome
   has no supporting evidence. Preserve existing outcome evidence and source-change invalidation.
2. Show selection beside Review Outcome. Warn immediately and disable confirmation for a stated
   outcome without evidence. Keep Not stated valid; use a clear service-side guard as well.
3. Track evidence selection as a human change; test reconstruction, routing, invalidation and both
   confirmation paths. Run full tests, Ruff, build and diff check.
4. Verify in a real browser at desktop/narrow sizes, close browser/server, synchronize lifecycle,
   commit and push the current branch.

## Boundaries and compatibility

No model/provider/fixture/dependency change. No inferred approval, editable evidence quote, live
integration or extra workflow. Existing source evidence stays read-only. New selections use exact
line references; a new analysis clears review widgets. No persistent-state migration or blockers.
Affected components: app.py, ui_support.py, focused tests and maintained documentation.

## Progress and verification

- [x] State/reconstruction and focused tests.
- [x] UI validation and full acceptance.
- [x] Browser cleanup, docs and Git handoff.

## Completion

Completed 2026-09-11. The human must judge whether selected evidence supports the chosen outcome.

Focused confirmation, reconstruction and routing tests: 3 passed. Tests cover Not stated without
support, clear rejection of an unsupported stated outcome, binding immutable transcript evidence,
selection retention through edits/routes, source-location validation and human change summary.

Final verification: 514 tests passed in 61.78 seconds. uv sync, Ruff check, Ruff format check,
uv build and git diff --check passed. Actual Chromium in agc-acceptance on demo port 8509:
Not stated enabled confirmation, stated outcome without evidence disabled it, selected transcript
line enabled confirmation and generated outputs. Desktop 1440x1000 and narrow 390x844 screenshots
inspected; returning to Human Review preserved selection and reconfirmation succeeded.
The searchable native combobox required typing/keyboard selection in automation. The first narrow
capture retained an off-canvas sidebar during resize; repeated after layout settled and verified the
unobscured selector, quote and action. Browser and server closed; artifacts remain in /tmp.
R21 Verified; active pointer cleared. Existing branch retained for commit and push.
