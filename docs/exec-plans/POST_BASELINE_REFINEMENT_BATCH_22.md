# Batch 22 — Delivery action feedback and attention guidance

Document status: `COMPLETED_VERIFIED`
Included refinement: R26
Baseline: ed1ad94
Approval: User requested the Delivery UX enhancement; no new delivery behavior is introduced.

## Scope, sequence and acceptance

1. Add one-shot session attention events for preview, confirmation and result. Clear on stale
   preview/selection changes. Consume once so ordinary reruns do not steal focus.
2. Render accessible named destinations and bounded static DOM focus/scroll using the installed
   Streamlit st.html API. Only allowlisted IDs and integer event tokens enter JavaScript; no user
   input is executable. Respect reduced-motion preference and provide persistent visible guidance.
3. Show prepared/not-sent, confirmed/not-sent and actual operation outcome distinctly. Failed or
   unknown submissions retain their existing correction/reconciliation rules; never imply success.
4. Test state lifecycle and actual UI outcomes, full repository checks, desktop/narrow Chrome
   focus and scroll transitions. Close dedicated test resources, update lifecycle, commit and push.

## Boundaries and dependencies

Affected: app.py, ui_support.py, a static focus helper and tests/docs. No dependencies, provider,
fixture, mapping, production or publication-contract changes. No persistent migration; attention
is ephemeral and never authority to send. Existing exact confirmation and duplicate guards remain.
No unresolved product decisions. Browser behavior must be verified, not inferred from unit tests.

## Progress and evidence

- [x] State and focus helper tests.
- [x] UI feedback and focused regression.
- [x] Full checks and desktop/narrow browser acceptance.
- [x] Cleanup, lifecycle and Git handoff.

## Completion

R26 verified. Active-plan pointer cleared; authorized Git handoff on the current branch.


Verification: focused state/feedback/protection tests 5 passed. Full suite 548 passed in 93.18
seconds. uv sync, Ruff check, Ruff format check, uv build and git diff --check passed. A missing
import in the new test was corrected before verification; application contracts were unchanged.
Chrome at 1920 x 963 and 390 x 844 verified Preview/Confirm/Create transitions. DOM focus reached
agc-delivery-preview (about 80px from viewport top), agc-delivery-confirmation (visible above the
floating action), and agc-delivery-result (about 80px from top). Repeated Preview revoked the old
confirmation and focused again. Actual fake Create produced verified receipt 7001. Screenshots
confirmed readable feedback and no overlay obstruction; console warnings/errors were empty.
The dedicated test tab and port 8509 server were closed, viewport reset, and user page preserved.

No remaining blockers. Smooth scrolling is browser-dependent; persistent inline/floating text also
explains state. The bounded focus script only accepts internal IDs and numeric tokens, does not
fetch external code, and never consumes user content as JavaScript. No provider or production change.
