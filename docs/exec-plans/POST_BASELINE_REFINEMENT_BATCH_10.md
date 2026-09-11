# Batch 10 — Input-aware offline demo drafting

Document status: `COMPLETED_VERIFIED`
Included refinement: R13
Baseline: ea53c6a
Approval: User approved extending the existing demo drafter to reflect custom Evidence without
new modes or real APIs. No unresolved product decisions.

## Scope, components, and sequence

1. Extend si_drafting.py: preserve exact sample output; for other nonempty Evidence, build a
   template-shaped draft with deterministic topic grouping, quoted evidence line references,
   complete source appendix, and explicit gaps. Do not reuse unsupported sample-only facts.
2. Update readiness messages and app wording; retain save, manifest binding, editing, and confirmation.
3. Update provider, state, and AppTests plus current documentation and AGENTS caveat.
4. Run full tests, Ruff, build, diff check, and real desktop/narrow browser tests. Close test
   browser and stop only the server created for this batch after acceptance.

## Boundaries and compatibility

No new mode, provider interface, API, credential, enterprise connector, database, or dependency.
Only the existing synthetic project/template/repository package is supported. Evidence is data,
never instructions. Topic grouping is lexical, not semantic interpretation or conflict resolution.
All source text remains available; unmapped material is retained. Existing source fingerprints
and edit invalidation apply. Exact canonical fixture and review extractor remain unchanged.

## Acceptance and progress

- [x] Custom notes/uploads generate different, traceable drafts without sample-only assertions.
- [x] Empty Evidence rejected; canonical draft unchanged; injected Markdown stays quoted.
- [x] Save, generate, edit, confirm, download and source invalidation verified.
- [x] Full repository and desktop/narrow browser acceptance passed; test instances cleaned up.
- [x] Current documentation and lifecycle synchronized.

## Verification and completion

Completed 2026-09-11. R13 Verified; active pointer cleared.

- Focused provider/support/AppTests: 150 passed. Full repository: 498 passed.
- uv sync, Ruff check, Ruff format check, uv build, and git diff --check passed.
- Actual Chromium via Playwright CLI, dedicated agc-acceptance session, fresh server port 8509;
  desktop 1440x1000 and narrow 390x844 screenshots inspected.
- Verified notes saving, Context confirmation, generation, literal retention value in the draft,
  human edits, confirmation, and downloaded Markdown preserving edits. Replaced notes with an
  uploaded Markdown document, regenerated, and verified the new value replaced the old value.
- Custom draft contains no sample-only 90-day retention or August release assertions. Automated
  tests preserve exact canonical output, reject empty evidence, and retain unmapped/instruction-like
  source content as indented literal text with deterministic output.
- No application exceptions. Browser console only reported local font loading.
- Closed agc-acceptance and stopped its server. No user browser or service was closed. Working
  screenshots, scripts, and uploads remain outside the repository.
- Existing branch used for commit and push; no API, dependency, mode, or enterprise integration added.

Limitations: deterministic topic grouping only, synthetic repository, no arbitrary-input
review analysis. Real model and enterprise integration remain later work.
