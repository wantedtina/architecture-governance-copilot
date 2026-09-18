# Batch 24 — Finding/action candidates and human-completed review results

Document status: `IN_PROGRESS`
Included refinement: R28
Prepared: 2026-09-18
Revision: Post-probe plan review, 2026-09-18
Baseline revision: `67a60da` on `main`, tracking `origin/main`
Approval: The user explicitly authorized implementation on 2026-09-18 after reviewing the
updated plan and reaffirming the integration/demo objective. R28 is now `In progress`.
Implementation, verification, commit, and push are authorized within this bounded plan.

The refinement register owns the sole active-plan pointer. This proposal does not reopen the
agreed one-call, two-category design or authorize live integration.

Primary objective: reduce the work and uncertainty for OpenCode with GPT-5.4 to integrate the
internal AIF call behind the app's Analyze Review button, enabling the complete final hackathon
demo as soon as practical while preserving its end-to-end coherence. Every change must directly
support that integration, the required human-review safeguards, or the complete demonstration.
Do not optimize for a general integration framework or an isolated successful endpoint probe.

## 1. Inspected baseline and preservation

- `GovernanceExtractor.extract()` and `GovernanceReviewService.analyze_review()` currently return
  `GovernanceResult`. `EvidenceValidatingExtractor` assumes that complete domain type.
- Local `AifGovernanceExtractor.extract()` already calls `AifTransport.analyze()` once, with full
  SI, transcript, context, provider identity, and source fingerprints. It requests the full domain
  schema, validates model-supplied evidence, and then assigns trusted references.
- This checkout has no real AIF HTTP transport, six-stage extractor, or request-time source-ID
  index. Internal implementation details must be inspected in the internal repository later.
- `DeterministicDemoExtractor`, `SyntheticReviewResponder`, and `group_transcript_candidates()`
  currently return complete six-category results. Edited-input grouping supplies business defaults
  and places unmatched text in `missing_evidence`.
- Human Review state, route eligibility, comparisons, and draft reconstruction depend on
  `GovernanceResult`. Existing finding status defaults to Open; candidate review must not inherit it.
- Delivery reconciliation currently maps retained actions to their original action-list indices.
  A mixed candidate list with reclassification requires explicit stable identity mapping.
- Minutes currently render empty categories as `None recorded.`; that is unsuitable for categories
  excluded from the new extraction scope.
- Preserve these existing untracked user files byte-for-byte and exclude them from task commits:
  `docs/AIF_INTEGRATION_HANDOFF.md`, `docs/AIF_TOOL_CALL_GOLDEN_FIXTURE.md`,
  `docs/CODEX_CONTINUATION_PROMPT.md`, and `docs/HOW_TO_HANDOFF_TO_CODEX.md`.
  Their historical observations are context, not the new target contract or evidence of local code.
- Leave other worktrees, tracked media, and unrelated changes untouched. After approval, create
  `codex/analyze-review-candidates` from the inspected baseline in this checkout. Reinspect status
  before branching; if the baseline has changed, reconcile the plan against actual changes first.

### 1.1 New evidence and its limits

The user reported a real internal AIF call using the supplied full-input Postman request and shared
response photographs. The visible response contains one `emit_review_candidates` tool call,
`finish_reason: tool_calls`, five findings and two actions, and 6,266 input / 766 output tokens.
The visible source IDs exist in the supplied request. Two findings describe items explicitly
classified as Missing Evidence in the transcript; both action dates are reduced to `the proposed
date`. This supports candidate-contract feasibility for one example, not semantic or end-to-end
acceptance. No raw response, exact transmitted-request capture, HTTP status, or elapsed-time
evidence is available for machine verification.

Use `docs/aif-candidate-probe/README.md` for artifact lineage and observations. The reported test
follows `postman-request-body.json`; the earlier `sample-request.json` is a different preparation
artifact. Preserve both, do not rewrite the tested prompt in place, and do not label a screenshot
transcription as a live golden fixture. The final implementation-generated request will require
its own version because the prototype source-ID hash differs from current app normalization.

## 2. Scope and non-goals

Implement the agreed candidate pipeline across Offline, Internal fake, the provider boundary,
Human Review, and generated records. Reuse Python 3.12, `uv`, Pydantic, Streamlit, and existing
provider/delivery abstractions. Keep source acquisition and SI drafting behavior unchanged.

Prioritize the shortest complete path: existing SI loading and confirmed review inputs -> Analyze
Review -> one AIF candidate response -> human corrections and required-field completion -> reviewed
minutes/action outputs -> the existing authorized Delivery flow. Preserve the separate SI-drafting
workflow, navigation, source context, evidence visibility, and output consistency. Reduced automated
categories must not leave broken stages, misleading empty summaries, or unusable downstream records.
Defer unrelated refactoring, generic provider abstractions, performance tuning, and additional
features. Prefer focused reusable functions and a short integration checklist over new machinery.

