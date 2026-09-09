# Final-stage implementation plan

Updated: 2026-09-08

**Current execution horizon: the 14 September submission.** Prioritize the verified development
version targeted for 11 September and the four required submission artifacts due 14 September. Prepare
business evidence and material outlines alongside development. This prioritization does not itself
authorize implementation or submission, or silently remove selected requirements.

All post-submission activities are deferred until after the 14 September submission is complete:
feedback-driven development, conference-specific scripts and rehearsals, and Shark Tank pitch,
Q&A, and coaching preparation. Later dates, requirements, and detailed guidance below are retained
as reference only, not active work or prerequisites for submission. Collecting briefing information
now is appropriate; it does not activate those activities. Apply relevant storytelling and business
value guidance now only to the four-minute submission video and key-details write-up.

Status: The split structure is confirmed; implementation details remain under review.
Application development has not been authorized.

## 1. Objective and scope

This plan owns development scope, code behavior, implementation steps, dependencies, tests,
risks, internal integration, and code freeze. Complete judge feedback, narration, specific demo
actions, materials, rehearsals, and materials freeze belong in the
[Presentation and Demo Plan](FINAL_STAGE_PRESENTATION_DEMO_PLAN.md).

Preserve the deterministic offline workflow, improve the human-change summary, persistent
invalidation protection, and evidence/output comparison, and prepare network-free testable
boundaries for Confluence GET → AIF analysis → ADO Create. Work proceeds through dependencies
and acceptance gates, not a day-by-day development schedule.

The 8 September briefing clarifies the timeline: aim to finish development and materials by
11 September, but there is no separate formal checkpoint; submission is accepted throughout
14 September. Keep the same solution/problem statement. SharePoint access will follow, and the
previous repository submission method remains accepted. Preserve a verified version for the
video (at most four minutes), diagram, repository reference, and write-up. Review is 14–17 September,
with feedback on 18 September. No revised submission is required: improvements are demonstrated
on-site on 21–23 September; finalists are announced on 23 September and Shark Tank is on 24 September.
These later activities remain deferred until after submission. Do not invent a midnight/timezone
cutoff from the all-day clarification or treat 11 September as a mandatory code freeze.

All repository content and deliverables must be in English. Prefer Chinese only for session
communication with the user, as required by AGENTS.md.

### Primary improvement and acceptance direction

The original judge feedback is the primary improvement and acceptance direction for this revision:
it initiated the work and determines which changes and demonstration evidence receive priority.
It is not the sole acceptance standard. Organizer submission requirements, engineering/regression
gates, and user-confirmed scope remain mandatory constraints; they must not be weakened to make
an apparent response to feedback. Unrelated work must not displace the feedback response.

Use the following response map during implementation and final review. This is an acceptance map,
not a claim that any step is already complete. Preserve the full feedback in the presentation plan.

| Feedback point | Planned response | Acceptance evidence |
| --- | --- | --- |
| Lead with Human Review; edit an owner and exclude a finding | I2 and the presentation opening | Verified edits/exclusions reach confirmed outputs; demonstrate both actions visibly. |
| Show input changes invalidating outputs | I3 and G1 | Tests and browser demonstration show stale results cannot be revived, including after restoring inputs. |
| Show minutes and ADO items beside cited evidence | I4–I5 and G1 | Source locators/quotes and reviewed values agree across the comparison, minutes, and work-item output. |
| Single frozen scenario limits AI capability | I6–I8 and G3 for the selected live path | New synthetic-input analysis must pass actual provider acceptance; otherwise state the fixture limitation and unfinished live scope explicitly. |
| ADO/Teams are not live integrations | I7–I8 for ADO Create; manual transcript input with optional Teams assessment | Distinguish verified creation receipts from previews. Disclose manual transcript input; Teams API is not mandatory and its deferral is not represented as completed integration. |

At each selected work-package review and submission-version acceptance, record the applicable
feedback point, implemented behavior or presentation response, actual check/demo evidence, and
any remaining limitation or explicit deferral with rationale. Do not silently mark unmet feedback
as satisfied. Praise in the feedback is not a technical guarantee: exact quote validation does
not prove semantic correctness or eliminate hallucinations. Material scope tradeoffs still require
the user's decision. Passing tests alone does not complete the feedback demonstration or submission.

## 2. Independent baseline inspection and corrections

Baseline commit: 56cee29. At takeover, there were no tracked implementation changes, only
untracked planning files. Inspection covered AGENTS.md, README, SPEC, DEMO, dependency
configuration, the complete app.py, all production modules, five route entries, relevant tests,
and all samples. The historical 251 passing tests are not a current verification result.
Rerun baseline verification when development starts.

Preserve the five-stage routes, Existing SI shortcut, provider protocols, Human Review,
analysis/generation separation, strict field validation, and frozen synthetic scenario.

The following independent-review corrections are included in this revised draft, pending
subsequent development authorization:

- Field-schema validation is not runtime quote/locator validation; add a separate source boundary.
- Keep SourceEvidence.reference optional and reuse it without a second evidence-ID schema.
- The first action has only transcript evidence; do not infer its SI section from a related finding.
- The actual finding is Undefined production support ownership; exact demo values belong in
  the presentation plan.
- Restoring an input's original value must not restore confirmation eligibility after invalidation.
- Generating outputs for internal results must not construct DeterministicDemoExtractor and load fixtures.
- Live ADO payloads must not reuse mock descriptions containing a no-item-created statement.
- Source invalidation revokes publication eligibility without forgetting completed or unknown
  remote operations.
