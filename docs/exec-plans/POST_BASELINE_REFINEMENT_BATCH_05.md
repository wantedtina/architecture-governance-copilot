# Post-baseline refinement Batch 05 — realistic Internal fake review scenario

Document status: `COMPLETED_VERIFIED`

Included refinement IDs: `R3`

Approval boundary: The user accepted R1-R10 as future implementation intent, authorized sequential
planning after each verified batch, and explicitly approved this plan and every product decision in
section 2 on 2026-09-11.

Baseline revision: `33aa7dd90cc27da95d2f6439f2879f7b4745001d`

Current phase: `COMPLETE`

## 1. Scope

Replace the contract-minimal primary Internal fake package with a coherent, realistic synthetic
architecture review while preserving the existing fake Confluence, fake AIF, and fake Azure DevOps
boundaries:

1. expand the distinct `Synthetic Order Routing Service` Solution Intent and its canonical fake
   Confluence storage response;
2. provide a credible multi-participant review transcript and synchronized metadata;
3. expand the structured fake AIF result with fully grounded, representative governance items;
4. retain a small dedicated contract fixture for boundary and empty-state tests; and
5. verify the complete Internal fake workflow without changing its explicit opt-in, no-network, or
   mandatory-human-review behavior.

## 2. Proposed product decisions requiring plan approval

Approval of this plan resolves every material open decision currently recorded for R3 as follows.

### Scenario identity and depth

- Retain and expand `Synthetic Order Routing Service`. It remains clearly distinct from the
  bundled `Digital Payment Notification Service` offline scenario and therefore continues to prove
  that the fake integration path does not reuse the deterministic offline extractor package.
- Keep the existing synthetic Confluence page ID, space, governance ticket, and version lineage,
  but advance the SI version and page version together to identify the expanded reviewed snapshot.
- Target approximately 900–1,300 SI words across context, scope, architecture, routing and data,
  resilience, security, observability, deployment, operations, and explicit open-assumption
  sections. This is substantial enough for evidence review without duplicating the longer offline
  scenario or overloading the demonstration.
- Target 24–32 timestamped transcript lines across four fictional roles: Domain Architect,
  Solution Architect, Service Owner, and Reliability Engineer. Every speaker, date, identifier,
  and technical fact remains visibly synthetic.

### Representative governance result

- The primary Internal fake result will contain three findings, one decision, one risk, two action
  items, one open question, and two missing-evidence items. Every review collection is intentionally
  nonempty in the main demo so Human Review, evidence traceability, pending edits, exclusions, and
  generated outputs can all be demonstrated without manufacturing excessive item counts.
- Keep `changes_requested` as the review outcome and ground it in an exact transcript quote.
- Every substantive claim, owner, due date, SI section, speaker, and timestamp must be supported by
  an exact unique source quote. The fake AIF response may propose only facts present in the
  canonical SI or transcript; trusted references remain assigned locally after validation.
- Use at least two action owners only if both are explicitly assigned in the transcript. Add only
  the corresponding fictional `.invalid` identities to the existing fake Azure DevOps target so
  the current guarded publication regression remains demonstrable.
- Do not force ordinary discussion into a governance item. Add focused negative assertions for at
  least two discussed details that the expected result deliberately does not promote.

### Fixture separation and synchronization

- Preserve the current small successful AIF example as a test-only contract fixture under
  `tests/fixtures/`. Keep zero-item and malformed responses as dedicated test cases rather than
  exposing an intentionally sparse result as the primary demo.
- The primary runtime continues to load only the `samples/internal_fake_*` package. Test-only
  fixtures must never be selectable from the UI or loaded by the production runtime.
- Treat the canonical Markdown SI as the expected human-readable source and the Confluence storage
  body as its fake API representation. Add a synchronization assertion that canonicalizing the
  storage response yields the committed Markdown snapshot exactly.
- Validate the primary package as one contract: metadata equality, page and SI version alignment,
  transcript shape, expected item counts, exact evidence locators, owner/date support, synthetic
  safety, and deterministic runtime wiring.

