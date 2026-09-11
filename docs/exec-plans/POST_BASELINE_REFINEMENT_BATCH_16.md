# Batch 16 — Edited review inputs and visible operation feedback

Document status: `COMPLETED_VERIFIED`
Included refinements: R19, R20
Baseline: 388b1a7
Approval: User approved implementation of the preceding two-part proposal.

## Scope and sequence

1. Extend the existing offline extractor for valid metadata and changed transcripts. Preserve exact
   canonical results. Use literal line evidence, conservative lexical candidate grouping and an
   unclassified queue; do not infer approval, owners or dates. Verify provider and evidence tests.
2. Make shared operation errors persistently visible near workflow actions, with correction guidance
   and stale-error clearing. Inspect Context, Drafting, Review Inputs, Human Review and Delivery.
   Verify focused state and AppTests before full acceptance.
3. Synchronize current docs. Run uv sync, pytest, both Ruff checks, build and diff check.
4. Verify edited metadata/transcript through outputs and visible errors at desktop/narrow sizes in
   a real browser; close dedicated browser/server. Complete lifecycle and commit/push.

## Boundaries and compatibility

The SI remains the bundled authoritative snapshot. No real integration, extra mode, dependency,
model schema or fixture change. Internal fake remains fixed. Candidate categories are suggestions;
medium severity/priority are visibly disclosed review defaults, never inferred facts. Unmatched
lines remain quoted for manual classification. All resulting quotes pass existing evidence checks.
Input changes still revoke confirmation, analysis and outputs. No persistence migration.
Affected components: extractor and local rule helper, app feedback, ui_support state, tests and docs.
No unresolved product decisions or blockers.

## Progress

- [x] Extractor and focused evidence tests.
- [x] Feedback and focused UI/state tests.
- [x] Full repository and browser acceptance, cleanup.
- [x] Documentation, lifecycle and Git handoff.

## Discoveries, verification and completion

Historical fixed-source restrictions are superseded only for Offline transcript/metadata.

- Initial provider/evidence suite: 66 passed. Focused custom input and feedback checks: 8 passed.
- Additional shared Context/Drafting/Delivery error and correction checks: 3 passed.
- First full suite: 510 passed. Final acceptance pending after the additional shared feedback test.
- Bumped Offline provider configuration identity to v2 so old confirmations cannot authorize the
  changed extraction contract. Existing provenance invalidation handles this without migration.
- Metadata edits cover the editable round/date/architect/ticket fields; source-bound SI identity
  remains validated. Unclassified lines are explicitly labelled, never silent sample fallback.
- Delivery unknown/failed messages are visible for the selected action, with protected-operation
  guidance rather than an unconditional retry instruction.


## Browser acceptance

Actual Chromium via Playwright CLI in the dedicated agc-acceptance session, demo server port 8509.
At 1440x1000 and 390x844, edited transcript plus Domain Architect reached Human Review; source
quotes and the unclassified note remained visible. An invalid finding date produced a persistent
error within the viewport above the confirmation control without overlap. Correction removed the
error; explicit human confirmation reached Generated Outputs. Both screenshots inspected.
Browser and server closed; user sessions/services preserved. Artifacts remain outside Git in /tmp.
Automation initially used an incorrect textbox label, then encountered source-reload invalidation;
reloaded synthetic inputs and completed the full check against the final UI code successfully.

Additional delivery recovery checks: 12 passed. Selection clears obsolete feedback while retaining
publication history; protected operations keep their existing safeguards. No fixture changes.

## Final completion record

Completed 2026-09-11. Final repository suite: 512 passed in 61.35 seconds. uv sync, Ruff check,
Ruff format check, uv build and git diff --check passed. R19 and R20 Verified; active pointer
cleared. Existing branch retained for commit and push. Offline SI identity and Internal fake fixed
contracts remain bounded; general semantic analysis and live integrations remain deferred.
