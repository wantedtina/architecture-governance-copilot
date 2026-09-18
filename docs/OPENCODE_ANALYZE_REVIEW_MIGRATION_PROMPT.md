# Ready instruction for internal OpenCode

Copy the instruction below into OpenCode in the internal repository. Use the final commits listed in
[the migration guide](ANALYZE_REVIEW_CANDIDATE_MIGRATION.md). Model choice does not replace verification.
This instruction is for the already-authorized bounded AIF migration and complete demo, not permission
to add enterprise capabilities or publication targets.

---

Implement the single-call finding/action candidate workflow behind this application's real Analyze
Review button. The goal is a complete demo from confirmed inputs through human review, consistent
outputs and the already-authorized Delivery path, while preserving existing working integrations.

First read `docs/ANALYZE_REVIEW_CANDIDATE_MIGRATION.md`, implementation commits `d143b7c`
(contracts) and `51a70fc` (workflow) on `codex/analyze-review-candidates`, and
repository instructions. Save our own checkpoint of current tracked/untracked integration work.
Inspect the actual internal call chain, including the current six-stage extractor, full-domain
response validators, UI state and confirmation path. Report the precise functions you will adapt.
Do not assume internal files match the external baseline `67a60da`, discard local changes, blindly
merge a whole file, or replace internal `integrations/aif.py` with the external no-network version.

Preserve existing Confluence canonical snapshot acquisition, AIF endpoint/client/authentication/TLS/
proxy settings, ADO gateway and target/owner/parent mappings, and source freshness/reconciliation
checks. Do not add dependencies, frameworks, network clients, extra model calls, retries, response
repair, generic normalization or silent fake fallback. Keep the independent SI-drafting workflow and
production denial of synthetic workflows intact.

Reuse `review_sources.py`, `review_candidates.py`, `candidate_review.py` and
`integrations/aif_candidate_protocol.py` with their required model definitions/tests. Build the
request through `build_candidate_request_body()` using the full current SI, full transcript and
confirmed context. Use the existing HTTP client once. Decode its outer JSON as today, then call
`decode_candidate_tool_response()` and return only the candidate object from `AifTransport.analyze()`.
Require exactly the `items` / `kind` / `text` / `evidence_source_ids` contract; no complete domain result
or structured business fields may come from the provider. Remove the old staged orchestration and
response-normalization path from this Analyze action. Do not run both implementations sequentially.

Keep application-owned context/provider/version/source bindings. Resolve evidence IDs locally to
original quotes/locators and reject the entire response on unknown/stale/duplicate IDs or invalid
shape. Refused, timed-out, malformed, truncated or ambiguous responses must yield safe errors with
no outputs or fallback. Revoke previous analysis eligibility before each Analyze attempt, including
same-input failures. Complete source text must remain inspectable beyond selected citations.

Adapt Human Review to the independent candidate draft. Permit editing, exclusion and finding/action
reclassification while retaining original evidence and stable identity. Require explicit finding
title/severity/status, action priority and review outcome; required selectors start unselected.
Optional owner/date values remain blank until human input even if they occur in candidate prose.
Do not let excluded incomplete items block confirmation or hidden fields leak across kinds.

Only explicit human confirmation may call `complete_candidate_review()` and construct a completed
`GovernanceResult`; run full domain and original-source evidence validation before atomically
storing outputs. Preserve non-production human-outcome provenance without expanding production
policy. Show application-owned scope in UI, JSON, minutes and action descriptions. Decisions, Risks,
Open Questions and Missing Evidence must say “Not extracted in this version; no conclusion about
whether such items exist.” Source traceability is not semantic certification or formal approval.

Preserve the last confirmed snapshot during unsubmitted edits with pending disclosure, but revoke
output eligibility before an invalid explicit reconfirmation. Preserve receipts through ordinary
reset/migration. Map retained actions to original candidate identities; reordered/reworded candidates,
changed source IDs or exclusions must not bypass success/unknown duplicate guards. Where prior
binding is unprovable, stop for reconciliation. Owner/date/parent and exact request confirmation
remain mandatory for Delivery. Do not activate missing ADO capability just to make this task pass.

Work in these observable stages: (1) checkpoint and inspect; (2) no-network protocol/source/candidate
replay; (3) real Analyze button routed to one model call; (4) human correction/completion and scoped
outputs; (5) bounded internal live request and already-authorized Delivery acceptance. Stop at a
failing boundary and fix that boundary within scope. Preserve existing internal configuration while
diagnosing response-shape issues.

Run all repository checks and inspect the rendered desktop/narrow workflow. Test empty candidates,
missing human values, exclusion/reclassification, unknown IDs, malformed/refused/timed-out response,
same-input failure, source-change invalidation and duplicate/unknown Delivery history. Include a
structurally valid five-finding/two-action synthetic response with two excluded-category false
positives; it must reach human review and allow correction, not be rejected by a topic/count rule.

Then use the final builder request with the real internal AIF endpoint on the designated synthetic
input plus one bounded changed variant. Verify exactly one model call, complete inputs, specific
action dates, source-supported classification and no invented actions. Click Analyze Review through
the application, complete human review, inspect every output and perform only the already-authorized
Delivery preview/confirmation/Create/GET sequence. Record semantic quality separately from successful
human correction and end-to-end operation. The prior photographs are observations, not raw golden
JSON or proof that the new request already passed. Do not put credentials or confidential sources
into commits/logs. Finish with actual changed functions, preserved integrations, check results and
any remaining live blockers; do not claim production acceptance from demo success.