No real Confluence, AIF, Teams, ADO, database, authentication, RAG, or agent-framework integration;
no dependency additions, transport/authentication/TLS/proxy configuration changes, heuristic JSON
repair, additional model calls, automatic retry, model fallback, or production activation. No new
manual authoring workflow for the four excluded categories. Live acceptance belongs to the internal
team and is a separate gate, not a prerequisite for this local synthetic implementation.

## 3. Candidate, source, and review contracts

### 3.1 Exact model response

```json
{
  "items": [
    {
      "kind": "finding",
      "text": "A source-supported review issue.",
      "evidence_source_ids": ["transcript-017"]
    },
    {
      "kind": "action",
      "text": "An explicitly stated follow-up action.",
      "evidence_source_ids": ["transcript-019"]
    }
  ]
}
```

The example IDs illustrate shape; actual IDs come only from the request's source map. Require the
`items` collection and all three item fields, reject extra fields, permit only `finding` and
`action`, and reject blank text, empty/non-string/unknown evidence IDs, and duplicate IDs within
an item. An empty items array is a valid result, not a global claim that the review has no issues.
Reject string-wrapped arrays/objects, old six-category payloads, alternate field names, malformed
JSON, and unsupported kinds without coercion or repair. Parsing a JSON string once at the existing
transport boundary is allowed; recursively decoding malformed nested fields is not.

The model must still classify and describe candidates. Do not replace extraction with ID selection
or generate candidate prose from a fixed local label. Findings are explicitly raised design gaps
or issues; actions are explicitly proposed/agreed work. Do not infer an action from a finding.
When an extracted action has an explicit owner or date, preserve that detail in candidate text;
do not replace an explicit date with `the proposed date`. If the source is uncertain or conflicting,
preserve that uncertainty without inventing a resolution or converting relative dates by guesswork.
No separate outcome, severity, priority, status, owner, or due-date fields appear in the model schema
or prompt request. Required structured business values remain human-entered.

Give later explicit reviewer classification/clarification precedence over the broad finding
definition. Do not convert excluded categories merely because they describe a gap. This is a
general prompt requirement, not a topic blacklist or target count. Schema/source-ID validation
cannot prove that the model obeyed it; semantically wrong but structurally valid proposals remain
available for human correction. Do not add an automatic semantic judge, extra model call, or
heuristic category filter.

### 3.2 Complete input and deterministic sources

- Build a versioned deterministic source index before the call. Retain exact original snapshots
  locally and render all SI/transcript content once, annotated with IDs, plus confirmed context.
  The annotation is the wire source map; do not send another complete duplicate of the same source
  text. Do not truncate, summarize, filter by category, or omit unrecognized source text.
- For v1, use deterministic physical-line segments in normalized source text, with opaque
  source-type/digest/line IDs. Normalize newlines and outer whitespace consistently with existing
  source fingerprints; retain the original source mapping locally. This deliberately versions the
  prototype raw-text hash rather than silently claiming identical IDs. Derive heading/utterance
  locators only from actual source structure, including multiline and unformatted transcripts;
  use multiple line IDs when necessary. No semantic chunker or generalized indexing subsystem.
- Preserve original source text/spans and only populate locators actually present. Follow existing
  newline-normalization conventions consistently and version the indexing rule. Duplicate text in
  different positions remains distinct. Identical snapshots produce identical IDs; changed source
  snapshots cannot silently reuse old evidence bindings.
- Resolve IDs locally to original `SourceEvidence` quotes, source types, locators, and references.
  Never accept model-generated quotes/locators or synthesize evidence from candidate descriptions.
- Keep confirmed context application-owned: it is not returned by the model. Replace the previous
  response-context equality test with request/analysis binding checks, source fingerprints, and
  immutable confirmed-context copies. Include provider identity and contract/index version in
  analysis invalidation.
- Prompt requirements include full input use, explicit finding/action definitions, no implied work,
  source-supported wording, exact schema, valid IDs only, and treating source text as data rather
  than instructions. Each eligible AIF Analyze attempt makes exactly one transport/model call,
  including empty-result and provider-failure cases; no retry or repair call. Local preflight
  rejection makes no call, and Offline stays entirely deterministic with no model invocation.

### 3.2.1 Reusable request/response adapter without HTTP

Add a small pure `integrations/aif_candidate_protocol.py` module so internal integration can reuse
the precise envelope handling without replacing its HTTP transport:

- Build the messages, small inline candidate tool schema, `strict: true`, `stream: false`, and
  named `tool_choice` for `emit_review_candidates`; do not combine it with `response_format`.
  Require model/configuration values from the caller; add no endpoint, client, credential, TLS,
  proxy, network operation, framework, or generic response-normalization layer.
- Generate the next Postman body with this same builder. Keep the plain wire schema small and
  free of domain-model definitions/references. Enforce nonblank values, duplicates, and ID
  membership locally even if the endpoint accepts only the simpler structural schema.
