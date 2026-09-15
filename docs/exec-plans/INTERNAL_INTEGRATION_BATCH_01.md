# Internal integration — bounded execution proposal

Updated: 2026-09-15

Document status: `PROPOSED_AWAITING_INTERNAL_DECISIONS_AND_USER_APPROVAL`

Execution authority: `NONE`. Active execution plan remains `NONE` in the refinement register.
Included requirements: proposed R28 and deferred R9b; preserve verified R1–R8, R9a, and R10–R27.
Reviewed main base revision: `67a60da0a528966909269ed06d616003a71e1944` (reviewed `main`).
Unchanged application baseline: `81835b9ced0c709f4003522557b6423bc4bdaa18`, also the target of
`submission-2026-09-14-final-materials`. Preserve that submission reference.
The receiving checkout must also include the committed handoff documents; record its exact HEAD
using the [startup instructions](../INTERNAL_OPENCODE_START_PROMPT.md), rather than resetting to
the main base.
See [the 15 September review](../INTERNAL_INTEGRATION_REVIEW_2026-09-15.md) for revision comparison,
reproduced findings and verification evidence.

The user explicitly authorized inspection and preparation of this proposal before implementation
approval. This is a task-specific exception to the creation timing in `exec-plans/README.md`, not
an activation of an implementation batch. Resolve the decision gates below, then obtain approval
of the resulting bounded plan before changing application behavior.

## 1. Ownership and environment

The user confirmed that integration development will run on their company MacBook, locally on the
company network, using OpenCode with GPT-5.4. This external session prepares the handoff only.
Availability of Python 3.12, uv, approved package sources, service permissions, model data handling,
and internal evidence storage has not been established. A company-network laptop is not evidence
that every reachable service, model route, or data category is approved.

The user confirmed on 15 September that the 14 September materials, including code, video, slides
and architecture diagram, are finalized. Internal integration is the highest-priority workstream
for subsequent competition development. This priority authorizes the present review and handoff
update; it does not approve implementation or service access.

The receiving agent owns application code, integration tests, and related product/execution
documentation. Preserve finalized `video/`, recordings, presentation materials, demo scripts and
submission evidence. `main` now contains versioned media archives and local-only artifact indexes;
their presence or missing ignored binaries does not make them integration dependencies.

## 2. Scope and non-goals

Implement one review-round vertical slice, subject to the approvals below:

1. Read one explicitly designated Confluence SI page and retain its complete versioned snapshot.
2. Accept a manually supplied transcript and approved review metadata; confirm the exact package.
3. Analyze that package through the real company AIF transport behind `GovernanceExtractor`.
4. Validate context and source evidence, then require human review and record confirmation.
5. Generate local reviewed outputs independently of delivery.
6. Preview and separately confirm one action's exact ADO Create request, reconcile correlations,
   submit once, and verify the returned work item through GET.
7. Evaluate R9b against explicitly accepted production behavior, evidence, and release authority.

Initial live acceptance uses newly authored, previously unbundled synthetic content in designated
internal targets. It does not authorize confidential production data or general production use.
Retain sequential single-item delivery; no automatic bulk publication.

Non-goals: Teams/Graph ingestion, ADO Update, Confluence write-back, enterprise discovery/search,
live SI drafting, repository ingestion, databases, application authentication, RAG, agent frameworks,
multi-round history, production hosting infrastructure, or submission/media changes. Service
authentication necessary for these three adapters is in the proposed scope; adding user login or
an identity platform is not. Preserve `SolutionIntentDrafter` and the offline drafting path.

## 3. Decisions and dependencies — resolve inside the company

Record actual values and approvals only in an approved internal location. Never request credentials
or confidential contracts in the external session. Named roles below are responsibilities to assign,
not claims that any person has already approved the work.

