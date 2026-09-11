# Batch 09 — Evidence saving and confirmation

Document status: `COMPLETED_VERIFIED`
Included refinement: R12
Baseline: 1e40a2e
Approval: User approved explicit saving, valid custom Context confirmation, and generation-only
provider blocking. No unresolved product decisions.

## Scope and sequence

1. Separate input validity from provider eligibility in ui_support.py.
2. Add Save evidence and durable saved/unsaved status in app.py; edits invalidate saved status and
   prior drafting confirmation. Require saving before Context confirmation. Validate generation
   compatibility on the drafting page. Preserve source manifests and independent review state.
3. Update focused support/AppTests, README, SPEC, and DEMO.
4. Run full tests, Ruff, build, diff check, and actual desktop/narrow browser acceptance.

## Boundaries and compatibility

No connectors, credentials, new providers, or durable storage. Existing session evidence without a
save marker requires explicit saving. Reset clears the marker. Saved content survives routing and
refresh. Invalid or empty evidence cannot be saved. Custom content never receives sample output.

## Acceptance and progress

- [x] Valid notes/uploads can be saved and confirmed; unsaved edits block confirmation.
- [x] Custom Context reaches drafting with generation disabled and an explicit explanation.
- [x] Exact sample still generates after saving and human confirmation.
- [x] Full automated and desktop/narrow browser acceptance passed.
- [x] Documentation and lifecycle synchronized.

## Verification evidence and completion

Completed 2026-09-11. R12 Verified; active pointer cleared.

- Focused support and AppTests: 131 passed.
- Full repository: 495 tests passed; uv sync, Ruff check, Ruff format check, uv build, and
  git diff --check passed.
- Fresh demo server on port 8508. Actual Chromium via Playwright CLI (dedicated Browser plugin
  unavailable), desktop 1440x1000 and narrow 390x844.
- Verified typing then directly clicking Save evidence, enabled Context confirmation, custom
  generation disabled, returning and editing revokes confirmation, uploaded Markdown saving and
  continuation on narrow screens, and exact sample generation through human confirmation and
  availability of the confirmed Markdown download.
- Inspected screenshots. No application exceptions; console only reported local font loading.
- Removed an immediate textarea rerun so clicking Save evidence after typing saves on the first
  click. Snapshot equality keeps saved status across routing and detects subsequent changes.
- No live integrations, provider changes, or confidential data. Browser artifacts remain in /tmp.
- Existing branch retained for commit and push; no history rewrite.

Remaining limitation: deterministic generation supports only the exact synthetic sample.