- Decode one expected tool call from one choice. Validate finish reason, function type/name,
  refusal, cardinality, and argument type. HTTP JSON decoding happens in the transport; decode
  `function.arguments` once as JSON into the candidate object. Null/empty message content is valid
  for a tool response; do not recover candidate data from prose, Markdown, alternate fields, or
  multiple outputs. Ignore unrelated provider metadata rather than rejecting ordinary envelope
  extensions, but reject conflicting content or an ambiguous result.
- Keep the existing `AifTransport.analyze()` role: return the extracted candidate object (or its
  single JSON serialization) to the extractor, not the whole provider envelope. Internal HTTP
  code calls the reusable codec; local Offline and synthetic transports need no real connection.
  Map refusal, timeout, malformed/truncated output, and provider failure to safe existing errors.

The request builder, candidate schema, source-index version, synthetic responses, and exported
probe must share the same definitions. Test this parity to avoid a passing manual request that
differs from what the app sends. The observed response supports this transport choice for this
batch; it does not establish provider-wide schema enforcement or warrant a fallback protocol.

### 3.3 Human review and final conversion

- Introduce separate validated candidate-analysis and editable review-draft types. Candidate
  analysis includes application-owned context, source binding, stable candidate identities,
  validated items, and resolved evidence. It is never a partial `GovernanceResult`.
- Present Findings and Actions with editable text, include/exclude controls, and kind correction
  between those two categories. Keep the complete source available for inspection; unmatched or
  out-of-scope text is not classified as Missing Evidence. Evidence views must let the reviewer
  inspect later context not cited by the candidate, such as the probe's category clarifications.
  Use kind correction for finding/action confusion and exclusion for an out-of-scope candidate;
  do not introduce an editor for the four excluded categories. Label resolved evidence as source
  traceability, not a verified interpretation or approval.
- Give each candidate a stable identity independent of its edited text, kind, position in a
  filtered list, and inclusion flag. Keep original evidence read-only and preserve the original
  analysis for comparisons. Reclassification must not lose provenance or silently fill business
  fields; irrelevant fields must not leak into the new category.
- Finding description starts from candidate text; the reviewer supplies a short title and
  explicitly selects severity and status. Action title starts from candidate text; the reviewer
  explicitly selects priority. The reviewer explicitly selects the review outcome. Required
  selectors start unselected, including status despite its legacy domain default.
- Optional owner/date/category/recommended-change values remain blank unless entered by the
  reviewer. Do not parse candidate text to silently prefill owner/date. Keep existing required
  Delivery owner/date/parent and mapping checks; valid local records may retain optional unknowns.
- Keep outcome provenance rules: demo/development/test human choices use the existing explicit
  reviewer-selected result/provenance and optional evidence; standard domain results still require
  source support for stated meeting outcomes. Do not expand demo outcome allowances to production.
- Validate draft fields during editing without constructing a completed result. On explicit human
  confirmation, reconstruct the complete result from retained reviewed candidates, current trusted
  context, and original evidence, then run full domain validation and
  `validate_governance_evidence()` before generating or storing outputs. Invalid completion leaves
  no eligible completed result, preview, confirmation, or generated output.
- Empty/all-excluded candidates still require an explicit human outcome and confirmation. Do not
  create default findings, actions, or business values to make the workflow pass.

### 3.4 Extraction scope in generated records

Add typed application-owned extraction-scope metadata to completed results from this path:
automated categories are finding/action; Decisions, Risks, Open Questions, and Missing Evidence
are not extracted. Keep their domain collections available for historical full-result validation,
but empty in this bounded conversion. Historical results without this metadata remain explicitly
legacy examples; they cannot enter the new candidate workflow as provider output.

Human Review, output summaries, Markdown minutes, and downloadable/mock ADO record descriptions
must state: `Not extracted in this version; no conclusion about whether such items exist.`
Empty excluded categories must never display `None recorded.` or zero-count badges implying
absence. Scope also identifies review outcome as human-completed. Preserve the formal governance
authority note. Keep ADO adapter/payload interfaces stable; carry scope through existing record
description fields where appropriate rather than adding enterprise fields.

## 4. Components and implementation sequence

Proposed new reusable modules under `src/architecture_governance_copilot/`:

| Module | Responsibility |
| --- | --- |
| `review_candidates.py` | Strict wire contract, candidate analysis/draft types, source-reference validation, schema and prompt contract. |
| `review_sources.py` | Versioned source indexing, snapshot binding, deterministic ID resolution into original evidence. |
| `candidate_review.py` | Human completion validation, conversion to the complete domain result, retained candidate-to-action identity mapping. |
| `integrations/aif_candidate_protocol.py` | Pure one-tool request builder and envelope decoder; no HTTP or configuration changes. |

Keep shared Streamlit state/fingerprints/reset/reconstruction orchestration in `ui_support.py`;
delegate reusable pure conversion to the new modules. Keep the shell and renderers in `app.py` and
retain thin `pages/` routes. Do not restructure the app as an unrelated cleanup.