| ID | Decision / required evidence | Responsible role | Gate |
| --- | --- | --- | --- |
| D1 | Confirm company MacBook tooling, approved repository destination/transfer, package source, local binding, and browser access. Verify the selected OpenCode model route, telemetry, retention, and allowed input classification before exposing internal material to it. | User / internal environment owner | Before sensitive inspection or implementation |
| D2 | Approve data flow from Confluence/manual transcript to AIF and local outputs/ADO. Define permitted synthetic test data, downloads, screenshots, logs, caches, retention/deletion, and internal evidence repository. | Information owner / security authority | Before live access |
| D3 | Confluence deployment/API version, explicit page/space, auth scheme, TLS/CA/proxy, timeouts and size limits, supported storage markup, completeness indicators, trusted URL origin. | Confluence owner | Before transport completion/live read |
| D4 | AIF request/response envelope, deployment/configuration identity, schema support, context preservation, input/output limits, refusal/error semantics, data retention and approved authentication. Do not assume OpenAI API compatibility. | AIF owner | Before transport completion/live analysis |
| D5 | ADO organization/project/type/version, field reference names and types, required/optional owner/date/parent/classifications, authorized assignee mapping, parent verification, description format, correlation field and scoped query permissions. Validate against a designated existing synthetic item. | ADO process owner | Before Create eligibility |
| D6 | Approve a supervised synthetic live-test outcome/confirmation policy separately from production outcome authority, human overrides, evidence, provenance, edit reasons, confirmation identities and audit acceptance; see section 4. | Domain Architecture / product owner | Test policy before live Human Review; production policy before production behavior |
| D7 | Restart/unknown-result recovery, correlation lifetime across reanalysis, concurrent publisher control, and audit record storage under the no-database boundary. Define who reconciles and how release blocks while facts are missing. | Operational / release owner | Before first live Create and R9b |
| D8 | Identify the release authority and the intended deployment/use envelope. Decide whether a supervised single-operator laptop pilot is acceptable, and whether that is sufficient for R9b. | Release authority | Before production activation |

If any prerequisite is unavailable, preserve the unavailable capability and record the blocker.
Do not solve an unavailable authentication/audit/concurrency prerequisite by silently adding an
excluded subsystem. Seek a bounded scope decision internally. No estimate of completion dates is
credible for a phase until its prerequisite decisions have owners and sufficient answers.

### Stage-specific readiness

Do not require final production release decisions before every safe development step. The user may
approve a bounded subset of this plan once its own dependencies are resolved. Record that subset
and exclusions in this plan and the register; never treat later phases as implicitly approved.

- P1 offline corrections require D1 and explicit implementation approval. Adapter work additionally
  requires the relevant D3–D5 contract and approved handling of it; no live call is implied.
- P2 internal read/analysis requires D1–D4, approved metadata and D6's synthetic live-test policy,
  plus explicit access authorization. Keep production disabled while its policy is unresolved.
- P3 live Create requires D5, the applicable D6 confirmation policy and D7's supervised-operation
  audit/recovery/concurrency controls, plus separate exact-request confirmation.
- R9b activation requires completed production D6–D8 decisions and end-to-end acceptance. A
  competition demonstration or internal synthetic pilot may finish without closing R9b.

The exact review-only internal configuration must explicitly distinguish a real transport using
synthetic inputs from the no-network fake. Never reuse a demo label or infer outcome permissions
solely from `development`/`test`. Decide the configuration names internally before implementing them.

## 4. Production policy proposal — requires explicit internal decisions

The following is a proposed acceptance contract, not inherited demo policy:

