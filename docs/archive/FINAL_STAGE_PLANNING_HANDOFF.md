# Final-stage planning handoff

Updated: 2026-09-07

Repository: `/Users/wantedtina/Repos/architecture-governance-copilot`

Inspected baseline: `main`, `56cee29`.

## 1. Current status, authorization, and language policy

This is a planning handoff, not an implementation handoff.

- The user confirmed separating development from presentation/demo planning and authorized
  documentation updates.
- Implementation details remain open for revision. This request does not authorize application
  development, enterprise writes, or media production.
- Specific demo owner changes and finding exclusions remain candidates; silence is not approval.
- Prefer Chinese for session communication with the user. Use English everywhere else, including
  files, plans, code comments, UI text, commit messages, PR text, presentation/demo materials, and
  deliverables. This standing requirement is recorded in AGENTS.md and applies across sessions
  without asking the user to repeat it.
- Check AGENTS.md and current Git status before continuing.

## 2. Current documents and responsibilities

- [Implementation Plan](../FINAL_STAGE_IMPLEMENTATION_PLAN.md): engineering scope, steps, boundaries,
  tests, risks, internal integration, release gates, and code freeze. This is the maintenance
  location for engineering requirements.
- [Presentation and Demo Plan](../FINAL_STAGE_PRESENTATION_DEMO_PLAN.md): complete feedback
  transcription, holistic interpretation, demo values/actions, narrative, materials, timing,
  rehearsal, fallbacks, and materials freeze.
- [Original plan entry](../FINAL_STAGE_DEVELOPMENT_PLAN.md): navigation only, not a third plan.

The user wants to focus on development first and presentation/demo preparation in the final days
before the event. Retain 18 September for code freeze, 19–21 September for presentation preparation
and rehearsal, and 22–24 September for the event. Materials freeze separately after a successful
final rehearsal and before the event; the exact time remains unconfirmed. Conduct a lightweight
pre-freeze demonstrability check to avoid discovering readability or interaction defects too late.

## 3. Retained requirements

- Preserve the deterministic offline path, five stages, Existing SI shortcut, provider protocols,
  and analysis/generation separation.
- Human Review is mandatory and evidence is read-only. Provider output or human confirmation does
  not represent formal architecture approval.
- Show an owner edit, finding exclusion, input invalidation, and the source quote → reviewed record
  → minutes → ADO chain.
- A compact current-session change summary and SourceEvidence.reference display are selected scope.
- Do not add reviewer notes/identity/history, a second evidence-ID schema, or additional bundled
  presentation scenarios.
- Company-specific AIF/Confluence/ADO transport and authentication stay internal. Externally provide
  protocols, strict boundary models, fake adapters, pure payload builders, tests, searchable TODOs,
  and a future internal integration handoff.
- The primary internal path is Confluence GET → AIF analysis → Human Review → ADO Create, with
  separate publication confirmation.
- ADO Update and dedicated synthetic Confluence review-page write-back are gated; never overwrite
  the source SI.
- Teams/Graph, RAG, agent frameworks, databases, and automatic approval remain excluded.
- Use dependency-driven sequencing and release gates, not day-by-day development scheduling.
- The user reports that an internal AIF endpoint will be provided and that Confluence/ADO GET/POST
  access has been tested internally. These facts do not mean the application is integrated or
  that its complete live gate has passed.

## 4. Independent takeover inspection and corrections

The takeover inspected AGENTS.md, README, SPEC, DEMO, pyproject.toml, complete app.py, all production
modules, five route entries, relevant tests, all samples, the complete previous plan and handoff,
and recent Git history. At takeover there were only two untracked planning files and no tracked
implementation changes.

Corrections are documented in the revised drafts; documenting them does not implement them:

- The actual finding is Undefined production support ownership.
- The first action has only transcript evidence, with reference transcript-line-15. Do not infer
  its SI section from a related finding.
- Model validation does not replace runtime source validation. Preserve optional locators and
  permitted missing-evidence contracts.
- A matching quote does not prove claim semantics. Do not automatically convert unsupported claims
  to Missing Information.
- Restoring an input's original value still requires reanalysis; use persistent invalidation
  rather than only comparing current fingerprints.