## 3. Explicit non-goals

- Do not add live Confluence, Teams, AIF/LLM, Azure DevOps, repository, identity, or network access.
- Do not add credentials, authentication, databases, RAG, agents, uploads, or external data.
- Do not change the fake provider protocols, review-input manifest contract, mandatory Human Review
  boundary, exact publication-preview confirmation, or at-most-once fake delivery semantics.
- Do not implement R7 delivery queues, cross-item mapping controls, bulk publication, or recovery
  redesign.
- Do not change the offline drafting or review fixtures merely to make both scenarios resemble one
  another.
- Do not claim that fixture depth demonstrates general semantic extraction or a production-ready
  enterprise integration.

## 4. Dependencies and overlap boundaries

- Batch 02 is a completed prerequisite: the Internal fake scenario uses the independent Review a
  Solution Intent workflow and its authoritative SI input manifest.
- Batch 03 is a completed prerequisite: the richer Markdown SI and review content reuse the
  rendered-versus-exact presentation and pending-change behavior.
- Batch 04 is independent: the drafting source-package inventory and confirmation remain unchanged.
- R7 may later restructure delivery. This batch updates only the minimum fictional identity mapping
  needed to keep the current single-action fake publication path valid for the richer result.
- R9 remains readiness-gated and receives no live capability from this batch.

No unresolved blocker remains if the user approves every decision in section 2. Any requested
change to scenario identity, size, collection counts, participant roles, or fixture separation must
be incorporated before implementation begins.

## 5. Affected components and files

- `samples/internal_fake_solution_intent.md` — expanded canonical synthetic SI.
- `samples/internal_fake_confluence_page.json` — synchronized fake Content API storage response and
  version metadata.
- `samples/internal_fake_review_transcript.txt` — expanded timestamped synthetic review.
- `samples/internal_fake_review_metadata.json` — synchronized snapshot and round metadata.
- `samples/internal_fake_aif_result.json` — representative, evidence-grounded structured result.
- `tests/fixtures/` — preserved minimal successful AIF contract package.
- `src/architecture_governance_copilot/runtime_dependencies.py` — only fictional fake-delivery owner
  mappings required by explicitly assigned actions, if needed.
- `tests/test_sample_data.py`, `tests/test_runtime_dependencies.py`,
  `tests/test_aif_integration.py`, and focused UI/application tests — package synchronization,
  contract, count, evidence, runtime, and rendered-workflow regression coverage.
- `README.md`, `SPEC.md`, and `DEMO.md` — synchronized scenario description and demonstration facts.

No application-layout or provider-protocol change is planned. If fixture depth exposes a genuine UI
defect, record it before making a bounded fix and keep it within the existing review workflow.

## 6. Implementation sequence

- [x] Confirm Batch 04 is verified, committed, pushed, and no plan remains active.
- [x] Reconcile R3 decisions with the current fixtures, runtime wiring, provider boundaries, UI,
  tests, and maintained documentation.
- [x] Create this sole proposed plan and move R3 to `Ready` without treating it as implementation
  authorization.
- [x] Obtain explicit user approval of this execution plan and every section 2 decision.
- [x] Mark this plan `IN_PROGRESS`, move R3 to `In progress`, and record approval.
- [x] Preserve the current small successful response as a test-only contract fixture.
- [x] Expand and synchronize the primary SI, fake Confluence response, transcript, metadata, and
  fake AIF result.
- [x] Add package-level consistency, evidence, safety, runtime, and regression tests.
- [x] Synchronize maintained documentation and demo instructions.
- [x] Run focused and full automated verification plus the browser acceptance matrix.
- [x] Fix every in-scope failure before marking the batch verified.
- [x] On success, mark this plan `COMPLETED_VERIFIED`, set R3 to `Verified`, clear the active
  pointer, commit, and push under the user's standing sequential-batch instruction.

## 7. Acceptance criteria