| Concern | Proposed requirement and decision boundary |
| --- | --- |
| Review authority | The provider proposes analysis only. Input confirmation, reviewed-record confirmation, exact-request confirmation, and formal architecture approval are separate acts. This application does not automatically confer formal approval. |
| Outcome | Extracted stated outcomes retain valid source evidence. Decide whether production permits a human-selected outcome with source evidence only, or with an explicit human attestation/reason when no source statement exists. Until decided, production remains unavailable; do not reuse `DemoReviewedGovernanceResult` as a production exception. |
| Evidence | Validate every quote and supported locator against the exact analyzed snapshot; never trust provider reference IDs. Literal occurrence proves traceability, not semantic support for a changed conclusion. The reviewer must assess support. Decide how repeated/ambiguous quotes and missing-information claims are represented; never invent a unique reference. |
| Human changes | Preserve original proposal, confirmed changes/exclusions, outcome origin, selected evidence, and reasons required by D6. Do not relabel a human edit as a provider/source assertion. Revalidate retained evidence against the confirmed sources before generating production outputs. |
| Confirmations | Bind confirmations to source/manifest, analysis/provider identity, reviewed result, and exact target/request as appropriate. Record operator/reviewer identity and UTC time using an approved internal procedure. A typed display name alone is not authenticated identity. No new login implementation is implied. |
| Delivery eligibility | Use actual approved process requirements. Do not inherit fake aliases, synthetic parent IDs, nullable-date policy, or required field defaults as company rules. Missing mappings block Create while local reviewed outputs remain available under the approved data policy. |
| Audit | Preserve enough approved internal evidence to reconstruct the inputs, analysis, human decisions, exact request, state transitions, and receipt/read-back comparison. Define access, retention, integrity and recovery. A session dictionary or hash without retrievable source evidence is insufficient. |
| Release | Production exposes only accepted live review/delivery capabilities, no synthetic controls or automatic fallback. Drafting remains unavailable in production because live drafting is out of scope. A connection check or synthetic success does not itself authorize production use. |

Minimum internal audit record, with sensitive values retained internally: application revision;
deployment/policy/provider/schema identities; source ID/version/canonicalizer and content hashes;
transcript origin/edit status and hash; review metadata and manifest hash; original analysis;
human changes/exclusions/outcome provenance; reviewer confirmation identity/time; exact request
and preview/binding hash; publisher confirmation identity/time; target/mapping revision;
correlation and attempt identity; pre-submit source freshness; state transitions; known remote
ID/revision; GET comparison; final disposition and reconciliation owner. Define the minimum record
that must exist before Create, and fail closed if it cannot be preserved.

Prefer an already approved internal evidence mechanism and supervised operating procedure if they
satisfy D7. This proposal does not select or implement a new durable store. If the intended release
requires one, leave R9b incomplete until a separately approved solution exists.

## 5. Inspected code and required integration gaps

The code remains unchanged at the reviewed repository revision. The 15 September review reproduced
the wrong-GET-ID and HTTP-500/known-ID findings using in-memory fakes; other rows are source-inspection
findings or pending live-contract requirements. Existing passing tests do not close these gaps.

