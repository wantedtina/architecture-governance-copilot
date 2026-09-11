# Batch 12 — Persistent workflow actions

Document status: `COMPLETED_VERIFIED`
Included refinement: R15
Baseline: 66aaea5
Approval: User approved extending the existing fixed-action pattern across workflow steps.

## Scope and sequence

1. Introduce a scoped shared action container in app.py, replacing generic form-submit CSS.
2. Project Context retains confirmation; drafting uses generate, then confirm, then download;
   Review Inputs uses manifest confirmation, then analysis; Human Review uses record confirmation;
   Outputs uses continue to delivery; actionable Delivery uses preview, confirm request, then create.
   Protected delivery outcomes have no additional submitting action.
3. Preserve widget keys, callbacks, ordering, disabled conditions, and publication guards. Add
   adequate bottom space and responsive sizing. Secondary actions stay in the document flow.
4. Run focused AppTests, full tests, Ruff, build, diff check, and actual desktop/narrow browser flows.
5. Update documentation, lifecycle, and Git handoff. Close test browser and stop its test server.

## Boundaries and compatibility

Presentation-only. No provider/schema/fixture change, new mode, integration, or permission. The
container scopes styling; it does not introduce duplicate widgets or call handlers. No migration.

## Progress and acceptance

- [x] One current primary action fixed across applicable workflow steps; secondary actions inline.
- [x] Existing state gates, editing, confirmation and duplicate-submission protections preserved.
- [x] Automated and desktop/narrow browser acceptance passed; test instances cleaned up.
- [x] Documentation and lifecycle synchronized.

## Verification and completion

Completed 2026-09-11. R15 Verified; active pointer cleared.

- Existing focused AppTests: 64 passed, including source invalidation, confirmation, delivery
  capability, and protected-operation paths. Full repository: 498 passed.
- uv sync, Ruff check, Ruff format check, uv build, and git diff --check passed.
- Actual Chromium via Playwright CLI (dedicated Browser plugin unavailable), agc-acceptance session,
  fresh development profile with in-memory fake enabled on port 8509. No external submissions.
- Desktop 1440x1000 and narrow 390x844: verified one fixed primary container, stable viewport
  coordinates during scrolling, state transitions, and no offscreen action bar.
- Verified Context confirmation, drafting generation/confirmation/download, review-input
  confirmation/analysis, Human Review confirmation, output continuation, and delivery
  preview/confirmation/create. Both desktop and narrow fake delivery completed read-back;
  protected success exposed no duplicate Create action. No application exceptions.
- Inspected draft, review and delivery screenshots. Reserved bottom space keeps final content
  reachable above the bar. Secondary buttons remain inline with their original behavior.
- Browser checks wait for route rendering before checking the current action.
- Closed the test browser and stopped its test server; user instances retained. Artifacts in /tmp.
- Existing branch used for commit and push. No schema, fixture, provider or dependency changes.

Existing synthetic-only provider and delivery limits remain unchanged.