1. **Activate approved scope.** Recheck Git status, preserve user files, create the task branch,
   and record approval/lifecycle. Add strict contracts, source indexing, the pure protocol codec,
   and focused unit tests. Verify one complete request and synthetic response through this boundary
   before changing UI state; do not spend the batch on iterative prompt tuning.
2. **Migrate the analysis boundary and fixtures together.** Explicitly change
   `GovernanceExtractor.extract()` and `GovernanceReviewService.analyze_review()` to return
   candidate analysis. Update `EvidenceValidatingExtractor` to validate candidates without making
   a domain result. Adapt `integrations/aif.py` request/schema/parser to one candidate call;
   preserve safe error categories. Adapt `extractors.py`, `demo_review.py`, `synthetic_aif.py`,
   `runtime_dependencies.py`, test doubles, and active fixtures in the same coherent change.
   Preserve `SolutionIntentDrafter`; output generators still consume reviewed `GovernanceResult`.
3. **Implement human completion and state transitions.** Update `ui_support.py` and `app.py`
   analysis storage, route guards, editor fields, comparisons, confirmation, failure handling,
   and invalidation. Implement the late domain/evidence-validation gate and stable action mapping.
   Exercise both correct candidates and a structurally valid response containing category mistakes.
4. **Make output scope truthful.** Update `models.py`, `minutes_generator.py`, `ado_generator.py`,
   and relevant UI summaries. Preserve delivery capability checks, explicit preview/confirm/Create,
   reconciliation history, no-duplicate behavior, and development-only new-demo-run reset. Make
   only a focused `publication.py` compatibility adjustment if needed for retained legacy receipts;
   do not change the ADO gateway interface or enterprise mapping requirements.
5. **Synchronize maintained documentation and internal handoff.** Update `AGENTS.md` current
   caveats, `README.md`, `SPEC.md`, `DEMO.md`, and the relevant Analyze Review section of
   `docs/INTERNAL_INTEGRATION_HANDOFF.md`. Add the migration guide and OpenCode instruction below.
   Do not rewrite completed plans, submission baseline, historical media, or user-provided files.
6. **Verify, complete lifecycle, commit, and push.** Run the checks and browser scenarios below,
   fix failures within scope, record evidence, mark R28/Batch 24 verified only after acceptance,
   clear the active pointer, and push focused commits to `origin/codex/analyze-review-candidates`.
   Never reset unrelated changes or force-push.

Prefer reviewable commits for reusable contracts/protocol code, the coherent provider/UI/fixture
migration, and final documentation/evidence, with the actual dependency order recorded. Do not
hand off a provider-return-type change without its required consumers and tests. Keep commits
small enough for internal inspection; do not require a wholesale merge over uncommitted adapters.

## 5. Synthetic fixtures and compatibility

- Preserve current SI/transcript/metadata text, drafting fixtures, and Confluence snapshot content.
  Keep fixture-bound SI eligibility and request-aware edited-transcript/metadata behavior. No new
  claim of general semantic AI capability in either deterministic synthetic path.
- Keep `samples/expected_result.json` and `samples/internal_fake_aif_result.json` byte-for-byte as
  legacy full-domain examples, not active extraction responses or sources of hidden UI defaults.
- Add `samples/expected_candidates.json` and `samples/internal_fake_review_candidates.json` as
  active exact-contract fixtures. Preserve the explicitly supported three findings and two actions
  in each canonical scenario, including useful original wording and evidence; validate every ID
  against the actual source index. Do not carry over the four excluded categories or outcome.
- Add explicit synthetic human-completion overlays and expected completed results under
  `tests/fixtures/` for the new canonical flows. Required business values are visibly supplied by
  those simulated human steps, never supplied by the provider fixture or runtime defaults.
- Add a candidate response for the minimal Internal fake test package. Retain its existing
  full-result fixture as a legacy boundary example. Document active versus legacy roles, lineage,
  and source bindings in `samples/README.md`.
- Add a clearly labeled synthetic adverse-quality fixture reflecting five findings/two actions,
  including the two excluded-category false positives observed in the photographs. It must pass
  structure/reference validation, enter human review, and support exclusion of those two items
  using the full transcript before confirmation. Test the retained evidence, identities, action
  mapping, and output scope. It is neither a verbatim live response nor a correct canonical answer.
- Keep the scenario-specific three-finding/two-action expected fixture as the correct demo
  contract. Live acceptance evaluates supported meaning rather than exact wording/count across
  arbitrary inputs; never implement the canonical count as a runtime validator.
- Update sample/extractor/AIF/service/runtime/UI/generator tests with the new fixtures together.
  Preserve meaningful legacy domain/evidence/generator tests as historical full-result coverage.
  Existing six-category fixture equality is intentionally superseded for active Analyze Review.
