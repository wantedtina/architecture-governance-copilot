# Batch 18 — Non-production reviewer outcome selection

Document status: `COMPLETED_VERIFIED`
Included refinement: R22
Baseline: 2e10d84
Approval: User approved free human outcome selection and clarified demo/development-only feedback.

## Scope and sequence

1. Audit deployment policy, route guards and maintained docs. Keep production synthetic denial;
   do not infer future production behavior from current manual acceptance.
2. Separate non-production human-reviewed outcome provenance from strict provider result validation.
   Allow every outcome without transcript evidence after human editing, explicitly record
   Reviewer-selected and before/after values, retain optional read-only source references.
3. Test all outcomes, provider rejection of human provenance, explicit production denial and
   existing routing/invalidation. Run full repository checks and desktop/narrow browser acceptance.
4. Close dedicated browser/server, synchronize lifecycle, commit and push the existing branch.

## Boundaries and compatibility

Production is unavailable pending internal integration and R9b acceptance. Demo, development and
test may use the new human-review policy. Internal fake input contracts stay fixed; no live API,
authentication, database or provider fallback. A distinct reviewed-result subtype records human
provenance; provider GovernanceResult validation remains strict. New policy is opt-in at the UI
reconstruction boundary; default reconstruction retains prior strict behavior. No stored-state
migration. Existing source fingerprints and protected delivery operations remain authoritative.
Affected: models, policy, evidence validation, UI/state, output provenance, tests and current docs.
No unresolved product decisions or blockers.

## Progress and evidence

- [x] Policy/provenance implementation and focused tests.
- [x] Full checks and browser acceptance.
- [x] Cleanup, documentation and Git handoff.

## Completion

Completed 2026-09-11. Production product semantics remain deferred; this batch is not production acceptance.

Audit: production policy exposes no review modes, disallows drafting, rejects fake enablement and
blocks direct/stale routed sessions. Existing R9b remains deferred. AGENTS, register, README, SPEC,
DEMO and internal handoff explicitly separate current synthetic acceptance from future production.

Focused outcome/production tests: 23 passed before expanding the all-outcome matrix to both demo
and development. Full regression initially exposed three object-identity contract failures from
reconstructing provider responses during validation; validation now preserves the original object.
Five focused delegation/provider guard checks passed. Final full suite: 527 passed in 75.25 seconds.
uv sync, Ruff checks, build and diff check passed. Browser acceptance in progress.

## Browser and completion record

Actual Chromium, one agc-acceptance session. Demo port 8509: Approved at 1440x1000 and Rejected at
390x844 both confirmed without selected evidence, generated outputs and retained Reviewer-selected
provenance. Screenshots inspected, including reference-only evidence and enabled confirmation.
Native combobox automation required waiting between search, arrow and Enter to commit the selection.
Production port 8510: home, /human-review and /work-item-delivery all showed unavailable capability
and exposed no outcome or confirmation controls. Route bootstrap emitted local nested health/config
404 probes before rendering the blocked page; no workflow was exposed and no external provider ran.
These checks verify denial only, not production integration or product acceptance.

Both dedicated servers and the browser closed. Artifacts remain in /tmp; user sessions preserved.
R22 Verified; active pointer cleared. All 527 tests, uv sync, Ruff, build and diff check passed.
Existing branch retained for commit/push. R9b and future production outcome semantics remain deferred.