- Remove output generation's dependency on reconstructing a deterministic fixture extractor.
- Compare normalized review values paired by original position; map outputs using reviewed action indices.
- Do not directly reuse mock descriptions containing no-item-created statements in live ADO payloads.
- Revoking current publication eligibility must not erase knowledge of completed or unknown remote
  operations. Reset/restart requires reliable reconciliation, not claims of cross-client exactly-once
  based on session receipts.
- Internal mode requires explicit transcript/metadata input, not unrelated bundled companions.
- The primary scope is AIF analysis, not AIF drafting.
- The previous proposal to treat unmodified demo values as approved no longer applies.

## 5. Outstanding inputs and their timing

**Before development:** Explicit user approval of implementation scope and authorization to develop.

**Before each internal adapter:** Confluence product/body/page/space/permissions and canonicalization;
AIF request/response/deployment/authentication/runtime constraints; ADO test targets, field/identity/
parent/path/tag/notification mappings, evidence/correlation destination, and reconciliation. Provide
these details internally; they do not block external fakes. Secondary writes also require specific
targets and a decision to include them.

**Before presentation materials are finalized:** Confirm whether to use Alex Chen → Taylor Kim and
exclude the actual production-support finding; confirm duration, deliverable formats, and materials
freeze time. These do not block generic implementation.

Choose live/offline based on validation gates rather than promising live in advance. If the live
gate has not passed by code freeze, use the offline demonstration and retain completed external
preparation work.

## 6. Verification and continuation notes

- This revision changes planning documents and the AGENTS.md language policy only. No application
  implementation was performed; pytest, uv sync, and build were not run.
- git diff --check passed at takeover. Historical 251 passing tests and Ruff results are background
  only; rerun verification when development begins.
- docs/INTERNAL_INTEGRATION_HANDOFF.md remains a planned development deliverable and does not yet exist.
- docs/CODEX_HANDOFF.md and July presentation materials are historical context, not replacements
  for the two current plans.
- Future Streamlit implementation must follow the repository skill and AGENTS.md; keep shared state
  in ui_support.py.
- Planning files are currently untracked. Inspect the working tree before further work; do not
  automatically commit or expand documentation authorization into code authorization.
- Complete feedback transcription is retained in the presentation plan. The original screenshot
  was not rechecked in this revision. Do not broadly distribute confidential invitation screenshots.

## 7. Confluence API sample follow-up

Two initial screenshot examples demonstrate collection lookup by space/title and direct lookup
by page ID, with metadata/version information but no expanded body; they use different pages.
A follow-up `GET /rest/api/content/{page_id}?expand=body.storage,version,space` demonstrates a
nonempty paragraph in `body.storage.value`, `representation=storage`, and `version.number` in
the same response. Basic body expansion is verified for this internal sample. This does not
establish completed application integration or API write support. No internal host, identifier,
user information, credential, cookie, or screenshot has been copied into the planning documents.

Implementation Plan Section I6.1 records the observed structures, optional discovery versus
primary page-ID retrieval, strict snapshot mapping, body/version binding, canonicalization limits,
and fake/internal acceptance cases. No further screenshot is required for planning. HTTP status
and Content-Type handling, structured body conversion, version-change invalidation, deployment
edition/version, minimum authentication, and end-to-end adapter acceptance remain internal
implementation-time checks. The sample only demonstrates paragraph content; it does not validate
headings, lists, tables, macros, or authentication without cookies.

## 8. ADO Create API sample follow-up

The user reports successful internal ticket creation with an account-generated token. Section
I7.1 records the POST/JSON Patch structure, configurable process-specific type and field mapping,
and receipt ID/revision/API URL/browser URL contract. The supplied request and response titles
slightly differ, and the request's classification field is absent from visible response fields;
exact pairing and field persistence remain unverified. Bearer Authorization and cookies appear
together, so token type and cookie-free authentication must be verified internally. No secrets,
identities, actual targets, or internal classification configuration were copied into these files.

Planning can continue with these observations. Prefer GET verification of the existing synthetic
item over another Create merely to resolve sample differences. Preserve known created IDs on
read-back failure or mismatch and block duplicate creation pending reconciliation. Exact mapped
payload acceptance and the full human-confirmed live path remain implementation-time checks.