| Area / anchors | Existing foundation | Required bounded work |
| --- | --- | --- |
| `integrations/confluence.py`: `ConfluenceContentTransport`, `ConfluenceContentApiReader`, `_map_content_api_response` | Explicit content-object GET; body/version/space from one response; canonicalization rejects unsupported macros and incomplete markup. | Implement approved HTTP transport. Validate configured origin/target rather than trusting response links alone. Map actual truncation/completeness signals and reject partial bodies. Existing API mapping does not propagate upstream truncation flags into `ConfluencePagePayload`. |
| `integrations/aif.py`: `AifTransport`, `AifGovernanceExtractor` | Strict schema/context check, safe top-level error categories, local reference assignment. | Adapt the actual wire envelope; enforce bounded requests/responses and sanitized diagnostics, including exception causes/logging. Preserve exact sources and metadata. Repeated quotes may legitimately retain `reference=None`; resolve production policy explicitly. |
| `evidence_validation.py`, `models.py`, `governance_service.py` | Provider-neutral quote/locator validation; provider human-provenance forgery rejected; analysis separate from output generation. | Add the approved production reviewed-result/provenance contract without relaxing provider schema or source validation. Verify human-edited evidence and outcome policy before production output generation. |
| `app.py`: `_analyze_current_inputs` | UI disables analysis until manifest confirmation. | Move/repeat exact manifest and policy eligibility checks before calling a live provider. Currently `current_input_fingerprint` is called when storing the result, after extractor invocation. Test direct/stale calls cause zero AIF requests. |
| `runtime_dependencies.py`: `ReviewMode`, `build_review_runtime`, `configured_delivery_capability` | Only Offline/Internal fake; production has no descriptors; fake capability is fixture-bound. | Add explicit live wiring, independent source/analysis/delivery eligibility and configuration identity. Never extend the generic non-offline branch to construct fakes for a new live mode. No live network calls during imports, ordinary reruns, or readiness rendering. |
| `app.py`: `_enforce_deployment_policy`, `_load_review_source_component`, `_submit_fake_ado_publication` | All production pages blocked; fake gateway constructed in UI; source refresh precedes fake Create. | Decouple review route eligibility from `drafting_allowed`, which currently blocks all production routes. Inject live gateway explicitly; no fake default. Replace fake-only source/intake text and default companions on live routes. |
| `integrations/azure_devops.py`: `AdoGateway`, `parse_work_item_response` | Create, correlation lookup, GET boundary; partial receipt support. | Implement approved service auth, scoped complete lookup and GET. Current parser treats every non-200/201 as definite failure: preserve uncertainty for responses that cannot establish non-creation. A known ID must never permit automatic resubmission even if other response facts are invalid. |
| `publication.py`: `_verify_known_item`, `_verification_mismatches` | Exact preview, separate confirmation, lookup before Create, field/relation comparison, protected status set. | Compare requested/created/read ID, revision consistency and trusted target URLs. Current GET comparison does not check returned ID against the requested ID. Define field-specific equivalence for actual identity objects, dates, tags, description and server relation attributes; never drop a material field to make verification pass. |
| `publication.py`: `_correlation_id`, `publication_correlations` | Original analyzed action positions survive exclusion within the analyzed package; legacy aliases checked. | Establish live identity/reanalysis policy. AIF can reorder or change evidence across analyses, changing correlations. A zero-match query is not a server uniqueness guarantee; serialize approved publishing and handle incomplete/eventually visible lookup and concurrent attempts according to D7. |
| `ui_support.py`: manifest, reset, policy, reviewed-result and publication-history helpers | Resets/migrations preserve reconciliation facts; explicit new fake run alone clears simulated history. | Bind live source/provider/target/policy changes and revoke stale confirmations; keep actual receipts across approved recovery. Do not let live-to-demo transitions retain confidential transcript/metadata in a synthetic session. Protect production/live state from the fake reset path. |

Source freshness comparisons must include approved source origin/space/page/version/canonicalizer/
content identity. `_same_source_snapshot` currently compares only page/version/canonicalizer/content.
Freshness re-read and ADO Create are not atomic; document the residual time-of-check gap and stop on
observed drift, without claiming a cross-service transaction.

## 6. Bounded implementation sequence after approval

### P0 — Internal readiness and scope ratification

Recheck repository truth and baseline on the company machine. Record the status of D1–D8, inspect only approved
internal contracts, and revise this plan with concrete policy choices or explicitly deferred
decisions using the stage-specific readiness rules. The user may approve only ready phases; only
then set this file as the register's sole active execution plan and change the included requirement
to `In progress`. Keep R9b Deferred if only the internal pilot is approved. Keep separate approvals
for live operations and production release. Never require a completed production decision merely
to investigate or implement an independently approved offline correction.

### P1 — Offline-tested foundations and adapters

Implement the scoped validation/uncertainty/identity corrections first with failing synthetic tests.
Add approved transport implementations behind the existing protocols; keep service configuration
and credentials outside Git. Use synthetic, purpose-built wire contracts in public-safe tests.
Separate construction from requests, configure bounded timeouts/size limits/TLS, and prevent
credential forwarding to unapproved redirects. Disable Create retry at client and intermediary
layers. No contract or endpoint is to be guessed from the fake implementation.

### P2 — Review runtime and explicitly approved review policy

