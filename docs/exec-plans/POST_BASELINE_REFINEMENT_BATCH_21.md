# Batch 21 — Free-form synthetic delivery inputs

Document status: `COMPLETED_VERIFIED`
Included refinement: R25
Baseline: eea0bb2
Approval: User explicitly approved fixing the free-form demo workflow end to end.

## Scope and sequence

1. Add deterministic synthetic aliases for any nonblank owner and governance ticket. Preserve
   canonical mappings and bind generated mappings to the confirmed metadata and reviewed result.
2. Show local mapping behavior in Review Inputs, Human Review and Delivery. Sample owner buttons
   remain conveniences, not an allowlist. Empty owner, parent or date remains a named blocker.
3. Test SYN-205, arbitrary ticket text and custom owners through analysis, review, output and fake
   Create. Check missing fields, stale previews, duplicate protection, Offline and production denial.
4. Run repository acceptance and Chrome desktop/narrow verification. Close only test resources,
   complete lifecycle, commit and push the existing branch.

## Dependencies and boundaries

Affected: runtime wiring, a pure synthetic mapping helper, UI and focused tests/docs. No dependency,
fixture, provider extraction, database, API, credential or production behavior change. Mapping is
only used by the opt-in development/test fake capability; generic publication mapping validation
is retained. Missing data is never invented. Existing preview bindings include the resolved target
maps and will revoke old confirmation; stable action correlations retain duplicate protection.
No persistent migration or new deployment mode. No unresolved product decisions.

## Acceptance criteria

Edited transcript and metadata including arbitrary nonempty ticket text plus a custom human owner
must reach fake Create/read-back without a sample allowlist. Existing reviewed text remains intact.
Blank required fields block only delivery and are explained early. Offline can generate local
outputs from custom review edits but cannot submit; production continues to deny synthetic paths.

## Progress and evidence

- [x] Runtime mappings and focused tests.
- [x] UI guidance and end-to-end focused tests.
- [x] Full checks and browser verification.
- [x] Cleanup, lifecycle and Git handoff.

## Completion

R25 verified. This is local simulation, not enterprise identity or parent existence verification.

Focused runtime/mapping suite: 41 passed. Focused end-to-end/state/guard regression: 9 passed.
Tests cover SYN-205, arbitrary ticket text and custom owner through successful Create, empty parent,
missing date, metadata mismatch, stale custom-owner preview, stable correlation, and Offline output.
Initial new unit fixtures omitted required schema fields; corrected test setup without relaxing models.


Final acceptance: uv sync, Ruff check, Ruff format check, uv build and git diff --check passed.
Full suite: 545 passed in 91.87 seconds. Chrome desktop 1920 x 963 and narrow 390 x 844 verified
custom transcript, Round 2, Demo Architect, SYN-205 and human-edited Taylor Demo / Platform through
Preview, Confirm request, Create, and successful GET read-back (receipt 7001). The original reviewed
owner and ticket remain visible; simulated alias and parent ID are separately disclosed. No blank
page or framework exception. Console entries came only from the Grammarly extension, not the app.
The test tab was closed, temporary viewport reset, and port 8509 test server stopped. User page
and server on port 8501 were preserved. Browser used existing Chrome through the CUA runtime;
no extra Chrome session or external connection was introduced.

No remaining blocker. Alias mapping applies on the next rerun; no forced analysis reset or provider
identity change is necessary because extraction did not change. Exact preview maps are still bound
and stale confirmations are revoked. Offline remains local-only; production remains unavailable.
Lifecycle completed and active pointer cleared for the authorized commit/push on the current branch.
