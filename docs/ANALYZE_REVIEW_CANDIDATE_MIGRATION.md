# Analyze Review candidate migration

Purpose: connect the internal application's existing AIF HTTP call to a smaller, tested candidate
contract so the real Analyze Review button leads to a complete human-reviewed demo. This guide does
not authorize new enterprise services, production activation or publication targets.

## Operator checklist

1. Save the internal team's own checkpoint, including its uncommitted integration work. Inspect the
   actual Analyze Review call chain and locate the six-stage extractor and full-result consumers.
2. Reuse the four pure modules below. Adapt internal orchestration and UI state to candidate
   analysis. Preserve working Confluence acquisition, HTTP client/authentication/TLS/proxy settings,
   ADO transport, target mappings and publication safeguards.
3. Replay a synthetic envelope through the request/decoder/extractor seam. Then route the real
   Analyze button through exactly one complete-source AIF call; old extraction stages must stop.
4. Complete candidate Human Review, including required fields/outcome, exclusion and kind correction.
   Verify final domain/source validation and consistent scoped minutes, JSON and action outputs.
5. Run one bounded live synthetic input through the actual button, then the already-authorized
   Delivery flow. Record endpoint/semantic quality separately from human-reviewed workflow success.

Stop at a failing boundary and fix it within this scope. Do not revive staged extraction, add JSON
repair, create a fallback model path or rewrite authentication as a generic response-shape remedy.

## Local implementation and commit map

Baseline: `67a60da`. Task branch: `codex/analyze-review-candidates`.

| Commit | Review purpose |
| --- | --- |
| `d143b7c` | Four reusable candidate/source/conversion/protocol modules, scoped domain metadata and focused contract tests. |
| `51a70fc` | Coherent provider/service/runtime/UI/fixture migration, final confirmation and delivery safeguards with regression coverage. |
| Documentation commits following `51a70fc` on `codex/analyze-review-candidates` | Maintained product documentation, versioned probe artifacts, this guide, ready OpenCode instruction and final verification record. |

Review the commits in this order; port only the required functions after inspecting internal
changes. These are not instructions to cherry-pick over working uncommitted transports. Batch
verification is recorded in [Batch 24](exec-plans/POST_BASELINE_REFINEMENT_BATCH_24.md): 637 tests,
Ruff checks, build and desktop/narrow synthetic browser flows passed. Real internal AIF acceptance
remains separate and unverified here.

| Reuse or adapt | Actual module/API | Responsibility |
| --- | --- | --- |
| Reuse pure module | `review_sources.build_review_source_index(solution_intent, review_transcript)` | Complete deterministic source index, immutable original spans and local ID resolution. |
| Reuse pure module | `review_candidates.parse_candidate_payload`, `candidate_json_schema`, `build_candidate_analysis`, `validate_candidate_analysis_binding` | Strict wire contract and source/context/provider-bound `ReviewCandidateAnalysis`. |
| Reuse pure module | `candidate_review.create_candidate_review_draft`, `complete_candidate_review` | Editable draft, explicit human completion and final result/evidence validation. |
| Reuse pure module | `integrations.aif_candidate_protocol.build_candidate_request_body`, `decode_candidate_tool_response` | Forced single-tool request and one envelope decode; no HTTP client/configuration. |
| Adapt existing seam | `AifTransport.analyze(AifGovernanceRequest)` | Use existing approved HTTP client once; return only candidate object or its single JSON serialization. |
| Adapt consumers together | `GovernanceExtractor.extract`, `GovernanceReviewService.analyze_review`, `EvidenceValidatingExtractor` | Return/validate candidate analysis; do not construct a complete result during analysis. |
| Adapt UI/state | `app.py`, `ui_support.py`, thin `pages/` routes | Candidate eligibility, independent draft, human fields, confirmation, invalidation and action identity. |
| Preserve downstream input | `generate_review_minutes`, `generate_mock_ado_work_items`, publication coordinator | Consume only a completed human-confirmed `GovernanceResult`; disclose typed scope. |

Copy/import the reusable modules together with their model definitions and focused tests. Internal
files may contain real transport work absent from this checkout. **Do not replace internal
`integrations/aif.py`, runtime wiring or configuration wholesale with the external versions.**
Use a reviewed function-level port or selective commit application after inspecting each diff.
The separate `SolutionIntentDrafter` boundary and existing source acquisition remain unchanged.