- No persisted database migration exists. Reject/invalidate obsolete full-result analysis session
  state on rerun rather than treating it as reviewed candidates. Preserve remote-operation facts
  and receipts under ordinary invalidation/reset; only the existing explicit fake new-run command
  may clear its authorized local simulation state.

## 6. Invalidation and failure behavior

- Source, transcript, confirmed metadata, provider configuration, source-index/contract version,
  and deployment-policy changes invalidate candidate eligibility, review confirmation, completed
  result, generated outputs, and delivery preview/selection/confirmation as appropriate.
- Revoke the previous analysis before each new attempt, including retries with unchanged input.
  Only atomically store a fully validated candidate batch and matching fingerprint on success.
  Timeout/refusal, malformed output, any bad item/ID, or provider failure leaves no stale/partial
  success or route to outputs. Retain inputs and safe actionable error feedback.
- Preserve the existing confirmed-snapshot rule: unsubmitted review edits/reclassification/exclusion
  remain pending and visibly distinct from the last confirmed result; they never silently mutate
  its outputs or delivery payload. At the next explicit confirmation attempt, revoke old output
  eligibility before validation and atomically replace the confirmed result/artifacts only after
  validation and generation succeed. A failed reconfirmation cannot leave stale success. Input or
  provider changes still invalidate the prior snapshot immediately as described above.
- Map retained reviewed actions to stable original candidate identities/indices for delivery.
  Test finding-to-action, action-to-finding, exclusion of earlier candidates, reordering of displayed
  groups, editing after a receipt, and retry paths. Compact reviewed-list indices alone must not
  change the identity of an already tracked action or bypass duplicate protection.
- Treat candidate order as stable only within its analysis snapshot. A later live response can
  reorder candidates or change wording/supporting references for the same inputs. Regression-test
  reanalysis with retained success/unknown receipts: reuse a provable existing action binding, or
  block an ambiguous Create for reconciliation. Do not treat a new list index or newly generated
  candidate text as proof that a new remote action should be created.
- Cover cross-contract receipt migration too: existing publication correlation hashes evidence
  quote/reference as well as index, so new indexed evidence may change the correlation even for
  the same review/action. Preserve pre-candidate `SUCCEEDED` and `UNKNOWN_RESULT` history. Reuse
  a provably matching receipt; if safe identity cannot be established for retained legacy history
  in the same review package/target, block new Create pending reconciliation rather than assigning
  a new correlation and risking duplication. Do not clear that history through ordinary resets or
  schema migration. The existing explicitly confirmed development fake new-run reset remains the
  only in-product exception for discarding its local simulation facts.
- Keep production synthetic denial, ordinary reset preservation, and the narrow explicit fake
  new-run reset guards. Never select Offline/Internal fake because a live provider fails.
- Rollback is by a normal reviewed revert of this batch's commits, followed by a fresh review
  analysis/session. Do not use destructive Git resets, clear real receipts, or replay old results as
  new successes. Internal rollout begins with the internal team's own checkpoint.

## 7. Acceptance and verification

Required behavior and evidence:

| Area | Acceptance |
| --- | --- |
| Complete demo and internal handoff | The local candidate workflow is usable from the existing Analyze Review button through human confirmation and consistent outputs/authorized synthetic Delivery, with SI drafting preserved. The internal handoff identifies exact replacement points, reusable tested code, preserved connections, and button-to-output acceptance steps so OpenCode does not have to redesign the workflow. |
| One-call contract | An admitted AIF request makes exactly one call with full indexed SI/transcript/context; Offline and failed preflight make none. Only finding/action candidate fields are accepted. No business defaults, retries, repair, or fallback. |
| Protocol parity | The pure builder, inline schema, parser, synthetic transport tests, source index, and next exported probe agree. One target tool call is decoded once; malformed, refused, truncated, ambiguous, or nested-string collections fail without repair. |
| Evidence | Deterministic IDs and coverage, repeated text/headings, multiline/plain transcript, newline handling, multiple supporting sources, unknown/stale IDs, and immutable original evidence are verified. |
| Atomic validation | One malformed item rejects the whole response; failed unchanged-input retry cannot reuse prior analysis; empty valid response is handled truthfully. |
| Human completion | Edit/exclude/reclassify, missing title/severity/status/priority/outcome, blank optional values, excluded incomplete items, invalid dates, and change/revert comparisons behave correctly. |
| Semantic correction | Structurally valid but out-of-scope proposals are not certified as correct. A synthetic five-finding/two-action response reaches review; the user can inspect later classification context and exclude the two false positives without harming the two actions. |
| Final gate | Full domain and original-source evidence validation run after human review; no outputs or delivery before explicit valid confirmation. |
| Scope disclosure | All four excluded categories read as not extracted throughout UI and generated/downloaded records, including empty-result cases. |
| State | Inputs/provider/policy/version changes, direct route access, legacy session state, ordinary reset, and explicit fake new-run reset enforce eligibility and preserve reconciliation. Pending edits preserve the confirmed snapshot; failed reconfirmation revokes its output eligibility. |
| Delivery | Missing owner/date/parent still blocks; completed synthetic values permit preview/confirm/Create/read-back; stable candidate identity survives exclusions and reclassification; repeat Create remains blocked. Reordered/reworded reanalysis and pre-candidate success/unknown receipts cannot bypass reconciliation through changed indices or evidence IDs. |
| Offline compatibility | Canonical and edited synthetic input paths work without network; fixed SI restrictions, source acquisition, and separate SI drafting still hold. |