Wire live intake and AIF into shared Review Inputs and Human Review. Keep the SI read-only, obtain
manual transcript provenance and approved metadata, confirm the package before AIF invocation,
validate response context/evidence and require human confirmation before output generation.
Implement only the D6 policy approved for the current use envelope. Preserve offline/fake profiles,
production synthetic denial, explicit unavailable capabilities and direct-route/stale-session guards.
Stage live acceptance in the approved internal test configuration, separately from production
release activation; a test profile must not accidentally apply demo outcome policy to live results.

### P3 — ADO readiness, exact Create and reconciliation

Implement approved mappings, complete project/type-scoped correlation lookup and GET first.
Validate the existing designated synthetic item read-only, including actual field representations.
Keep assignee mapping separate from reviewed owner. Revalidate manifest/result/target/mapping,
source freshness and exact confirmation before one controlled Create. Preserve every known ID,
perform GET verification and expose a read-only reconciliation route/procedure for protected
operations; do not retry `unknown_result` through the Create control.

### P4 — Internal live acceptance, then R9b decision

Run the acceptance matrix below with new synthetic inputs and recorded authorization. Produce
internal evidence and a sanitized pass/fail summary. Release authority evaluates D6–D8 and the
exact verified revision before enabling production capabilities. Keep R9b Deferred or In progress
as appropriate if release conditions remain unresolved; do not mark the parent R9 Verified merely
because adapters or fake tests pass. This proposal does not authorize a production deployment.

## 7. Acceptance and test matrix

| Test group | Required checks | Evidence / gate |
| --- | --- | --- |
| Baseline and isolation | Python 3.12/uv; frozen offline fixtures and edited synthetic paths; no internal configuration/import/network required. | Baseline and final suite results; run offline with network calls prohibited. |
| Confluence transport | Explicit approved ID; status/type/version/space/body; login HTML, wrong ID/origin, missing expansion, partial/oversized body, unsupported macros, drift and errors; no credential leakage. | Synthetic HTTP tests, then one approved internal read and canonicalization comparison. |
| AIF | Exact envelope/source/context/schema/config identity; valid novel synthetic inputs reach Human Review; invalid quote/context/refusal/malformed/timeout/oversize rejected; no outputs or fallback on failure; no call before confirmed manifest. | Mock transport assertions and internal success case. Invalid-response injection must be labelled injection, not claimed as a natural provider response. |
| Human review | D6-approved outcomes with/without support, human edits/exclusions and reasons; immutable evidence; no automatic approval/output; explicit confirmations; reanalysis/edit invalidation. | Focused model/service/state tests and desktop/narrow browser checks. |
| ADO lookup/read | Approved existing item, authenticated without reused browser cookies; query scope/escaping/pagination/completeness; zero/one/multiple matches; wrong ID/origin/type/fields/revision/relations rejected. | Synthetic wire tests and separately authorized internal read-only checks. |
| Create | Exact displayed JSON Patch; target/mapping/source freshness; no request without confirmation or with stale binding; one designated Create and GET verification of all material fields. | Internal authorization, operator/time, preview hash, correlation, actual ID/revision and comparison record. |
| Failure/recovery | Pre-Create failure means zero Create calls; ambiguous response/5xx/timeout remains protected; known ID with failed GET retained; rerun/double-click/reset/restart/reanalysis/concurrency handled under D7; local outputs remain accessible. | Deterministic fault tests plus approved internal recovery exercise. No repeated live Create just to provoke failures. |
| Deployment/R9b | Missing/invalid/unaccepted live config blocks; ordinary production UI has accepted capabilities only; no fake controls or fallback; direct-route/stale-session/revoked-policy checks; no confidential data crosses to demo. | Profile matrix, rendered checks and release-authority decision for exact revision/use envelope. |