## Exact candidate and scope contract

```json
{
  "items": [
    {
      "kind": "finding",
      "text": "An explicitly raised design issue supported by the sources.",
      "evidence_source_ids": ["an-ID-from-this-request"]
    },
    {
      "kind": "action",
      "text": "An explicitly proposed or agreed follow-up, preserving stated owner/date detail.",
      "evidence_source_ids": ["another-ID-from-this-request"]
    }
  ]
}
```

IDs above illustrate shape only. Generate real IDs from the complete current snapshots. All fields
are required; extras, unsupported kinds, blank/non-string text/IDs, empty or duplicate evidence IDs,
unknown/stale IDs, nested string-wrapped arrays and old full-result responses fail without repair.
One invalid item rejects the complete response. `{"items": []}` is valid.

The small inline tool schema comes from `candidate_json_schema()`, not `GovernanceResult`'s schema.
No outcome, severity, status, priority, owner, due date, evidence quote or confirmed-context fields
are returned by the model. The model still classifies and writes descriptions; it is not an ID
selector with locally invented prose. Findings identify explicit issues; actions describe explicitly
proposed/agreed work. A finding alone is not authorization to invent an action. Later explicit
reviewer category clarification takes precedence; excluded-category content is not automatically a
finding. Preserve specific source dates in action text and preserve genuine uncertainty.

Contract version: `review-candidates-v1`. Source index: `normalized-physical-lines-v1`.
Sources normalize CRLF/CR to LF and outer whitespace before SHA-256 fingerprinting. Source IDs carry
source type, digest prefix and physical-line position. Blank lines are present in the complete
annotated input but cannot support a candidate. Repeated text retains distinct positions. The index
keeps exact original snapshots/spans and derives only real heading/speaker/timestamp locators.
Changed source snapshots cannot silently bind old IDs. Resolve evidence locally from IDs, never
from candidate prose or provider-supplied quotes.

The final record adds application-owned `ReviewExtractionScope`: automated categories finding/action,
excluded decisions/risks/open_questions/missing_evidence, and `review_outcome_origin=human_completed`.
The scope also carries an application-generated `analysis_fingerprint` over the original candidate
analysis for Delivery migration/reanalysis guards. Do not accept this value from the model.
Excluded collections must stay empty; UI/minutes and work-item descriptions say **Not extracted in
this version; no conclusion about whether such items exist.** Historical full-domain fixtures with
no scope remain legacy examples and must not enter the new analysis path or prefill business fields.

## Existing transport adaptation

The following is a structural sketch. Replace the placeholder HTTP operation with the internal
team's existing client call; do not add a second network operation or copy configuration here.

```python
from architecture_governance_copilot.integrations.aif_candidate_protocol import (
    build_candidate_request_body,
    decode_candidate_tool_response,
)


def analyze(self, request):
    body = build_candidate_request_body(
        model=self.configured_model,
        solution_intent=request.solution_intent,
        review_transcript=request.review_transcript,
        context=request.context,
    )
    envelope = self.existing_http_post_and_decode_json(body)
    return decode_candidate_tool_response(envelope)
```

The request uses full SI/transcript content once, annotated with source IDs, plus confirmed context;
there is no duplicate full-source appendix, summarization or filtering. It sets `stream: false`,
`strict: true`, a named `emit_review_candidates` tool choice and no `response_format`. Model and
configuration come from the caller. The HTTP transport decodes the outer response JSON. The pure
helper expects one choice with `finish_reason: tool_calls`, one function tool of the expected name,
and string arguments decoded once into the candidate object. Null/empty message content is valid;
conflicting prose, refusal, truncation, multiple/ambiguous outputs, unsupported shape and malformed
arguments are not. Ordinary metadata/usage extensions are ignored.

Map timeout, refusal, malformed output, invalid source IDs and provider failure to safe existing
error categories; avoid raw response/error dumps. Confirmed context is owned by the application;
replace old response-context equality with analysis/source/context/provider/version bindings.
Each admitted AIF Analyze attempt makes one transport/model call. Preflight rejection makes none.
No retry, repair model call, alternate parser or fake fallback is part of this path.

## Human review and final conversion