Add focused tests for the four new modules. Update relevant existing suites:
`test_models.py`, `test_extractors.py`, `test_governance_service.py`, `test_aif_integration.py`,
`test_evidence_validation.py`, `test_runtime_dependencies.py`, `test_sample_data.py`,
`test_internal_fake_sample_data.py`, `test_app.py`, `test_ui_support.py`,
`test_minutes_generator.py`, `test_ado_generator.py`, and affected publication/delivery tests.
Use strict synthetic mocks to verify call count and request completeness; they do not measure live
model accuracy or reliability.

Record four separate acceptance levels:

1. **Wire contract:** exact request/response envelope, parsing, candidate field validation, and call
   counts. Screenshots are observations; only supplied raw bytes can establish raw-response parsing.
2. **Source traceability:** every reference resolves to original source evidence and the correct
   snapshot. This does not establish entailment, correct classification, or extraction completeness.
3. **Human-reviewed local workflow:** synthetic canonical, edited, malformed, and adverse-quality
   inputs exercise review, completion, invalidation, output, and delivery safeguards. Passing this
   level closes only the local batch after all required checks.
4. **Internal live workflow and quality:** use the implementation-generated request with the real
   internal adapter; record extraction quality separately from successful human correction and
   end-to-end operation. A live sample with extra findings is not a clean semantic pass, even if
   human exclusion makes its final record usable. R9b release acceptance remains separate.

Include bounded synthetic variants for finding-only/no-action content, explicit action dates,
repeated commitments, later category clarification, and a changed classification under new
source fingerprints. They check contracts/workflow deterministically; prompt assertions and fake
results must never be described as proof of live semantic performance.

Run from the repository root after implementation:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Run `uv run streamlit run app.py` on an available dedicated local port, preserving any user server.
Use applicable Streamlit state/code-organization guidance and the frontend testing skill. The
Browser plugin/skill is not listed in this session; use the skill's regular Playwright fallback,
recording `Browser plugin not available` and any tooling limitation. Read the Playwright skill and
inspect the available runtime before executing browser verification. Keep
browser state, screenshots, and temporary scripts outside the repository; do not add dependencies
for convenience.

Browser flow under test: Review Inputs -> Analyze Review -> editable finding/action candidates ->
human completion/confirmation -> scoped outputs -> Internal fake Delivery preview/confirm/Create
and read-back. Exercise canonical Offline and Internal fake paths, edited transcript/metadata,
reclassification/exclusion, missing required business fields, changed-input invalidation, and
ordinary/new-demo-run reset behavior. Check desktop and a narrow viewport, meaningful content,
route identity, readable evidence, action feedback, console errors, and screenshot/interaction
evidence. Programmatic AppTest/contract tests cover failure injection and duplicate/receipt cases
that are unsuitable for browser-only manipulation. Report remaining live-integration limitations.

## 8. Internal migration deliverables

Lead the handoff with a concise operator checklist for OpenCode with GPT-5.4: what to reuse, where
to connect the existing AIF HTTP call, what internal code/configuration to preserve, and how to
demonstrate the complete result. Keep implementation reference detail separate from that checklist.
The intended internal task is bounded adaptation of tested code, with actual internal differences
inspected first; model choice alone is not evidence that the integration has passed.

Create `docs/ANALYZE_REVIEW_CANDIDATE_MIGRATION.md` with:

1. The actual new module/API names and commit map; explicit change from complete result to
   candidate analysis at `GovernanceExtractor`/service boundaries, and unchanged downstream input.
   Distinguish reusable files to copy/import, existing functions to adapt, and internal transport
   configuration that must remain intact. Base the map on actual final commits, not guessed paths.
2. Exact JSON contract/schema, a complete synthetic request/example, prompt requirements, versioned
   source-ID construction, evidence validation, and errors rejected without normalization patches.
   Include the builder-generated Postman body, protocol tests, the versioned manual-probe record,
   and known classification/date limitations. A raw live replay fixture is optional until the user
   supplies one; label all constructed envelope examples synthetic.
3. Surgical integration instructions: checkpoint and inspect internal differences; import reusable
   modules; build index from the existing Confluence canonical snapshot and transcript; pass full
   sources/context to one existing HTTP/model call; replace staged extraction orchestration and
   old response normalization; connect candidate review and final conversion. Do not copy the
   whole local `aif.py` over internal transport/authentication code.