Update focused tests in `tests/test_app.py` and `tests/test_ui_support.py` for every stage/state
change. Extend `test_runtime_dependencies.py`, `test_confluence_integration.py`,
`test_aif_integration.py`, `test_azure_devops_integration.py`, `test_publication.py`,
`test_evidence_validation.py`, `test_models.py`, and generator/service tests as changes require.
Live tests must be opt-in and absent from the default no-network suite. Read-only acceptance may
use an approved query endpoint even if its HTTP method is POST; distinguish query semantics from
work-item Create and never infer its authorization from implementation approval.

Run from the implementation worktree:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Use `uv run streamlit run app.py` for approved local browser acceptance, with the company's approved
local binding. Verify desktop and narrow views for input order/readiness, Human Review, output
preservation, exact preview/confirmation, success and reconciliation, disabled production, and
offline regression. Stop only the process started for this work; do not interrupt another session.

## 8. Compatibility, rollback and migration

Preserve canonical samples and existing provider protocols. Do not regenerate frozen sample results
from a live model. Add isolated synthetic wire fixtures; update fixture contracts and tests together
only where explicitly needed. Dependencies remain in `pyproject.toml` and `uv.lock`.

If model/session schema or identity changes, explicitly invalidate incompatible local analysis and
confirmations, retaining known remote identities and unresolved attempts in the approved internal
recovery mechanism. Test old fake sessions and live sessions separately. Treat lost session state as
unknown history, not authorization to Create again. Recovery must consult retained evidence and
remote state. Do not claim exactly-once delivery.

Rollback disables live actions and restores a known application revision through normal commits or
configuration. It never deletes remote items, clears uncertain attempts, force-pushes, or rewrites
the verified baseline. Do not push internal configuration, data, or unreviewed internal changes to
the external Git remote. Product documentation changes must describe verified final behavior.

## 9. Progress and verification evidence

- [x] Original `AGENTS.md`, requested maintained documents, and relevant provider/policy/evidence/
  publication/session code and tests inspected on 2026-09-11.
- [x] Original directory clean at supplied baseline; refreshed origin refs and verified upstream
  ahead/behind `0/0`; recent history consistent through Batch 23.
- [x] Separate worktree and branch created at the baseline for external handoff documents.
- [x] Company MacBook and receiving OpenCode + GPT-5.4 role confirmed by user.
- [x] On 2026-09-15, reviewed updated `main`, preserved the old handoff, and fast-forwarded the
  isolated integration branch to `67a60da` without changing application code or submission content.
- [x] Refreshed repository checks and targeted fake-only probes; results in the dated review.
- [ ] D1–D8 completed internally; material policy decisions ratified.
- [ ] Bounded implementation approved and sole active pointer assigned.
- [ ] P1–P3 implemented with required offline/synthetic tests and rendered verification.
- [ ] Authorized live read/analysis acceptance passed.
- [ ] Separately confirmed single Create and GET verification passed.
- [ ] Failure/reconciliation acceptance and offline regression passed.
- [ ] R9b release authority and evidence accepted; product documents synchronized.

The original 11 September planning pass did not rerun application tests. The 15 September follow-up
reruns checks and records fresh results separately in the dated review. Neither pass implements
application changes, connects to company services, performs live writes or claims production
acceptance. The local Streamlit
skill was read in the original directory. `.agents/` is ignored and is not transferred by a Git
worktree; the referenced session-state guide was unavailable in the isolated checkout. Internal
setup must resolve needed guidance before application edits rather than assuming external paths.

## 10. Remaining limitations and completion record

Planning output only. D1–D8, service contracts and all live evidence remain outstanding. The existing
code offers synthetic capabilities, session-local recovery and no durable audit guarantee. This
proposal does not close those gaps, activate R9b, or override the no-database/authentication scope.

Implementation completion: `NOT_STARTED`.
Live acceptance: `NOT_RUN`.
R9b release acceptance: `NOT_RUN`.

At actual completion, record commit, commands/results, browser cases, approved internal evidence
reference and release decision; mark only evidenced requirements Verified and clear the register's
active pointer. If blocked, record the precise dependency and completed phase without overstating
remaining capability.
