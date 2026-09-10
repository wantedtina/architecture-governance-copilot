# Post-baseline refinement Batch 03 — pending review awareness and Markdown presentation

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R4`, `R6`

Approval boundary: The user accepted R1-R10 as future implementation intent, authorized sequential
planning after each verified batch, and explicitly approved this Batch 03 plan on 2026-09-10. Only
R4, R6, and the scope in this plan are authorized for implementation.

Baseline revision: `4a679d7bc4998ae7d23d28d9c13a9db83d804e5c`

Current phase: `COMPLETE`

## 1. Scope

Improve two closely related reading and editing surfaces without changing workflow boundaries:

1. Human Review shows restrained, live awareness of pending field changes, exclusions, and invalid
   in-progress values before confirmation.
2. Markdown-bearing drafting and review documents use purpose-labelled rendered, editable, and
   exact-source views while transcripts, evidence quotes, source code, logs, and machine payloads
   remain verbatim.

The complete confirmed before-and-after record remains on Generated Outputs. Pending indicators are
session-local editing aids only and never imply save, confirmation, publication, or approval.

## 2. Proposed product decisions requiring plan approval

Approval of this plan resolves the material open decisions in R4 and R6 as follows.

### Pending human-review changes

- Human Review displays one compact page-level `Pending human changes` summary above the review
  tabs. It reports modified fields, excluded items, affected sections, and validation issues.
- Tab labels retain proposal counts and append a concise pending count only when that collection has
  changes, for example `Actions · 2 · 1 pending`. The governance outcome reports through the
  page-level summary because it is outside the collection tabs.
- Each affected item remains fully visible and gains a text marker such as `Pending · 1 modified`
  or `Pending · Excluded`. Excluded items are not collapsed or hidden because their evidence must
  remain reviewable before confirmation.
- Individual native fields are not recolored and do not receive a badge on every keystroke. The
  item and page summaries provide accessible text rather than color-only meaning.
- Live comparison is tolerant and does not construct a `GovernanceResult`. Text uses the same
  strip/blank-to-`None` normalization as confirmed reconstruction; enum values compare by their
  stored value; a valid ISO date compares canonically; an invalid nonblank date is both a pending
  value and one validation issue.
- Restoring the analyzed value removes its pending marker on the next Streamlit rerun. Pending state
  is derived from the analyzed snapshot plus current widget values and is not a second mutable audit
  record.
- Pending edits continue to use the existing routed widget preservation. Navigating Back and Return
  does not confirm them, replace the analyzed result, or alter review-input manifest eligibility.

### Purpose-driven Markdown presentation

- Project Context presents the SI template and supporting-document Markdown as `Rendered` by
  default with a `Markdown source` tab. Repository excerpts remain verbatim source code and
  governance metadata remains structured UI.
- Draft Solution Intent source inputs follow the same policy for template/supporting Markdown;
  repository context remains code. The editable generated draft uses `Markdown editor` and
  `Rendered preview` tabs, with the editor first so the value being confirmed is unambiguous.
- After draft confirmation, the document switches to `Rendered` by default with `Markdown source`
  available for exact inspection and download. The source view is read-only after confirmation.
- Review Inputs presents the authoritative SI as `Rendered` by default and `Canonical Markdown
  source` second. Evidence locators bind to that canonical source. The current PoC does not expose
  raw Confluence storage representation because it is not retained as an application contract.
- Transcript intake stays editable plain text. Human Review evidence stays exact, read-only,
  line-wrapped verbatim text. Neither is interpreted as Markdown.
- Generated Review Record tabs are renamed to `Rendered` and `Markdown source`. ADO cards stay
  human-readable with exact JSON separate; request URLs and JSON Patch remain exact machine views.
- Long document previews use labelled, bordered, full-document regions without nested scrolling.
  This preserves browser search, keyboard navigation, and responsive behavior. A bounded scroll
  container is deferred unless later browser evidence shows a material usability problem.
- Rendered previews update on normal Streamlit reruns; no explicit preview-build action, cache, or
  asynchronous renderer is introduced.
- Markdown generators escape or safely delimit interpolated user/provider fields so a value cannot
  introduce an unintended heading, list, link, HTML block, or emphasis into generated documents.
  Exact original values remain available in editable fields, evidence/source views, and structured
  JSON. Intentional document Markdown from an authoritative SI/template is rendered as document
  content and is never treated as a generated structured field.

## 3. Explicit non-goals

- Do not implement R1 discovery, R3 fixture expansion, R7 delivery restructuring, or R9 deployment
  gating.
- Do not change workflow navigation, review-input manifest semantics, provider protocols, evidence
  validation, or publication safeguards established by Batch 02.
- Do not add autosave, persistence, version history, audit history, collaborative editing, rich-text
  authoring, Markdown libraries, databases, or authentication.
- Do not collapse excluded evidence, rewrite evidence quotes, render transcripts as Markdown, or
  expose raw Confluence storage markup.
- Do not add live enterprise connections, real credentials, or confidential data.

## 4. Dependencies and overlap boundaries

- R4 and R6 share the Human Review and generated-document presentation surfaces, so implementing
  them together avoids duplicate layout and browser-regression work.
- Batch 02 is a completed prerequisite: pending edits must survive its independent review routing,
  exact manifest, scoped reset, and invalidation behavior.
- R3 may later change collection sizes and empty states; pending summaries must derive from models
  and form schema rather than fixture-specific counts.
- R7 will reuse the safe rendered-versus-exact output policy but does not enter this batch.
- R1 affects drafting source acquisition, not how already acquired Markdown is presented.

No unresolved blocker remains if the user approves every decision in section 2. Any requested
change to those decisions must be incorporated before implementation begins.

## 5. Affected components and files

- `app.py` — document-view components, Human Review pending summary/tab/item markers, and explicit
  presentation labels.
- `src/architecture_governance_copilot/ui_support.py` — tolerant pending-change derivation and
  normalization helpers with no Streamlit dependency.
- `src/architecture_governance_copilot/minutes_generator.py` and `ado_generator.py` — safe Markdown
  composition for interpolated structured values if current output tests confirm exposure.
- `tests/test_app.py`, `tests/test_ui_support.py`, generator tests, and focused security/presentation
  tests.
- `README.md`, `SPEC.md`, and `DEMO.md` where current presentation or Human Review behavior changes.

No fixture update is planned.

## 6. Implementation sequence

- [x] Confirm Batch 02 is verified, committed, pushed, and no plan remains active.
- [x] Reconcile R4/R6 overlap and open decisions against current code, tests, and maintained docs.
- [x] Obtain explicit user approval of this execution plan and all section 2 decisions.
- [x] Mark this plan `IN_PROGRESS`, move R4/R6 to `In progress`, and record approval.
- [x] Add tolerant pending-change models/derivation and focused pure tests.
- [x] Add page, tab, and item pending indicators without changing evidence or confirmation state.
- [x] Add reusable labelled Markdown document views across drafting and review.
- [x] Harden generated Markdown interpolation while retaining exact source/evidence representations.
- [x] Synchronize maintained documentation and demo procedure.
- [x] Run focused and full automated verification plus the browser acceptance matrix.
- [x] Fix every in-scope failure before marking the batch verified.
- [x] On success, mark this plan `COMPLETED_VERIFIED`, set R4/R6 to `Verified`, clear the active
  pointer, commit, and push under the user's standing sequential-batch instruction.

## 7. Acceptance criteria

- Human Review immediately identifies pending modified fields, exclusions, affected collections,
  and invalid values without implying confirmation or persistence.
- Reverting to normalized analyzed values removes pending indicators.
- Invalid in-progress values remain editable, are distinguished from valid modifications, and
  cannot generate outputs.
- Pending edits and indicators survive routed Back/Return while the confirmed result and exact
  review-input manifest remain unchanged.
- SI/template/supporting-document views are rendered for reading and expose clearly labelled exact
  Markdown where useful; editable drafts clearly distinguish editor from preview.
- Authoritative SI remains read-only and its rendered view never obscures source identity or
  canonical evidence binding.
- Transcript and evidence fidelity remain verbatim; machine payloads retain exact JSON/code views.
- Generated Markdown cannot acquire unintended structure from interpolated fields, while exact
  original values remain traceable outside the rendered composition.
- Offline and Internal fake flows, human confirmation, evidence validation, scoped reset, guarded
  fake publication, and light-theme presentation remain intact.

## 8. Required verification

Automated commands from the repository root:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Focused tests must cover:

- unchanged, modified, excluded, reverted, blank optional, enum, valid-date, and invalid-date
  pending comparisons;
- pending counts by collection and page, item markers, tab labels, and routed persistence;
- confirmation producing the same normalized change summary shown as pending before submission;
- rendered/source/editor labels and read-only/editable contracts for each Markdown-bearing surface;
- literal treatment of transcript/evidence punctuation and malicious-looking structured values;
- unchanged deterministic output for ordinary fixture values and exact JSON/source traceability;
- Offline and Internal fake regressions through existing provider and publication boundaries.

Browser verification at a desktop viewport must complete:

1. drafting source Rendered/Markdown source views, draft editor/preview, and confirmed
   Rendered/source/download state;
2. authoritative SI Rendered/Canonical Markdown source views with source identity visible;
3. Human Review unchanged state, one modified field, one exclusion, an invalid date, revert, routed
   Back/Return persistence, confirmation, and matching Generated Outputs summary;
4. transcript and evidence punctuation displayed literally, plus Generated Review Record rendered
   and Markdown-source views;
5. Internal fake Generated Outputs and exact ADO JSON Patch confirmation/read-back regression;
6. desktop light-theme and narrow-viewport usability for every changed surface.

## 9. Compatibility, state, and rollback

- Pending-change state is derived rather than persisted, so no session-schema migration is planned.
- Existing review widget preservation remains the only routed edit store. Input changes still
  invalidate analysis and outputs according to the Batch 02 manifest contract.
- Presentation changes do not alter canonical SI, transcript, evidence, analyzed result, reviewed
  result, or publication request identity.
- Safe Markdown composition may intentionally change rendered escaping for adversarial structured
  values; ordinary fixture outputs must remain stable unless a documented escaping rule requires an
  exact test update.
- If verification fails, retain R4/R6 as `In progress`, keep this plan active, and record the exact
  failure. Do not hide pending changes, weaken validation, or fall back to unsafe rendering.

## 10. Progress

- [x] Accepted requirements and current implementation reconciled.
- [x] Proposed product decisions consolidated.
- [x] Sole active-plan pointer assigned for review.
- [x] User approval recorded.
- [x] Implementation complete.
- [x] Automated verification passed.
- [x] Browser verification passed.
- [x] Maintained documentation synchronized.
- [x] Completion record finalized and active pointer cleared.

## 11. Decisions and important discoveries

- Batch 02 completed at `4a679d7bc4998ae7d23d28d9c13a9db83d804e5c`; the working tree was clean
  when Batch 03 planning began.
- Human Review widgets rerun immediately and are already preserved across routed pages. Pending
  comparison can therefore remain a pure derived view and needs no autosave or new persistence.
- The confirmed `build_review_change_summary()` requires a valid reconstructed model and cannot
  represent an invalid in-progress date. Batch 03 needs a tolerant comparison that shares its
  normalization rules without weakening final Pydantic validation.
- The current source roles are already distinct: templates/supporting notes/authoritative SI are
  Markdown documents; repository excerpts, transcripts, evidence, request URLs, and JSON are exact
  text or machine data. The UI needs consistent purpose labels, not a universal Markdown renderer.
- The user explicitly approved this plan and every section 2 decision on 2026-09-10.
- Streamlit removes widget-owned keys when their routed page is absent. The existing durable review
  snapshot now explicitly retains those keys on Generated Outputs, and drafting source views keep
  their established widget identities, so routed preservation survives both presentation changes.
- Dynamic pending counts rebuild the tab group on a rerun and return selection to the first tab;
  affected collection labels still locate every change, while exact widget values remain preserved.

## 12. Actual verification evidence

Completed on 2026-09-10 from the repository root:

- focused Batch 03 regression: `109 passed` across UI support, Streamlit AppTest, minutes, and ADO
  generator tests;
- `uv sync` completed successfully;
- `uv run pytest`: `382 passed`;
- `uv run ruff check .`: passed;
- `uv run ruff format --check .`: 40 files already formatted;
- `uv build`: source distribution and wheel built successfully;
- `git diff --check`: passed;
- desktop browser: drafting source Rendered/source views, draft editor/preview, confirmed
  Rendered/source/download, authoritative SI Rendered/canonical source, unchanged/modified/invalid/
  reverted/routed pending states, confirmed output summary, and Generated Review Record tabs passed;
- browser exclusion regression: an excluded item remained visible with `Pending · Excluded ·
  Unconfirmed`, and its collection label showed one pending item;
- Internal fake browser regression: fake Confluence and AIF completed without network, exact JSON
  Patch required separate confirmation, one fake Create succeeded, and GET read-back verified receipt
  `7001`;
- narrow viewport: Project Context source tabs/full-document rendering, sticky confirmation, draft
  Markdown editor/preview, and stacked evidence/output cards remained usable without unintended
  nested document scrolling.

## 13. Remaining limitations and deferred work

- Drafting source discovery remains R1.
- The realistic Internal fake scenario remains R3.
- Governed Azure DevOps delivery restructuring remains R7.
- Deployment-controlled synthetic-mode visibility remains R9 and live-capability gated.
- Rich-text editing, raw Confluence storage inspection, autosave, durable audit history, and live
  enterprise adapters remain out of scope.

## 14. Final completion record

Completed and verified on 2026-09-10. R4 and R6 are `Verified`; the refinement register's active
execution-plan pointer and execution authority are both `NONE`. The implementation preserves the
deterministic offline path, explicit human confirmation, immutable evidence, provider boundaries,
and fake-only enterprise transports. No credential, confidential data, live connector, database,
authentication, or speculative later-batch scope was introduced.