- AIF governance analysis is the primary scope; do not add AIF SI drafting.
- The summary and reference display are selected scope, not silently removable optional polish.
- Unchanged proposed demo values do not imply user approval.

## 3. Shared constraints

- Follow AGENTS.md and retain Python 3.12, uv, pyproject.toml, and uv.lock conventions.
- Keep reusable code in src/architecture_governance_copilot/. Keep shell/stage renderers in
  app.py, thin route entries in pages/, and shared state, fingerprints, and reconstruction in ui_support.py.
- Offline operation requires no network, credentials, or enterprise adapters. Never silently
  fall back while labelling results live/AIF.
- Providers propose records. Generate deterministically after human confirmation; publication
  requires separate confirmation. Neither represents formal architecture approval.
- Quotes remain read-only. Edited fields are reviewer overrides, not new source facts.
- Do not globally introduce Pydantic strict=True; preserve date/enum parsing and optional-evidence contracts.
- Missing Information may have no quote; not_stated may have no outcome evidence.
- Company-specific HTTP, authentication, endpoints, deployments, and field mappings are implemented
  internally. The external repository provides protocols, strict boundary models, pure payload
  builders, fake adapters, tests, and searchable TODOs.
- Do not commit secrets, confidential data, internal error payloads, browser state, or large generated media.

New filenames below are suggested locations, not a requirement for a plugin framework,
registry, or general-purpose integration platform.

## 4. Implementation work packages

### Pre-implementation Codex setup checkpoint

**Timing and authorization:** This records agreed preparation guidance for external development
with Codex and GPT-6 Astra. Execute it only after the plan is finalized and the user asks Codex
to perform pre-implementation preparation. Recording this checkpoint does not authorize installs,
configuration changes, commits, environment changes, or application implementation now. Distinguish
preparation authorization from authorization to implement the selected work packages.

1. **Establish the baseline.** Inspect current Git status and preserve all existing work. Include
   the reviewed plans, language policy, and archive changes in an explicitly identified Git baseline
   under the user's subsequent authorization. Use a dedicated development branch; a worktree is
   optional. Do not treat untracked plans or archived handoffs as approved implementation scope.
2. **Verify the local environment.** Retain Python 3.12, uv, pyproject.toml, and uv.lock. Synchronize
   dependencies in the actual checkout/worktree. The Streamlit skill was readable during planning
   but is a symlink into `.venv`; verify its target after setup, especially in a fresh worktree.
   If it is missing, resolve the actual skill availability rather than assuming synchronization
   always restores it. Do not install a duplicate skill when the existing one works.
3. **Choose model settings.** Use the requested GPT-6 Astra where available. Start routine
   implementation at high reasoning effort; consider xhigh for difficult state invalidation,
   evidence validation, or unknown-publication reconciliation. These are project recommendations,
   not model requirements. Recheck available settings at execution time. UI selection is sufficient;
   do not create project configuration merely for completeness or default every task to maximum.
   The coding model choice does not change the application's internal AIF provider contract.
4. **Keep tooling minimal.** Retain the Streamlit skill and use OpenAI Docs when working on
   OpenAI/Codex configuration. Verify one browser automation path can inspect and operate the local
   Streamlit app; existing computer-use tools or Playwright are sufficient. GitHub tooling is
   optional for PR work. External ADO/Confluence/Teams connectors, generic skill bundles, and a
   custom agent harness are not prerequisites. Do not install them speculatively.
5. **Verify before implementation.** Coordinate the baseline commands and normal workflow checks
   with I1, recording actual outcomes once rather than duplicating identical checks. Historical
   test counts are not current evidence. Include real browser navigation and form behavior where
   AppTest is insufficient. Resolve or report existing blockers before changing application behavior.
6. **Use bounded execution.** Select explicit implementation steps and their acceptance criteria.
   Use one agent by default; parallel agent work is optional only when explicitly requested and
   independently bounded. Shared app.py/ui_support.py changes favor sequential work. Complete
   implementation, focused and required checks, and diff review before reporting a work package
   for user review. Preserve the internal-transport boundary and deterministic offline path.

**Execution environment:** Codex, AGENTS.md, this plan, Git, pytest/Ruff, and browser verification
are the intended development loop. No LangGraph, Agents SDK, orchestration service, or memory
database is needed to operate that loop. Do not create a continuously maintained handoff duplicate.

**Validation and risks:** Report the checkout/branch and baseline, environment and skill availability,
selected model settings, browser readiness, actual baseline checks, and remaining limitations.
Avoid losing uncommitted work, broken skill symlinks, conflicting workflow packs, unnecessary
permission expansion, or confusing preparation with implementation authorization.

**Future implementation prompt template:** Replace the selected steps before use. This template
is an example, not a current instruction to begin I1–I2.

```text
Implement steps I1–I2 of docs/FINAL_STAGE_IMPLEMENTATION_PLAN.md.

Read AGENTS.md, the selected plan sections, and the relevant current code
and tests before editing. Inspect git status and preserve existing changes.

Complete the selected scope through implementation, required checks,
and diff review. Preserve the deterministic offline workflow.
Use synthetic data and fake integration boundaries only.

Do not implement later steps, enterprise transports, presentation work,
or archived handoff recommendations.

Ask only when a missing product decision materially affects correctness.
Report what changed, checks actually run, and remaining limitations.

Communicate with me in Chinese. Use English in all files and deliverables.
```

