# Batch 08 — Project Context acceptance corrections

Document status: `COMPLETED_VERIFIED`
Included refinement IDs: `R11`
Baseline revision: `4d8f22631492d207a7de03a2277e3dc91868c6a3`
Approval: The user explicitly approved repository selection and user-supplied evidence changes
and requested implementation and verification. The initial upload boundary is UTF-8 TXT/Markdown (1 MiB per item, 10 items),
using the stated default after the optional preference received no response.

## Scope and product behavior

- Keep governed template content and governance metadata read-only.
- Expose separate searchable repository and revision selection from synthetic inventory. The
  inventory contract supports multiple repositories without claiming live ADO permission checks.
- Evidence starts empty; users can add/edit/remove notes and uploaded text documents. Sample
  evidence is an explicit convenience, never automatically substituted for user content.
- Preserve evidence identity, user-entered/uploaded provenance, original upload fingerprint,
  current content fingerprint, and exact manifest binding. Normalize text deterministically.
- Validate file types, encoding, nonempty content, and bounded size; never execute uploaded content
  or use client filenames as filesystem paths. Initial formats are TXT and Markdown.
- The existing deterministic provider supports only its exact sample package. Validate eligibility
  separately from input validity and block unsupported generation without discarding custom input.
- Source changes revoke drafting confirmation and artifacts immediately, preserving independent
  review and publication history. Refresh must retain user evidence. Reset clears it.

## Non-goals and dependencies

No real ADO/Confluence connection, arbitrary semantic drafting, credentials, authentication,
database, or new specification framework. Preserve existing provider boundaries and offline demo.
R1/Batch 04 is historical; R11 corrects the acceptance gap without erasing that evidence.

## Components and sequence

1. Read current contracts; record scope and approval.
2. Extend selection/evidence support and provider eligibility; pass focused model/support tests.
3. Update Project Context widgets, provenance, and invalidation; pass AppTests.
4. Update README, SPEC, DEMO; run full repository checks and actual desktop/narrow browser flows.
5. Mark R11 Verified, plan COMPLETED_VERIFIED, clear active pointer, and record Git handoff.

## Verification and acceptance

Test multiple repository selection, unauthorized selection rejection, revision reset, editable
notes, upload validation and provenance, refresh/reset/navigation persistence, unsupported custom
input blocking, exact sample generation, independent review retention, and deployment guards.
Run uv sync, pytest, both Ruff checks, uv build, git diff --check. Verify browser desktop/narrow:
select repository, provide/edit/upload/remove evidence, inspect invalidation, restore exact sample,
confirm source package, generate and confirm draft. Inspect screenshots and runtime errors.

## Compatibility and rollback

Keep canonical fixture text and provider protocol unchanged. Migrate old fixed-evidence UI state
without silently treating fixture content as user-supplied. Roll back UI and evidence state together;
never discard publication facts or rewrite history.

## Progress

- [x] User authorization and current behavior reconciled.
- [x] File-format boundary resolved.
- [x] Support/provider tests passed (163 tests).
- [x] UI tests passed.
- [x] Full acceptance and browser checks passed.
- [x] Documentation and lifecycle synchronized.

## Discoveries and verification evidence

Current inventory model enforces exactly one repository, although R1 originally described selectable
repository discovery. Current readiness checks source IDs but does not validate exact deterministic
content until generation. Both need correction to make the accepted interaction truthful.

## Remaining limitations

Live permission discovery and arbitrary-input drafting remain unavailable. Uploaded data is
session-local; no durable store or enterprise verification is implied.

## Completion record

Completed on 2026-09-11. R11 is Verified and the active-plan pointer is NONE.

- `uv sync`: passed.
- `uv run pytest -q`: 495 passed.
- `uv run ruff check .`, `uv run ruff format --check .`: passed.
- `uv build`, `git diff --check`: passed.
- Actual Chromium via Playwright CLI, using the terminal fallback because the dedicated Browser
  plugin was unavailable. Fresh demo server at port 8507; desktop 1440x1000 and narrow 390x844.
- Verified repository dropdown, read-only template, empty evidence start, notes editing, refresh
  retention, deletion, Markdown upload, invalid UTF-8 rejection without partial mutation, custom
  package blocking, explicit sample restoration, source confirmation, generation, human draft
  confirmation, and confirmed Markdown download. Evidence edits revoked the prior confirmation.
- Inspected desktop/narrow screenshots; no horizontal overflow or application exceptions.
  Browser console contained only a local font-loading informational message.
- Focused AppTests additionally cover multiple synthetic repositories and revision reset. No live
  repository discovery was claimed; the bundled inventory still contains one repository.
- Fixed routed repository-widget retention and evidence-removal widget cleanup during verification.
  Keep the original inventory separate from the effective user-evidence package after confirmation.
- Browser scripts, uploads, screenshots, and downloaded artifacts remain outside the repository.
- Git handoff uses the existing branch `codex/final-stage-i2-review-summary`; no history rewrite.

