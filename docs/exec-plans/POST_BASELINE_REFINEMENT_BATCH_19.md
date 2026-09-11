# Batch 19 — Edited Internal fake review packages

Document status: `COMPLETED_VERIFIED`
Included refinement: R23
Baseline: d07a638
Approval: User approved dynamic fake analysis plus downstream delivery review.

## Scope and sequence

1. Add a request-aware synthetic response factory to the fake transport. Preserve canonical output,
   carry editable metadata, and group changed transcript lines using shared deterministic rules.
   Keep AifGovernanceExtractor responsible for context, schema and evidence validation.
2. Bind fake delivery capability to the current confirmed manifest only for the configured synthetic
   SI/provider. Preserve all target mappings, due-date checks, correlation and duplicate protection.
3. Test changed inputs through human review/output/Create, unmapped values and stale inputs; preserve
   no-fallback and production-denial tests. Run full checks and desktop/narrow browser acceptance.
4. Close dedicated test services/browser, synchronize docs/lifecycle, commit and push.

## Boundaries and dependencies

Development/test only; no new provider mode, live API, model schema or fixture change. Default fake
provider identity advances to v2 to revoke stale packages. Canonical synthetic SI identity is fixed.
Changing a governance ticket to an unmapped value or leaving owner/date unset remains an explicit
readiness blocker; no invented enterprise mapping. No persistent migration or unresolved decisions.
Affected: fake transport/responder, runtime capability binding, UI/state, tests and maintained docs.

## Progress and verification

- [x] Response factory and focused tests.
- [x] Confirmed capability binding and downstream tests.
- [x] Full/browser acceptance and cleanup.
- [x] Lifecycle and Git handoff.

## Completion

R23 is verified. Production remains unavailable and separately governed.

Verification: canonical runtime/fixture tests 38 passed; focused edited package, no-fallback
and production checks 5 passed. Final full suite 531 passed in 80.17 seconds. uv sync, Ruff check,
format check, build and diff check passed. Dynamic capability tests reject wrong source/provider/mode
and production, while edited-package UI tests reach fake Create or an explicit unmapped-parent block.
No fixture or model-schema change. Current fake default identity is internal-fake-aif-v2.

Real Chrome acceptance passed at 1440 x 1000 and 390 x 844: edit Internal fake transcript and
metadata, confirm inputs, analyze with Fake AIF, review and edit action owner/date, generate outputs,
preview and confirm the fake request, and create a work item with Succeeded status. Screenshots
were visually checked; no application exception occurred. The dedicated agc-acceptance browser
and port 8509 test server were closed. Existing user sessions were preserved.

Lifecycle synchronized; this batch is ready for its authorized commit/push on the current branch.