- Internal fake remains hidden unless explicitly enabled and performs no network request.
- The primary fake Confluence snapshot canonicalizes exactly to the expanded committed Markdown SI,
  with synchronized project, title, SI version, page version, and governance ticket identity.
- The primary transcript contains 24–32 uniquely locatable timestamped lines across the four
  approved fictional roles.
- The validated fake AIF result contains exactly three findings, one decision, one risk, two
  actions, one open question, and two missing-evidence items, plus supported outcome evidence.
- Every evidence quote exists in the correct canonical source with accurate SI section or transcript
  speaker/timestamp locators; locally assigned trusted references contain no provider references.
- Every populated action owner and due date is stated explicitly in transcript evidence and every
  publishable action owner has a fictional `.invalid` fake-target identity.
- The minimal success case, zero-item response, invalid response, context mismatch, unsupported
  evidence, refusal, timeout, and provider failure remain covered without driving the primary demo.
- The complete Internal fake flow supports source loading, input confirmation, fake AIF analysis,
  pending Human Review edits/exclusions, reviewed-record confirmation, outputs, exact fake
  publication preview, one guarded submission, and deterministic read-back.
- Offline drafting and review behavior remain unchanged and pass regression verification.
- All maintained product descriptions state accurately that the scenario is synthetic,
  deterministic, provider-shaped, and not general semantic extraction or live integration.

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

- primary package parsing, strict model validation, exact item counts, version and identity
  consistency, and canonical Markdown/storage equivalence;
- exact evidence quote, SI-section, speaker, timestamp, owner, and due-date support;
- unique local reference assignment and rejection of unsupported or ambiguous evidence;
- transcript length and role coverage plus an explicit assertion that ordinary discussion is not
  promoted;
- synthetic-only safety checks, absent credentials, and no production-like endpoint or identity;
- runtime isolation from the offline path and from test-only minimal fixtures;
- unchanged provider protocols, review manifest binding, invalidation, human confirmation, and fake
  delivery guardrails.

Browser verification at desktop and narrow viewports must complete:

1. enable Internal fake explicitly and load the fake Confluence SI, transcript, and metadata in a
   non-default order;
2. inspect the richer rendered SI, exact canonical source, snapshot identity, transcript,
   provenance, and confirmed manifest;
3. analyze with fake AIF and inspect every nonempty Human Review collection plus source evidence;
4. make and restore a pending edit, exclude and restore one proposed item, then confirm the reviewed
   record and inspect the confirmed change summary;
5. prepare and confirm one exact fake Azure DevOps preview, submit once, and verify the deterministic
   receipt and read-back without a network request;
6. switch to Offline review and verify its independent input/result package remains unchanged;
7. verify keyboard-accessible controls, readable long content, light-only styling, and no horizontal
   overflow at a narrow viewport.

## 9. Compatibility, state, and rollback

- Existing session-state and manifest schemas remain unchanged. The expanded source fingerprints
  intentionally differ from Batch 04 and will invalidate any stale Internal fake analysis created
  from the old package.
- Page and SI versions advance together; the page ID and governance ticket remain stable fictional
  identifiers so fake delivery parent mapping remains deterministic.
- The fake AIF result stays behind `GovernanceExtractor`, and source acquisition stays behind the
  existing Confluence reader boundary. No UI code may deserialize provider output directly.
- Rollback consists of reverting the synchronized primary fixture package, matching test
  expectations, any added fictional fake-target identity mappings, and maintained documentation as
  one unit. Never roll back only one source representation.
- If verification fails, retain R3 as `In progress`, keep this plan active, and record the exact
  failure. Do not weaken evidence validation, reduce human confirmation, or substitute the offline
  expected result.

## 10. Progress

- [x] Accepted requirement and current implementation reconciled.
- [x] Proposed product decisions consolidated.
- [x] Sole active-plan pointer assigned for review.
- [x] User approval recorded.
- [x] Primary and minimal fixture packages separated.
- [x] Realistic primary package synchronized.
- [x] Automated verification passed.
- [x] Browser verification passed.
- [x] Maintained documentation synchronized.
- [x] Completion record finalized and active pointer cleared.