`create_candidate_review_draft(analysis)` creates separate editable state without completing a
`GovernanceResult`. Finding description and action title start with candidate text. Finding title,
severity and status; action priority; and the review outcome require explicit human input. Optional
owner/date/category/recommended-change values start blank. Dates/owners in prose are useful source
context, not automatic structured assignments. Finding status must not inherit the legacy Open
default. Excluded incomplete items do not block completion; reclassification keeps original identity
and evidence, and irrelevant hidden fields cannot leak into the new kind.

At explicit confirmation, `complete_candidate_review(analysis, draft,
allow_reviewer_selected_outcome=...)` returns `CompletedCandidateReview` with `.result`,
`.action_original_indices` and `.action_candidate_ids`. Use the existing deployment policy for the
outcome flag. Non-production human-selected outcomes retain their explicit provenance; standard
production domain rules are not relaxed. Completion performs full domain and original-source
evidence validation before any outputs are stored. Store confirmation/result/outputs atomically.

Required state behavior:

- Revoke old analysis eligibility before a new Analyze attempt, including unchanged-input failure.
- Source/context/provider/contract/index changes invalidate eligible analysis and output state.
- Keep original analysis immutable and complete sources accessible for semantic review.
- Preserve a confirmed snapshot during unsubmitted edits with pending disclosure. Revoke output
  eligibility before an explicit reconfirmation that may fail validation.
- Empty/all-excluded candidates still require explicit outcome and confirmation.
- Preserve success/unknown publication history through ordinary resets and session migration.

## Delivery preservation

Owner, due date, parent, mapped identity/priority, source freshness, exact preview confirmation,
correlation lookup and GET verification remain required. Local artifact generation may succeed with
optional owner/date unknown; Delivery must remain blocked until its requirements are met. Do not
activate a missing real ADO capability simply to complete AIF migration.

Retained actions map back to original mixed-candidate identities/indices. Compact output position is
not delivery identity. Exclusion, reclassification, reordered/reworded reanalysis or changed evidence
IDs must not bypass existing success/unknown records. Reuse a prior binding only when provable;
otherwise require reconciliation for the same source package/target. Do not delete receipts to make
Create available. Only the existing explicitly confirmed local fake new-demo-run operation can
discard simulated history, and never in production or for a real gateway.

## Replays and probe lineage

Use `docs/aif-candidate-probe/implementation-request-v1.json` and its README; it must be
produced by the same request builder, schema and index as the application. The two original probe
files are frozen historical artifacts and use a different raw-text hash. Do not substitute their IDs
into current snapshots or call the new builder request live-tested until it has been sent internally.

The user supplied photographs of one real response with five findings/two actions and visible usage
6,266 input plus 766 output tokens. Two findings contradicted a later Missing Evidence classification;
action text weakened explicit dates to “the proposed date.” The photographs support feasibility but
do not provide raw bytes, HTTP/timing evidence, semantic correctness or app end-to-end acceptance.
A constructed response with the same category-error pattern is a synthetic human-correction test,
not a live golden fixture. If raw response JSON becomes available internally, replay it separately
and record provenance without committing confidential content.

## Observable acceptance stops

1. **Checkpoint/inspection:** identify the internal six-stage entry point and full-domain consumers;
   record preserved transport files/configuration. Stop if the actual call chain is unknown.
2. **No-network contract replay:** run source, candidate, codec and conversion tests; pass synthetic
   envelope replay through the existing adapter seam. Unknown IDs/malformed/refused/ambiguous output
   must fail with no old eligible result, retry or fallback. HTTP/authentication changes are unnecessary.
3. **Real button routing:** an admitted Analyze Review action sends complete sources/context in
   exactly one model call. Confirm that legacy stages/full-domain response validation no longer run.
4. **Human-reviewed local workflow:** valid but misclassified candidates reach review and can be
   corrected/excluded. Complete required fields/outcome, validate evidence, generate consistent
   scoped outputs, and check changed-input and failed-attempt invalidation.
5. **Internal live quality/workflow:** use the final builder and original plus a bounded changed
   synthetic input. Check specific dates, explicit actions, later category clarification and source
   support. Complete human review and the existing authorized Delivery preview/confirm/Create/GET
   sequence, including duplicate protection. Record extraction quality separately from workflow pass.

Run internal regressions with `uv sync`, `uv run pytest`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv build` and `git diff --check`; also run the app and inspect desktop
and narrow routes. Local verification is recorded in Batch 24. **Internal live acceptance: not run
by this external implementation.** Record redacted outcomes in the approved internal system.