References: [Official AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skill discovery](https://learn.chatgpt.com/docs/build-skills),
[Codex configuration](https://learn.chatgpt.com/docs/config-file/config-basic),
[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), and
[community engineering workflow examples](https://github.com/Phelan164/codex-howto).
Community workflow advice is supporting experience, not a required dependency or performance guarantee.

### I1 — Baseline verification

- **Objective:** Establish the comparison baseline.
- **Files:** Existing tests/, samples/, and relevant README/SPEC implementation-status statements.
- **Behavior:** After development is authorized, run Section 6 commands and inspect inputs,
  reviewed records, minutes, ADO previews, and key transitions through the normal five-stage
  path and the shortcut.
- **Edge cases:** Preserve sample dates and references. Fixture changes require a concrete reason
  and matching test updates.
- **Dependencies:** User authorization to develop.
- **Validation:** Record actual results rather than historical test counts; identify existing
  blocking defects separately.
- **Regression risks:** Rewriting fixtures for presentation purposes or treating untracked plans
  as approved implementation.
- **Out of scope:** Unrelated cleanup, new scenarios, and historical media changes.

### I2 — Normalized Human Review change summary

- **Objective:** Explain which fields human confirmation changed and which items it excluded.
- **Files:** ui_support.py, app.py, test_ui_support.py, and test_app.py.
- **Behavior:** Call build_reviewed_result first. After validation, pair items by original
  collection position, compare normalized retained values, and record outcome/field before-and-after
  changes plus excluded items' original names. Store the summary together with the reviewed result
  and outputs only on success. Show it at the top of outputs, including an explicit no-change state.
- **Edge cases:** Report only exclusion for excluded items. Whitespace/None, dates, and enums must
  not create false differences. Distinguish duplicate titles, recompute on reconfirmation, and
  exclude evidence from the editable comparison surface.
- **Dependencies:** I1.
- **Validation:** Cover every editable field, no changes, all items excluded, invalid dates,
  duplicate titles, unchanged evidence, no old summary after generation failure, and routed form state.
- **Regression risks:** Index shifts after exclusion and old widget values contaminating new analysis.
- **Out of scope:** Reviewer notes, identity, timestamps, exclusion reasons, audit records, and permanent item IDs.

### I3 — Unified invalidation state, notices, and route protection

- **Objective:** Revoke old confirmation eligibility after real input changes and retain an explanation.
- **Files:** ui_support.py, app.py, and corresponding state/AppTest tests.
- **Behavior:** Route SI/transcript/metadata changes through one helper. Clear reviewed results,
  outputs, summaries, and old review-widget values; mark analysis unusable and retain a minimal
  invalidation reason. Show Inputs changed → outputs invalidated and reanalysis instructions
  on Review Inputs/Human Review. Outputs deep links check the same state. Do not show the old
  analysis-success message at the same time.
- **Recovery and edge cases:** Only successful reanalysis or full reset clears the marker.
  Failed analysis and restoration of the original input do not. If no outputs existed, describe
  analysis invalidation accurately. Navigation alone does not invalidate. Unsubmitted review
  edits must not be presented as the confirmed snapshot.
- **Dependencies:** I2; I6 connects source/provider identity to the same mechanism.
- **Validation:** Edit-and-revert, failed analysis, sample reload, missing metadata, deep links,
  Back/Forward, reset, and reconfirmation. Generation/publication remain blocked while invalid.
- **Regression risks:** Widget cleanup timing, redirect loops, and clear_analysis erasing the notice.
- **Out of scope:** Invalidation history, per-field fingerprints, and automatic reanalysis.

### I4 — Shared source and reference validation

- **Objective:** Enforce source guarantees at a provider-neutral runtime boundary.
- **Files:** New evidence_validation.py, a validation wrapper at the analysis boundary, and
  extractor/service/sample tests.
- **Behavior:** Visit outcome evidence and every collection. Each quote must exist in the
  corresponding analyzed text; parsable source locators must match the actual span. Within one
  snapshot, the same nonempty reference cannot resolve to conflicting source/quote/locator values.
  Wrap the existing GovernanceExtractor boundary while preserving its extract signature, service
  delegation, and separation from generation.
- **Edge cases:** Allow valid reference reuse and optional references. Preserve line-ending and
  outer-whitespace compatibility. Do not invent a precise locator when repeated text cannot be
  uniquely located. Retain the Missing Information contract allowing no evidence.
- **Dependencies:** I1; used by I5/I6.
- **Validation:** False quotes, mismatched source/section/speaker/timestamp, conflicting references,
  valid reuse, optional locators, and unchanged fixtures. Do not impose source validation on pure
  generator unit tests that have no source documents.
- **Regression risks:** Tightening schemas enough to break existing models or independent generator tests.
- **Out of scope:** Automatic semantic proof, fuzzy matching, automatic conversion of unsupported
  claims to Missing Information, and a second ID schema.

### I5 — Evidence-to-output comparison view

- **Objective:** Show source quotes, a reviewed action, its actual minutes entry, and its ADO
  preview in one view.
- **Files:** app.py, a small shared entry-formatting function in minutes_generator.py, any necessary
  ui_support.py helper, and corresponding UI/generator tests.
- **Behavior:** Add an action selector and two-column comparison near the top of outputs. The left
  shows direct evidence, references, and locators; the right shows human-confirmed values and
  generated content. Retain full minutes and downloads. Minutes excerpts and full artifacts
  share formatting logic. ADO mapping uses source_action_index in the reviewed collection.
- **Edge cases:** Do not match by title or pre-review index. With no actions, show an empty state
  and optionally a finding-to-minutes comparison without inventing a work item. Handle multiple
  evidence items, duplicate titles, exclusion of the first action, and absent references.
  Excluding a finding does not require its quote to disappear from retained Missing Information.
- **Dependencies:** I2–I4.
- **Validation:** Comparison content matches actual artifacts, owners/references agree, and mapping
  remains correct after exclusion. At 1920×1080, check the existing h4 container-height restriction
  and fixed-submit styling; adjust only affected areas.
- **Regression risks:** Separate excerpt generation drifting from actual minutes or inferring
  nonexistent SI/action relationships.
- **Out of scope:** Full UI redesign, lineage graphs, and invented fixture evidence.

### I6 — External Confluence/AIF boundaries and state wiring

- **Objective:** Exercise the same review workflow using fakes and define bounded internal adapter work.
- **Files:** New integrations/confluence.py, integrations/aif.py, a narrow dependency-wiring module,
  ui_support.py, app.py, and corresponding contract tests.
- **Confluence contract:** get_page returns ID, title, space, version, URL, retrieval time, raw body,
  body format, canonical text, canonicalizer version, and content fingerprint. AIF, quote matching,
  and source display use the same canonical text. Retrieval time does not invalidate content.
  Implement only minimal transformations verifiable with synthetic content externally; never
  silently ignore unknown formats, truncation, or unprocessed content.
- **AIF contract:** Requests include SI, transcript, confirmed metadata, and schema constraints.
  Parse GovernanceResult, check its context against the request, then apply I4. Reject invalid
  responses with recoverable error categories and no sensitive body content. The application assigns
  references after validation, distinguishes SI/transcript namespaces, binds them to source snapshots,
  and reuses references for the same span. Do not trust model IDs or number solely by provider order.
- **UI/state:** Offline is the zero-configuration default. Internal mode is available only when
  configured, and fake operation is explicitly labelled. Only explicit Load/Refresh/Analyze
  actions invoke adapters. Fingerprints include mode, source identity/version/content, canonicalizer
  version, and provider-configuration identity affecting analysis. Switching or load failure must
  not reuse the previous source's eligibility. Output generation neither constructs a fixture
  extractor nor calls a provider.
- **Input edge cases:** Preserve the two-source contract. Supply synthetic transcript and metadata
  explicitly internally; do not mix in unrelated bundled companions. Confluence snapshots are
  read-only, and local edits cannot masquerade as the original page/version.
- **Dependencies:** Offline gate and I4.
- **Validation:** Non-bundled synthetic inputs; zero/one/multiple items; schema/context/quote errors;
  refusal; timeout; source switches; version changes; repeated quotes; no extra calls on ordinary
  reruns; complete offline independence.
- **Regression risks:** Confusing fake/live states, cross-session state leakage, implicit fallback,
  and canonicalization changing references.
- **Out of scope:** AIF drafting, actual HTTP/authentication, Teams, arbitrary page parsing, and
  provider frameworks.

### I6.1 — Confluence read contract refined from internal API samples

Evidence status: the user supplied two initial internal GET samples and a successful follow-up
GET sample with expanded storage body, version, and space.
Only structural observations are recorded here; do not copy screenshots, internal hosts, page IDs,
space identifiers, user metadata, Authorization values, or cookies into this repository.

**Observed, not inferred:**

- `GET /rest/api/content?spaceKey={space_key}&title={title}&expand=version` returned a
  collection with `results`, `start`, `limit`, and `size`, plus page identity and version data.
- `GET /rest/api/content/{page_id}` returned one page object with `space`, `history`,
  `version`, and `_links`. Both samples exposed `_expandable.body`, not actual body content.
- The initial samples used different pages; they do not demonstrate a lookup-to-read sequence
  for the same page.
- The follow-up expansion request returned a nonempty paragraph in `body.storage.value`,
  `representation=storage`, and `version.number` in the same response. Basic body expansion is
  verified for this internal sample. HTTP status and Content-Type headers are not visible.
  Complex structures, version changes, and API writes are not demonstrated by this sample.
- The requests contained both Basic Authorization and cookies. The minimum required authentication
  remains unverified. The exact deployed Confluence edition/version is also unconfirmed.

**Planned read sequence:**

1. Prefer an explicitly configured/selected page ID for the primary vertical slice. A title/space
   lookup is optional discovery, not a required new search UI. If used, encode query parameters,
   respect pagination, report no match, and never silently choose among multiple candidates.
2. Use the content API expansion validated by the internal sample:
   `GET /rest/api/content/{page_id}?expand=body.storage,version,space`.
   Repeat it through the implemented internal adapter during acceptance. The sample demonstrates
   endpoint feasibility, not completion of the application integration.
3. Validate that the response is JSON for the requested page, with `type=page`, an acceptable
   current status, `version.number`, and `body.storage.value` plus `representation=storage`.
   Obtain body and version from that same response, never from different sample requests.
4. Map only necessary fields into the strict application snapshot: page ID/title, space identity,
   version, approved web URL, storage body/representation, application retrieval time, canonical
   text, canonicalizer version, and computed content fingerprint. Do not retain user profiles or
   full history just because upstream includes them. Map the upstream response explicitly rather
   than parsing its entire extensible shape into the strict application model.
5. Preserve the exact storage body separately. Convert supported headings, paragraphs, lists,
   tables, and text deterministically, retaining section and cell boundaries. Validate quotes
   against that canonical text. Storage markup is not plain text; do not strip tags with a regex.
   Detect unsupported macros, embedded content, images, or attachments and block incomplete
   analysis with a clear explanation rather than silently dropping them. Do not add recursive
   retrieval, OCR, or macro execution.
6. Missing body is a retrieval/expansion failure, not proof of an empty page. An explicitly empty
   body on a blank test page differs from a missing body; neither makes a nonempty SI ready for
   analysis. Block analysis on missing/invalid versions, unsupported representation, wrong page,
   authentication redirects returning HTML, or source conversion failure.
7. On explicit refresh, compare page identity, version, canonicalizer version, and content
   fingerprint through the shared invalidation mechanism. A newer response replaces the snapshot;
   do not pair a new body with an old version. Recheck source freshness before live publication.

**Additional validation required internally:**

- During adapter acceptance, inspect HTTP status and Content-Type alongside page identity,
  `version.number`, and `body.storage` representation/value. Basic nonempty paragraph retrieval
  is already evidenced by the follow-up sample.
- Include a heading, paragraph, list, and small table so canonicalization can be designed against
  meaningful structure. The supplied paragraph does not validate these structures or macros.
- If permitted, edit one synthetic sentence, save, and repeat the same GET to verify body/version
  changes. This is a later invalidation acceptance check, not a prerequisite for external planning.
- Verify the deployed version and minimum approved authentication internally; do not assume copied
  session cookies are a durable service authentication contract.

**External fake tests:** single-object versus collection responses; zero/multiple/paginated lookup
results when discovery is implemented; nested storage body; missing versus empty body; wrong page;
wrong representation; missing version; extra upstream fields; HTML login response; structured text
conversion; unsupported macros; unchanged refresh; changed version/body; lookup/read version drift.

The supplied body-response sample is sufficient to refine the read contract and plan external
protocols and synthetic fake tests. No further screenshot is required for planning. Structured
body conversion, authentication, refresh invalidation, and end-to-end live acceptance remain
implementation-time checks in the internal environment.

References: [Atlassian REST expansions](https://developer.atlassian.com/server/confluence/expansions-in-the-rest-api/)
and [Atlassian page-content retrieval](https://support.atlassian.com/confluence/kb/how-to-get-page-content-or-child-list-via-rest-api/).

### I7 — Single-item ADO Create publication contract

- **Objective:** Generate an exact preview deterministically and submit only the separately
  confirmed request.
- **Files:** integrations/azure_devops.py, a small publication-coordination module, ui_support.py,
  app.py, and payload/state/gateway tests. Preserve ado_generator.py's offline mock contract.
- **Behavior:** Build JSON Patch for the selected action from the confirmed model, including target,
  field mappings, evidence, and correlation information. Do not create live payloads by trimming
  mock descriptions. Bind the preview fingerprint to reviewed result, source snapshot, action index,
  target, and mapping. Sequence: preview → validation → separate confirmation → current eligibility
  and source check → single submission → receipt/GET verification.
- **State:** Distinguish not submitted, submitting, succeeded, definitely failed, and unknown result.
  Successful/unknown requests cannot be resubmitted directly. Receipts retain ID, URL, revision,
  correlation, and request binding. Source invalidation revokes current eligibility but retains
  necessary completed/unknown operation results for reconciliation; it does not undo remote items.
- **Duplicate protection:** In addition to session protection, provide gateway correlation lookup
  and reconciliation. After reset/restart, absence of a local record does not prove no publication
  occurred. A changed whole-record fingerprint must not automatically permit recreating the same
  action. Do not promise cross-client exactly-once or add a database. Block live retries until
  reliable reconciliation is available.
- **Edge cases:** Unmapped synthetic owners, non-real parent IDs, and missing required fields block
  publication. Target/mapping/record changes require another preview and confirmation. validateOnly
  is neither a lock nor proof of successful publication.
- **Dependencies:** I6; external tests use explicit fake mappings instead of guessed enterprise fields.
- **Validation:** No writes without human confirmation; preview/send identity; double clicks/reruns;
  unknown results; duplicate correlations; stale sources; mismatched returned fields; preservation
  of local outputs after failure.
- **Regression risks:** Duplicate creation after clearing receipts, mock disclaimers in live items,
  and payload changes after validation.
- **Out of scope:** Bulk publication, automatic Create retries, production projects, and rule bypass.

### I7.1 — ADO Create contract refined from internal API samples

**Evidence:** The user reports successful ticket creation using an account-generated token.
The supplied request uses POST to the work-items collection with a dollar-prefixed, URL-encoded
work item type and `api-version=7.1`, `application/json-patch+json`, and an array of `add`
operations for title and a process-specific classification field. The response contains integer
`id`, `rev`, `fields`, an API `url`, and `_links.html.href`. Record only structural observations;
keep actual targets, identities, token/cookie values, screenshots, and internal field configuration
outside this repository.

The request and response titles differ slightly, and the supplied classification field is absent
from the visible response fields. Preserve the user's reported creation success, but do not treat
these screenshots as exact request/response field verification. HTTP status is not visible.
The returned work item type is process-specific; do not assume the offline mock type or field
mapping is valid for the live target. The sample does not prove classification is mandatory,
that returned default fields must be submitted, or that owner/description/parent mapping works.

- **Objective and dependencies:** Refine I7 payload and receipt handling using this sample;
  retain I6 target configuration, Human Review, and separate publication confirmation.
- **Affected components:** The same I7 payload builder, gateway, publication coordinator,
  configuration contract, and tests; no additional architecture or authentication UI.
- **Intended behavior:** Configure the approved target type and required field mappings internally.
  Encode the type as a path segment with the required dollar prefix. Build the exact JSON Patch
  from the confirmed action and approved mapping; do not copy server-generated identity, state,
  board, or process-default fields from the sample. Required classification values must be
  confirmed against the target process, not inferred from an unrelated sample action.
- **Receipt behavior:** Map the returned ID, revision, API URL, and browser link separately;
  validate target and expected fields through GET read-back. Retain a known created ID even if
  field verification fails. Mark it for reconciliation and block another Create; a mismatch
  must not be treated as proof that no remote item exists.
- **Authentication boundary:** The request shows Bearer Authorization together with cookies.
  Token type and cookie-free authentication remain unverified. Microsoft documents PAT usage
  with Basic authentication; do not infer PAT/Bearer interchangeability or attribute success
  solely to the token. Resolve the approved scheme and test without a cookie jar internally,
  preferably using a read-only request against the already-created synthetic item.
- **Internal acceptance:** Verify the existing item's title and classification field via GET;
  confirm target type, required fields and allowed values, description/evidence formatting,
  owner identity mapping, and parent mapping only where required by the planned action.
  Exercise exact preview/Create/read-back once in the approved synthetic target. Missing required
  mappings block publication. No additional creation is needed solely to resolve screenshot pairing.
- **Tests and edge cases:** Encoded work item type; required custom mapping absent or invalid;
  extra upstream fields; separate API/browser URLs; missing or malformed receipt; known ID with
  mismatched fields or failed GET; token errors; existing unknown-outcome and duplicate protection.
- **Regression risks:** Hardcoding a process-specific type, silently dropping classification,
  assuming a display name is an assignable identity, and creating duplicates after receipt mismatch.
- **Out of scope:** Real credentials or company configuration in external fixtures, bulk creation,
  automatic retries, process customization, and ADO Update before the existing I9 gate.

References: [Microsoft Work Items Create](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/create?view=azure-devops-rest-7.1)
and [Microsoft PAT authentication](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops).

### I8 — Internal handoff and primary live-path acceptance

- **Objective:** Make company-specific implementation bounded adapter work with explicit inputs
  and acceptance checks.
- **Files:** New docs/INTERNAL_INTEGRATION_HANDOFF.md; TODO(INTERNAL-AIF),
  TODO(INTERNAL-CONFLUENCE), and TODO(INTERNAL-ADO) markers in adapters; internal implementation
  and configuration.
- **Behavior:** Map each TODO to a code location, protocol, required internal input, fake test,
  and live acceptance check. Internally implement Confluence GET/canonicalization, AIF transport,
  new synthetic-input validation, then ADO mapping/GET/validation/Create/reconciliation.
  Recheck source version before publication; changes or inability to verify block publication.
  Do not claim this forms an atomic cross-system transaction with ADO.
- **Dependencies:** I6–I7 and internal interface information.
- **Validation:** A previously unbundled synthetic page enters the shared Human Review; invalid quotes
  are rejected; one test item is separately confirmed, created, and its receipt verified; stale,
  duplicate, and unknown-result handling passes; offline works with internal connections disabled.
- **Regression risks:** Body-format/identity-mapping differences, leaked internal errors, and treating
  fake acceptance as live acceptance.
- **Out of scope:** Company transport, endpoints, credentials, or confidential configuration in the
  external repository.

### Optional Teams transcript feasibility assessment

- **Objective:** Assess whether a designated synthetic meeting transcript can be retrieved
  internally. Manual transcript input remains the baseline; this assessment is not a dependency
  of I1–I10, the primary live gate, or code freeze. Discussion and planning do not authorize
  implementing a Teams connector or acquiring additional tenant permissions.
- **Scope and dependencies:** If time permits, use an existing approved internal Graph application
  and authorized access to a completed synthetic meeting with a transcript. Confirm the permitted
  authentication path, tenant transcript-access settings, and applicable access policy or consent.
  If access is unavailable, stop the assessment and retain manual input; do not delay core work.
- **Feasibility validation:** Resolve the designated meeting, list its transcripts, and read one
  explicitly selected nonempty transcript. Verify meeting identity, content format, available
  speaker/time information, and whether the material can support the existing evidence contract.
  A successful GET is feasibility evidence, not full application acceptance.
- **Conditional implementation:** Only reconsider connector scope after feasibility succeeds,
  the primary path is stable, sufficient verification time remains, and the user selects it for
  implementation. Limit the candidate to user-triggered retrieval of a designated meeting.
- **Affected components if selected:** Internal Teams/Graph adapter, source normalization and
  metadata mapping, existing Review Inputs renderer and shared invalidation in ui_support.py,
  plus focused adapter/source/state tests. Choose exact new filenames when scope is approved;
  do not scaffold unused external adapters now.
- **Intended behavior if selected:** Preserve the raw transcript and deterministic source spans;
  let the user confirm the selected source before analysis. Feed the same AIF/Human Review path
  as manual input. Missing speaker identity must remain unknown, never be invented. Unsupported
  source information must produce an explicit validation failure where the existing contract
  requires it. Keep imported-source status distinct from API-retrieved status.
- **Edge cases and tests if selected:** No transcript, multiple transcripts, unsupported or expired
  meeting, denied access, malformed/empty content, missing speakers, multiline timed utterances,
  changed meeting/content, and retrieval failure. Source replacement or changed refresh invalidates
  previous analysis and confirmation without erasing remote publication receipts. Verify the
  manual and deterministic offline paths remain usable with Graph disabled.
- **Regression risks:** Wrong meeting association, lost quote/time boundaries, invented identities,
  stale results, permission delays, and optional work consuming freeze verification time.
- **Out of scope:** Meeting bots, real-time transcription, automatic meeting discovery, event
  subscriptions, background synchronization, Teams message publication, recordings, and automatic
  SI-body revision. Teams remains an optional source-retrieval candidate, not another AI provider.

References: [Microsoft transcript listing and permissions](https://learn.microsoft.com/en-us/graph/api/onlinemeeting-list-transcripts?view=graph-rest-1.0)
and [Microsoft transcript content retrieval](https://learn.microsoft.com/en-us/graph/api/calltranscript-get?view=graph-rest-1.0).

### I9 — Conditional secondary writes

- **Objective:** Retain gated ADO Update and dedicated Confluence review-page write-back.
- **Files:** Internal adapters, existing publication coordination, and corresponding tests.
- **Behavior:** Start only after Create is stable, the user specifies targets, and sufficient
  verification time remains before freeze. ADO Update first reads the revision, shows an exact diff,
  requires separate confirmation, and uses a revision test; conflicts require rereading.
  Confluence write-back has lower priority and targets only a designated synthetic review page.
  Preview title, space, parent, body, target, and version, then separately confirm and check the
  version. Never overwrite the source SI.
- **Dependencies:** Live gate and the relevant internal mappings, targets, and authorization.
- **Validation:** Concurrent version changes, duplicate clicks, incorrect targets, source-page
  protection, and preservation of confirmed records after failure.
- **Regression risks:** Secondary work destabilizing the primary path and blind retries after timeouts.
- **Out of scope:** Automatic synchronization, bulk updates, and source-SI overwrite. Do not expose
  incomplete write controls when gates have not passed.

### I10 — Development verification, documentation, and code-freeze handoff

- **Objective:** Deliver an identified frozen version and verified capabilities for materials preparation.
- **Files:** tests/, README, SPEC, internal handoff, and this plan; application fixes stay within scope.
- **Behavior:** Complete Section 6 verification and the lightweight demonstrability check. Update
  current capabilities, limitations, and operating/configuration instructions. Record frozen commit,
  actual verification results, offline/fake/live eligibility, deferred capabilities, known limits,
  and startup/reset instructions. Separate application work from later presentation/media work.
- **Dependencies:** Offline gate; record external/live status independently without substituting one
  for another.
- **Validation:** Five-stage and shortcut flows from clean sessions; browser Back/Forward, deep links,
  unsubmitted form edits, invalidation and publication guards, and repository hygiene.
- **Regression risks:** AppTest navigation differing from real browsers and documenting unverified
  capabilities as complete.
- **Out of scope:** Narration, slides, formal recording, and final rehearsals, which belong to the
  presentation plan.

## 5. Implementation order and release gates

Order: I1 → I2 → I3 → I4 → I5 → offline gate → I6 → I7 → external-preparation gate →
I8 → live gate → conditional I9 → I10/code freeze.
Add tests with each step rather than postponing them; I10 consolidates final results.

### G1 — Offline gate

- Five stages and the shortcut work without credentials or network access.
- Human field edits and finding exclusions reach the confirmed model, minutes, and ADO previews correctly.
- The change summary is accurate, original evidence is unchanged, and source/output comparisons agree.
- Editing/restoring inputs, failed analysis, and route access cannot revive old confirmation eligibility.
- Source/reference checks pass, no formal approval is implied, and focused/full checks pass.

### G2 — External-preparation gate

- Fake Confluence/AIF/ADO workflows and failure branches are testable offline.
- Mode/source/provider changes and version changes share invalidation logic.
- Quote/context/reference validation occurs before Human Review; generation no longer depends on
  constructing a fixture provider.
- Exact publication previews, separate confirmation, duplicate protection, unknown-result state,
  and reconciliation contracts exist.
- TODOs and internal handoff are complete, without company secrets, configuration, or transport.

### G3 — Internal live gate

- New synthetic sources pass through Confluence/AIF into shared Human Review, and invalid evidence
  is rejected.
- A designated test Work Item is separately confirmed and created; fields, references, ID, URL,
  and revision are verified.
- Stale-source, duplicate-request, and unknown-result handling are verified; the event environment
  supports repeatable success.
- Offline works with internal connections disabled. Passing G2 does not mean G3 passed.

### Submission baseline and feedback refinement

The supplied Shark Tank FAQ confirms that winning solutions still follow normal SDLC and
production processes. Presentation of an investable pilot and production path does not authorize
additional hackathon infrastructure. The ten-minute Shark Tank pitch plus five-minute Q&A is a
presentation constraint, not a change to the four-minute submission video or development scope.
See the presentation plan for the supplied learning material and its project-specific application.

- **Target 11 September:** Aim to complete and verify the submission version and materials. Record its commit,
  gate results, known limitations, and deferred capabilities through I10. G1 remains mandatory;
  show live capabilities only when their applicable G3 checks pass. Freeze this identified version
  for recording and submission when ready; this is an internal practice, not a formal 11 September gate.
- **By 14 September:** Supply the repository reference and verified capability information for the
  four required deliverables in the presentation plan. Repository, diagram, video, and write-up
  must describe the same version. Submission is accepted throughout 14 September; aim to finish
  earlier and use the previous repository submission method. SharePoint link will follow.
- **14–17 September:** Preserve the submitted baseline so judges can reproduce it. Do not silently
  replace submitted artifacts. Any necessary fix needs verification and explicit version tracking;
  no revised submission is required after feedback; keep later changes in the conference version.
- **18–23 September:** Triage new judge feedback against the same problem statement. Propose bounded
  changes and confirm material scope changes with the user. Re-run affected checks and required
  regression gates; maintain a separately identified conference version and matching materials.
  The organizer permits refinement, but this is not authorization for speculative feature additions.
- **21–23 September:** Demonstrate the verified conference version. Choose a final rehearsal and
  operational freeze point once event arrangements are known; do not invent an organizer deadline.

Reassess feasibility before implementation against the shorter deadline. Preserve the planned
scope until the user agrees to material tradeoffs; an unfinished step must remain explicitly
unfinished. I10 must still close the submission version even if optional/live work is deferred.
Teams API exploration, ADO Update, and Confluence write-back must not consume required submission
verification or material-production time. Production estimates are documentation inputs, not a
requirement to build production infrastructure now.

Scope-drop order: keep additional bundled scenarios deferred → Confluence write-back → ADO
Update → extra visual polish → the live presentation path. Retain completed external seams.
Do not silently drop the selected summary/reference display or weaken offline operation,
Human Review, evidence validation, deterministic generation, invalidation, or source-to-output traceability.

## 6. Verification plan

Establish a baseline when development starts. After application changes, run tests and both
Ruff checks. Before freeze, complete:

```bash
uv sync
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Run Streamlit startup/browser verification separately from the other commands. New tests remain
network-free. Fake inputs cover zero, one, and multiple collection items without new bundled demo
scenarios. Preserve existing contracts for permitted empty evidence, optional locators, independent
return values, and no inferred SI sections. Verify actual internal transports only internally.
Check real browser Back/Forward and form navigation; AppTest's explicit switch_page cannot fully
replace those checks.

## 7. Internal inputs and pre-development decisions

- Before development: explicit user approval of implementation scope and authorization to develop.
  Splitting these documents is not development authorization.
- Before the Confluence adapter: Cloud/Data Center, allowed page/space, body format/canonicalization,
  authentication/network requirements, and permission to change/refresh the synthetic page.
- Before the AIF adapter: endpoint/authentication/deployment, request/response and structured-output
  contracts, timeout/retry, proxy/certificate, and telemetry requirements.
- Before the ADO adapter: test target, Work Item Type, required fields, identity/parent/path/tag/
  notification mappings, authentication/network, evidence/correlation destination, and reliable
  reconciliation.
- Before secondary features: whether to include them and their designated targets/operation scope.

Supply internal information internally; it does not block external protocols, fakes, or UI-state
tests. Exact demo names, exclusion candidates, narration duration, and materials format belong
in the presentation plan, not as prerequisites for generic implementation.

## 8. Explicit non-goals

No database/audit history, reviewer notes/identity, second evidence-ID schema, RAG/embeddings/vector
database, agent framework, mandatory Teams/Graph integration, arbitrary repository crawling/execution, AIF drafting,
additional bundled demo scenarios, automatic architecture approval, bulk publication, or production
deployment. Exact quote matching is not semantic proof; do not claim mathematical elimination
of hallucination or cross-client exactly-once. No unrelated cleanup, route migration, Git/media
history rewriting, or unauthorized large-media production. Teams connector implementation remains
outside the committed scope unless the optional feasibility and selection conditions above pass.

## 9. Interface references

Verify the actual deployed versions during internal implementation. Public references do not
replace internal mappings:

- [ADO Create](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/create?view=azure-devops-rest-7.1)
- [ADO Update](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.1)
- [Confluence Cloud pages](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/)
- [Confluence Data Center content](https://developer.atlassian.com/server/confluence/rest/v1000/api-group-content-resource/)

## 10. Submission implementation completion record

I1–I8 and I10 are complete for the 14 September submission baseline. The frozen implementation
and content commit is `ce5fd3f2a760504da40440558180c5245ed291e9`; the canonical release tag is
`submission-2026-09-14-r1`. This immutable revision supersedes the retained
`submission-2026-09-14` candidate after a real-browser form-navigation correction. G1 and G2
passed. G3 was not run because approved live endpoints,
authentication, mappings, and controlled targets were not supplied or added. I9 therefore remains
correctly deferred, and no incomplete secondary-write controls are exposed.

The final environment used Python 3.12.7 with `uv`; `uv.lock` remained unchanged. The complete
verification record, browser scenarios, startup/reset guidance, capability matrix, and known
limits are recorded in [SUBMISSION_BASELINE.md](SUBMISSION_BASELINE.md). That record separates
automated, real-browser, fake-integration, and unperformed live acceptance evidence. Later
presentation/media work and all post-submission conference or Shark Tank preparation remain
outside this implementation freeze.