4. Preserve current Confluence reader/snapshot acquisition, endpoint/client/authentication/TLS/proxy
   configuration, ADO transport and required-field validation. Map the existing provider envelope
   to exactly one candidate object; a forced tool-call argument may be decoded once if used by the
   internal transport. Reject truncation, refusal, ambiguous/multiple outputs, and malformed shape.
5. Regression commands and manual live acceptance: full real SI/transcript/context arrives in one
   call; candidate text/classification is meaningful and source-supported; findings do not invent
   follow-up work; human corrections/completion and final validation work; excluded scope is
   disclosed; bad/refused/timed-out responses do not produce outputs/fallback; source changes
   invalidate state; authorized test-target ADO preview/Create/read-back and duplicate safeguards
   remain valid. Record actual live successes/failures separately without confidential source data.

Give OpenCode an ordered integration sequence with observable stop points:

1. Save the internal team's own checkpoint, inspect its uncommitted changes and active call chain,
   and identify the precise six-stage entry point and old full-result validation consumers. Do not
   infer those paths from this external checkout or overwrite an existing `aif.py`.
2. Run the reusable protocol/source/candidate tests and replay a synthetic envelope through the
   existing transport adapter seam. If raw probe output is available, replay it separately with
   provenance recorded. Do not open network or rewrite authentication to make replay pass.
3. Route one explicitly selected Analyze action through the new single-call candidate path;
   verify that legacy stages and full-domain validation no longer execute on that path. Preserve
   the current source loader and all unrelated integration work.
4. Verify candidate review and final conversion end to end, including bad IDs, provider failure,
   valid-but-misclassified items, and source-change invalidation. Do not judge integration by a
   successful direct endpoint call alone.
5. Run a live request using the final builder and a bounded new/changed synthetic input, then
   complete human review and the already-authorized delivery acceptance. Do not add or activate
   a missing ADO capability merely to complete this migration; report any separate dependency.

Stop at the failing boundary, preserve evidence, and fix that boundary within scope. Do not revive
six-stage extraction, add a repair pipeline, or change HTTP/auth settings as a generic recovery.

Create `docs/OPENCODE_ANALYZE_REVIEW_MIGRATION_PROMPT.md` containing a ready-to-use English
instruction for the internal team, referencing the final commits and migration guide, preserving
their checkpoint/uncommitted integrations, forbidding wholesale transport replacement, and
requiring internal regression plus separate live acceptance. These deliverables do not claim or
perform live integration in this checkout.

## 9. Dependencies, discoveries, and deferred work

- No unresolved design blocker: the user settled the target scope and explicitly approved
  implementation. Internal files/access are not needed for local synthetic work.
- Raw live response bytes and another manual probe would improve protocol/quality evidence but
  do not block approved local implementation. Recommend only one targeted revised-prompt check
  on the original scenario and a changed-classification/no-action variant, using final generated
  IDs. Do not repeatedly optimize to the original answer or require perfect automatic classification
  before building the mandatory human correction path.
- Review reconstruction currently assumes a completed result; the change is broader than swapping
  an AIF prompt/schema. Source mapping and human-state migration are necessary parts of this batch.
- The final output path needs an explicit fresh evidence-validation call; analysis-time validation
  alone does not satisfy the new human-completion boundary.
- Existing same-input failure handling can leave the old analyzed result stored. Candidate state
  must fix that eligibility path rather than carry it into the new implementation.
- Source-index migration changes evidence references and may change quote granularity, both of
  which participate in delivery correlation. Retaining receipts without a compatibility guard is
  insufficient to protect existing simulated/remote-operation history from duplicate creation.
- The register's maintenance instruction incorrectly said to mark items `Verified` when work
  starts; the planning update corrects it to `In progress`, consistent with the lifecycle table.
- General semantic offline extraction, extra automatic categories, optional business-field AI
  extraction, richer candidate authoring, persistent state, real connections, and R9b production
  acceptance remain deferred. No scope expansion is implied by a passing local test suite.

## 10. Progress and actual verification evidence

- [x] Inspect baseline `67a60da`, repository instructions, register, code, fixtures and tests.
- [x] Review user-supplied photographs and versioned probe limitations; revise the bounded plan.
- [x] Record explicit implementation approval and create `codex/analyze-review-candidates`.
- [x] Implement strict source/candidate/codec/conversion contracts and migrate providers/fixtures.
- [x] Implement human completion, final validation, invalidation, scope and action identity.
- [x] Synchronize maintained documentation, migration guide and ready OpenCode instruction.
- [x] Complete automated and desktop/narrow browser acceptance.
- [ ] Commit final documentation, push the branch and verify the remote revision.

### Automated checks

All checks ran on 2026-09-18 against the final application changes:

