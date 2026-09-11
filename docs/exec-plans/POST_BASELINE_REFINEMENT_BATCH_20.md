# Batch 20 — Traceable action details and delivery guidance

Document status: `COMPLETED_VERIFIED`
Included refinement: R24
Baseline: f0e4608
Approval: User explicitly approved the proposed demo/development improvements.

## Scope and sequence

1. Extract explicit speaker commitments and unambiguous dates in synthetic transcript grouping.
   Merge ownership acknowledgement evidence only with a unique matching commitment; retain all
   ambiguous lines for review. Preserve canonical fixtures and strict provider validation.
2. Show mapped owner choices and delivery requirements during Human Review. Keep local output
   confirmation available when delivery requirements are incomplete; never invent mappings.
3. Run focused tests, full repository checks, and desktop/narrow browser acceptance.
4. Close test resources, synchronize lifecycle, commit and push the existing branch.

## Boundaries and dependencies

No live APIs, production change, schema relaxation, or new dependencies. Shared deterministic
rules serve Offline and Internal fake. Existing evidence validation and publication checks remain.
Advance default provider identities to invalidate stale analyses; no persistent migration.
Affected: demo_review.py, runtime dependencies, app.py, tests and maintained documentation.
No unresolved product decisions. Unsupported language or ambiguous attribution requires human review.

## Progress and evidence

- [x] Extraction and focused tests.
- [x] Human Review guidance and focused tests.
- [x] Full checks and desktop/narrow browser acceptance.
- [x] Cleanup and lifecycle/Git handoff.

## Completion

R24 verified; active-plan pointer cleared. Authorized commit/push on the existing branch.

Initial focused checks: 6 passed. Initial full suite: 535 passed in 81.53 seconds.
Real Chrome desktop (1920 x 963) and narrow (390 x 844) verified candidate owner/date, two evidence
quotes per action, explicit mapped-owner editing, local confirmation and successful fake Create
with GET read-back. The dedicated test tab was closed and viewport reset; user tab untouched.
Final review tightened dates to explicit deadline cues. Focused regression: 6 passed.
Final full suite: 537 passed in 83.07 seconds. uv sync, Ruff check, format check, uv build and
git diff --check passed. Port 8509 test server stopped with exit code 0. No user server was stopped.
Default provider identities advance to v3; existing inputs must be re-confirmed and re-analyzed.
Remaining limitation: literal English rules only; ambiguous or unsupported text requires human edits.