## 11. Decisions and important discoveries

- Batch 04 completed at `33aa7dd90cc27da95d2f6439f2879f7b4745001d`; the working tree was clean
  and local HEAD matched the remote branch when Batch 05 planning began.
- The current primary Internal fake package contains a 66-word, two-section SI, three transcript
  lines, one finding, one action, one missing-evidence item, and four empty result collections.
- The current fake Confluence Content API response and Markdown SI represent the same small content
  manually. A direct canonical-equivalence test is missing and is required before expanding both.
- Runtime construction already keeps Internal fake sources lazy, opt-in, separate from Offline mode,
  and behind the existing Confluence and AIF boundaries.
- Zero-item, malformed, context-mismatch, unsupported-evidence, refusal, timeout, and provider-
  failure cases already have dedicated AIF contract tests. The successful minimal case is the only
  small package that needs explicit preservation when the primary sample expands.
- The user explicitly approved this plan and every section 2 decision on 2026-09-11.
- The expanded primary package contains a 1,083-word SI and 28 transcript lines across the four
  approved fictional roles. Its result contains the exact 3/1/1/2/1/2 collection counts approved
  in section 2.
- An already-running Streamlit test process reloaded fixture files but retained its imported Python
  owner mapping. A deliberate cold restart loaded the synchronized mapping and the guarded
  publication flow passed; this is normal process-reload behavior rather than a product fallback.

## 12. Actual verification evidence

- Focused Internal fake package, AIF, runtime, and application verification passed: 57 tests.
- Full automated verification passed: 400 tests in 24.45 seconds before the final format-only
  adjustment; the final repository command matrix repeated the full suite successfully.
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed with 41 files already formatted.
- `git diff --check` passed.
- Package assertions confirmed 1,083 SI words, 28 transcript lines, four exact fictional roles,
  exact 3/1/1/2/1/2 review collection counts, and canonical equality between the fake Confluence
  storage body and the committed Markdown SI.
- Desktop Chrome verification loaded Internal fake components in a non-default order, displayed
  page version 8 and the full rendered SI, confirmed the exact manifest, and analyzed all nonempty
  Human Review collections with no automatic output generation.
- Browser interaction verification created and restored one pending field edit, excluded and
  restored one decision with its pending marker, and confirmed a clean reviewed record.
- Cold-start browser verification generated two mapped work-item previews, prepared and separately
  confirmed one exact Create request, submitted once to the in-memory fake gateway, and verified
  receipt `7001` through GET read-back with explicit no-network disclosure.
- Switching to Offline review produced the unchanged Digital Payment Notification Service result
  with 3/1/1/2/1/2 collection counts and no Fake AIF claim.
- Narrow Chrome verification at 390 by 844 pixels retained accessible controls and readable stacked
  content after using the standard responsive sidebar control, with no horizontal overflow
  (`scrollWidth` equaled `innerWidth`).
- A fresh post-restart browser tab had the correct title, meaningful content, no framework overlay,
  and no console warnings or errors. Earlier WebSocket/route logs were attributable to the
  deliberate server restart and were absent from the fresh tab.

## 13. Remaining limitations and deferred work

- The richer response remains a fixed fake AIF result for one exact synthetic package. It does not
  support arbitrary SI or transcript content.
- Internal fake mode remains local and opt-in. It proves contracts and review controls, not live
  enterprise connectivity, authentication, authorization, or provider quality.
- R7 delivery-queue and mapping decisions remain deferred to Candidate 06.
- R9 deployment policy remains readiness-gated until live capabilities and release authority are
  separately approved.

## 14. Final completion record

Completed and verified on 2026-09-11. R3 is verified, the active-plan pointer is cleared, and the
remaining limitations in section 13 remain outside this batch. Commit and push follow this
completion record under the user's standing sequential-batch authorization.