| Command | Actual result |
| --- | --- |
| `uv sync` | Passed; dependency and lock files unchanged. |
| `uv run pytest -q` | **637 passed in 114.44 seconds.** |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed; 57 files already formatted. |
| `uv build` | Source distribution and wheel built successfully. |
| `git diff --check` | Passed. |

The 637 tests include candidate/codec/source strictness, explicit human overlays, the constructed
seven-candidate semantic-error example, final original-source validation, source/provider/version
invalidation, same-input failure, legacy-session denial, publication reconciliation, shared-evidence
independent actions, production synthetic denial, ordinary/new-run resets and separate SI drafting.
Legacy full-domain fixtures remain covered as historical models/generator examples.

SHA-256 checks verified all four pre-existing untracked user files and both original probe bodies
unchanged. Every previously tracked file under `samples/` matches `67a60da` byte-for-byte. No real
connection, credential, dependency, lock-file, route-entry or media change was introduced.

### Browser acceptance

`Browser plugin not available`; used the installed Playwright CLI with isolated browser sessions
and temporary scripts/screenshots in `/tmp/agc-batch24-qa/`. A dedicated server used
`AGC_INTERNAL_FAKE_ENABLED=1 AGC_DEPLOYMENT_PROFILE=development AGC_DEMO_STEP_DELAY_SECONDS=0`
and `uv run streamlit run app.py --server.port 8507 --server.headless true`. Existing user servers
were preserved. Chromium desktop viewport was 1440x1000; an independent narrow session loaded at
390x844. Narrow content/client width both measured 390 pixels.

| Check | Observed result |
| --- | --- |
| Page identity/content | Correct Architecture Governance Copilot title and stage URLs; meaningful content, no blank page or framework exception overlay. |
| Initial candidate review | Canonical three-finding/two-action proposals; blank finding titles/severity/status and action priority/outcome; source traceability and full context available. |
| Classification correction | Changed first finding to action and back through the visible kind selector; original proposal/evidence retained. |
| Internal fake workflow | Loaded/confirmed complete inputs, clicked Analyze, explicitly completed human fields, generated consistent scoped outputs, delivered both actions independently through preview/confirm/Create. Both receipts reported GET read-back verification. Protected actions had preview disabled. |
| Offline/narrow workflow | Loaded canonical Offline inputs and analyzed; returned to inputs, edited transcript and architect metadata, observed prior-analysis invalidation, reconfirmed and analyzed the changed two-item transcript. |
| Missing required fields/exclusion | Confirming without outcome failed without outputs. Explicitly selected Not Stated, excluded the incomplete finding, selected action priority and generated scoped local output retaining updated metadata. Optional owner/date stayed unknown. |
| Reset | Confirmed Internal fake new-demo-run cleared that session's simulated run. Ordinary Offline Reset review returned to inputs with manifest confirmation disabled. Protected-history preservation and production/fake restrictions also passed automated tests. |
| Responsive/evidence | Fresh narrow session showed readable wrapped candidate fields; desktop outputs and both delivery receipts rendered correctly. Screenshots inspected locally. |
| Console | Both final browser sessions reported 0 errors and 0 warnings. |

Browser automation used keyboard selection for accessible native controls. Initial source hot-reload
and automation timing attempts were discarded before final acceptance; no application change was
made to compensate for tooling. Failure injection and cross-contract receipt ambiguity were covered
by AppTest/unit tests, not claimed as real-provider browser tests.

Representative external screenshots: `desktop-blank-review.png`, `desktop-outputs.png`,
`desktop-delivery.png`, `narrow-candidate-review.png`, and `narrow-offline-outputs.png` in the temporary
QA directory. These are local synthetic acceptance evidence, not committed product assets.

### Implementation discoveries resolved

- Freeze context before transport and bind analysis to that request snapshot.
- Check the confirmed manifest before calling the provider; revoke prior eligibility on every attempt.
- Ignore hidden owner/date callbacks after leaving Human Review so navigation preserves human edits.
- Use exact original indices for scoped candidate actions, retaining legacy compact aliases only for
  unscoped results; distinct actions sharing evidence can be delivered independently.
- Keep conservative protected-history guards when prior candidate/legacy identity is unprovable.
- Include scope in actual Create descriptions as well as local Markdown/JSON/mock previews.
- Reject duplicate JSON object keys, malformed dates and stale evidence without repair.

## 11. Completion record

Local implementation and acceptance are complete. Final documentation commit and branch push are
pending. Reusable contracts: `d143b7c`. Coherent application/provider/UI/fixture migration: `51a70fc`.
The migration guide and ready OpenCode instruction identify these commits and preserve the internal
team's unseen working transports/configuration through surgical adaptation.

Live AIF reliability, extraction quality with the revised prompt, internal button-to-output/ADO
acceptance and R9b production acceptance remain unverified here. The internal final demo is complete
only after its actual Analyze Review button calls real AIF and continues through human confirmation
and the intended existing outputs/delivery. A passing local batch is integration readiness evidence,
not proof that those internal operations have already been completed.
