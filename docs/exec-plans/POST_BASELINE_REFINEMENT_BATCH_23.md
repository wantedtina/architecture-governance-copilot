# Batch 23 — Explicit new Internal fake demo run

Document status: `COMPLETED_VERIFIED`
Included refinement: R27
Baseline: 323b24b
Approval: User explicitly approved the new-run proposal and its reset distinction.

## Scope and sequence

1. Add a pure, policy-guarded new-run reset: only development/test Internal fake and known local
   fake gateway instances. Clear review input/analysis/output/preview/selection/attention state,
   publication operations/history and gateway, preserving drafting and current Internal fake mode.
2. Expose Start new demo run across review stages with a popover describing exact cleanup and
   a separate confirmation button. Explain that ordinary Reset review retains delivery history.
3. Verify same-run duplicate prevention, normal Reset preservation, new-run Create without process
   restart, cleared uncertain fake results, preserved drafting, unavailable modes and UI cancellation.
4. Run full repository checks and desktop/narrow Chrome acceptance, close dedicated test resources,
   complete lifecycle, commit and push the existing branch.

## Dependencies, acceptance and boundaries

Affected: ui_support.py, app.py, focused tests and maintained docs. No provider, fixture, dependency,
real service, production or generic publication change. Empty review state returns to Review Inputs
in Internal fake. A new run needs fresh input and human confirmations; no auto-submit or auto-load.
No persistent migration. Old simulated records are intentionally discarded only by the explicit
new-run action; ordinary resets retain them. No unresolved product decisions.

## Progress and evidence

- [x] Pure guarded reset and focused tests.
- [x] UI scope confirmation and end-to-end tests.
- [x] Full checks and desktop/narrow browser acceptance.
- [x] Dedicated browser tabs and test server closed; lifecycle completed. Git handoff follows this record.

## Completion

Completed and verified. This operation affects only the current session's in-memory simulation.

Focused checks: 12 passed, including success/unknown fake results followed by a new run and a
second Create in the same process, ordinary reset protection, preserved drafting, mode/gateway
denial and no mutation from simply rendering the confirmation control.

Full checks: `uv sync`, `uv run pytest -q` (558 passed), `uv run ruff check .`,
`uv run ruff format --check .`, `uv build` and `git diff --check` passed.

Real Chrome acceptance reused the existing browser with dedicated temporary tabs and a local
Streamlit server on port 8509. Desktop and 390-by-844 narrow-screen checks verified the cleanup
scope and confirmation, dismissal without mutation, empty Internal fake inputs after reset, and
two successful Create/GET read-back cycles in the same process. Preview remained disabled after
each successful delivery within its run. The second run required fresh input and human confirmation.

Two download-source 404 console messages occurred during an earlier rapid output-page transition.
A separate stable output-page check clicked both Markdown and JSON download controls with no
warning/error console entries; the messages did not recur. This does not establish their root cause.
Dedicated test tabs and the port-8509 server were closed; the user's port-8501 session was preserved.
