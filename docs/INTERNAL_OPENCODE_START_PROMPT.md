# OpenCode internal integration startup

Updated: 2026-09-15

Document status: `READY_FOR_ADO_INTERNAL_DEVELOPMENT`.
Authority granted by this document: inspection and planning only; no new implementation, service
access, publication or release authorization. Existing explicit internal approvals remain valid
within their recorded scope.

## User operating guide

### Work from the ADO repository

The company ADO repository is the authoritative development workspace. Determine current behavior
from its code and tests, requirements from its maintained internal documents, and authorized work
from the user's internal decisions and sole active execution plan. The external session cannot
verify internal progress or approvals and does not reset them.

GitHub and the earlier handoff are historical sources. Do not routinely inspect the GitHub clone,
compare commit ancestry, require matching hashes, synchronize repositories, or create an import
record as a development gate. Existing provenance notes may remain as history. Consult an older
source only when a specific missing item or question requires it and the user agrees to that lookup.
Missing GitHub history is not an ADO defect.

This revision replaces the earlier instructions requiring source-clone comparison and an import
baseline. Older handoff statements about `NONE`, Deferred requirements, pending decisions and
external test results describe their recorded snapshot. They do not override later approved and
evidenced internal progress. Conversely, code changes or a plan marked active are not by themselves
proof that implementation, live access or production use was approved.

### Prepare the local project once

Open the company ADO project or its existing isolated worktree in OpenCode. Preserve existing
internal edits when incorporating this startup document. Do not copy older planning files over
newer internal decisions. Maintain subsequent plans and this guide inside ADO; routine development
does not require another external handoff update.

Ensure the project has its working application and development inputs:

- `AGENTS.md`, `README.md`, `SPEC.md` and applicable internal instructions.
- `app.py`, complete `src/`, `pages/`, `samples/`, `assets/` and `tests/`, including test fixtures.
- `pyproject.toml`, `uv.lock`, `.python-version`, `.streamlit/config.toml`, `.gitignore` and a
  placeholder-only `.env.example`.
- `docs/POST_BASELINE_REFINEMENT_PLAN.md` and `docs/exec-plans/README.md`.
- The current internal execution plan named by the register, if one exists.
- `docs/exec-plans/INTERNAL_INTEGRATION_BATCH_01.md`,
  `docs/INTERNAL_INTEGRATION_HANDOFF.md`, `docs/FINAL_STAGE_DEVELOPMENT_PLAN.md` and
  `docs/INTERNAL_INTEGRATION_REVIEW_2026-09-15.md`, where retained as proposal/reference material.

If an internal document has replaced one of these references, record the mapping rather than
restoring obsolete instructions. Missing required code, fixtures or authoritative planning files
must be reported and resolved locally. Missing historical media or a source commit is not a reason
to stop unrelated permitted work. Video, slides, course notes and recordings are not integration
dependencies. Retain `video/.ruff.toml` if preserved Python production sources are present there.

Keep `.env`, virtual environments, credentials, local tool state, caches and generated output out
of Git. Use company-approved local skills and package sources. Do not read secret values merely to
check readiness. App startup alone does not establish regression acceptance.

### Start, approve and continue

Paste the complete **OpenCode startup prompt** section below into OpenCode. It covers both a new
planning session and recovery of already approved internal work; no separate override is needed.
Its first checkpoint must identify the actual ADO state and what may proceed under existing approval.

If no implementation batch is approved, the agent prepares the smallest ready bounded plan for
review. It must state affected files, intended behavior, prerequisites, exclusions, tests and
acceptance criteria before requesting approval. After reviewing that concrete plan, the user can
approve its named ready phases and state whether service access is included. Approval of code work
alone does not authorize real requests or production use.

If an approved batch already exists, the agent resumes its unfinished authorized work without
asking the user to repeat valid approvals. Ambiguous or missing approval evidence should result in
one focused clarification, while independent inspection and planning continue. Do not restart
completed work or demand all final production decisions before an independently ready offline fix.

Use these staged acceptance boundaries:

1. **Local foundations and adapters:** approved implementation and applicable contracts; synthetic
   tests, explicit provider wiring, evidence/state guards and publication uncertainty safeguards.
2. **Live read and analysis:** approved targets/data, model route, Confluence/AIF contracts and
   explicit access authorization; validate source/context/evidence and require Human Review.
3. **ADO Create and read-back:** approved mappings, correlation/recovery/audit controls, exact
   request preview and separate human publication confirmation; reconcile uncertainty before any
   possible new attempt. Code or repository-write approval is not work-item Create confirmation.
4. **Production / R9b:** separately accepted outcome authority, evidence, confirmation, audit,
   operating envelope and release authority. A synthetic internal pilot or competition demo does
   not automatically complete production acceptance.

Review the resulting code, tests and internal evidence at each phase. Keep the living plan current
in ADO so the next OpenCode session can recover from repository state and recorded decisions.

## OpenCode startup prompt

Continue company internal integration for this project in the current company ADO repository,
using OpenCode with GPT-5.4 on my company MacBook. Internal integration is the highest-priority
workstream. Communicate in Chinese; use English for files, code, comments, UI, plans, commits and
other deliverables. Preserve finalized submission and presentation materials.

Treat this ADO repository as the authoritative workspace. Use its current code, tests, maintained
internal documents and my explicit internal approvals. Do not routinely read a GitHub clone, compare
GitHub hashes or ancestry, synchronize external repositories, or require an import/provenance
reconstruction before development. Historical handoff references are context only. If a concrete
missing item requires consulting an old source, explain the need and obtain my agreement first.
Do not replace .git, change remotes, merge unrelated histories, force-push or export internal work.

Read all applicable AGENTS.md and company instructions first. Inspect the actual ADO root, branch,
HEAD, status including untracked files, upstream, worktrees and recent relevant history. Preserve
local work and other sessions' changes. Use approved ADO remote access where already authorized;
otherwise use cached state and report its limitation. Never print credentials or credential-bearing
remote URLs. If the opened folder is not the intended ADO project, ask for its internal path rather
than repurposing another repository.

Read the internal POST_BASELINE_REFINEMENT_PLAN register, exec-plans/README, the single referenced
active plan if any, SPEC.md and README.md. Read the retained INTERNAL_INTEGRATION_BATCH_01 proposal,
INTERNAL_INTEGRATION_HANDOFF, FINAL_STAGE_DEVELOPMENT_PLAN and dated integration review where useful;
map any replacements to current internal documents. Identify decisions that have already been
resolved, work completed, remaining tasks and available approval evidence. Do not recreate a second
active plan for overlapping work. Do not overwrite newer internal documents with historical copies.

This startup prompt authorizes inspection and planning, and grants no new application implementation,
live service access, ADO work-item Create or production release permission. Honor existing explicit
internal approvals within their actual scope; do not ask me to repeat them. A reachable endpoint,
configured credential, code change or status label alone is not approval evidence. If an approval
is referenced but its scope cannot be established, ask one focused question and continue independent
permitted work. Do not infer or fabricate an approval.

If the register has an approved active plan, resume its unfinished authorized work. If no plan is
active and approved, keep implementation inactive while preparing the smallest ready bounded plan
for my approval. Do not force the pointer to NONE or restore old requirement states when valid
internal approvals and progress exist. Historical R28/R9b states and external test counts are not
current ADO acceptance evidence. Resolve discrepancies between register, plan, code and recorded
approvals without discarding work. Update governance records to reflect established decisions;
never declare an item Verified merely because implementation has begun.

Use an existing suitable isolated ADO worktree and development branch when available. Otherwise
prepare an independent worktree with an unused codex/ branch from the agreed ADO revision. Check
whether required files are uncommitted: a new worktree will not include them automatically. Preserve
and arrange those changes under the internal policy and existing authorization before relying on
the new checkout. Do not blanket-stage files or commit unrelated edits. An unavailable clean starting
point does not prevent useful read-only analysis.

Check local file completeness and current behavior: app.py, src, pages, samples, assets, complete
tests/fixtures, configuration templates, Python version, pyproject.toml and uv.lock. Use Python 3.12
and uv; do not introduce requirements.txt or a new specification framework. Read approved locally
available Streamlit guidance before application edits; do not claim to have read absent skills.
Inspect tests/configuration before execution and use approved package sources. Keep default tests
free of real enterprise calls. Verify this ADO revision instead of inheriting old external results.

Inspect relevant current provider, deployment policy, model, evidence validation, publication,
governance service and session-state code and tests. The old review describes possible gaps in GET
identity verification, uncertain Create receipts, pre-AIF confirmation, live dependency wiring,
source completeness and correlation/recovery. Recheck whether they still exist; do not reimplement
fixes already completed internally or assume all findings still apply.

Recover the current internal decisions corresponding to D1-D8 in the proposal: runtime/model data
handling, data flows and retention, Confluence contract, AIF contract, ADO process/mappings, review
and outcome policy, audit/recovery/concurrency and release authority. Carry forward resolved decisions
and ask only for what the next phase needs. Confirm the selected OpenCode/model route is approved
for the intended data classification before confidential inspection; a company-network laptop alone
is insufficient. Use approved internal configuration and evidence locations. Ask for safe internal
pointers rather than pasted secrets. Do not read secrets simply to prove they exist, dump environment
values, or disclose raw confidential inputs/provider diagnostics to external artifacts.

The intended bounded slice is designated Confluence SI read, manual transcript/metadata intake,
AIF review analysis, source/context/evidence validation, mandatory Human Review, local outputs,
separately confirmed single-action ADO Create, correlation reconciliation and GET verification.
Preserve existing SolutionIntentDrafter/GovernanceExtractor boundaries, deterministic offline
behavior, strict models and no silent synthetic fallback. Keep review analysis separate from output
generation. Keep app.py as the shared shell/renderers, pages as thin routes, and shared state and
invalidation in ui_support.py.

Do not extend scope into Teams ingestion, ADO Update, Confluence write-back, live drafting, databases,
application authentication, repository discovery, RAG, agent frameworks or production infrastructure
unless a separate explicit internal approval names that expansion. Adapter service authentication
is distinct from adding application login. Preserve samples and update synthetic fixtures with their
validation tests when approved changes require it. Do not alter videos or submission materials.

Sequence work by readiness: complete approved local corrections and adapter tests first; add live
read/analysis only under its established access/data authorization; permit Create only with approved
mappings, operating controls and separate exact-request human confirmation. Obtain any still-required
publication confirmation for the actual request. Do not demand final production release decisions
before every independent offline task. Existing live-test authorization does not imply production
release or permission for different targets/data.

Before live AIF, validate deployment eligibility and the exact confirmed source/input bindings.
Before outputs and delivery, validate the human-reviewed result and its evidence under the approved
policy. Do not carry demo outcome exceptions, fake owner aliases or synthetic parent IDs into live
behavior by assumption. Preserve known remote IDs and uncertain attempts through ordinary resets;
fake new-run cleanup must never clear real reconciliation state. Session loss, an empty lookup or
reanalysis is insufficient proof that no work item exists. Reconcile unknown results before any
possible resubmission and do not claim atomic or exactly-once delivery.

Production R9b requires separately evidenced decisions on outcome authority/provenance, evidence,
reviewer and publisher confirmation, audit retention, recovery, concurrency and release ownership.
Do not inherit demo acceptance as production policy. Preserve any valid internal acceptance already
recorded, but keep unaccepted production capabilities unavailable. A synthetic pilot or competition
demo does not automatically close R9b. If requirements cannot be met within approved scope, report
the exact dependency rather than silently adding a subsystem.

Your first checkpoint should state the current ADO revision/dirty state, current capability truth,
active plan and approval scope, completed work, remaining gaps, and the next permitted action. Then
continue approved work or finish a concrete plan for approval. The plan must name included phases,
affected components, prerequisite decisions, intended behavior, exclusions, tests and acceptance.
Make approval requests only for actual missing decisions or new scope, after doing the permitted
preparation that makes the request reviewable.

After implementation approval, maintain the sole active plan and requirement lifecycle, implement
the approved phases, and record actual validation. Run pytest, both Ruff checks, build and
`git diff --check` as appropriate to the changes under repository instructions; add focused app/state
tests and relevant desktop/narrow browser acceptance for UI/state changes. Keep live tests opt-in
and distinguish synthetic tests, real-browser checks and authorized live acceptance. Record commands,
results, failures and evidence honestly. Preserve local outputs on delivery failure.

At each checkpoint, record the ADO revision, approved scope, completed phase, test results, unresolved
decisions, internal live evidence references, production disposition and next permitted action in
ADO-maintained documents or the approved internal evidence system. Keep confidential values and
known remote IDs/correlations internal. Provide only an approved sanitized summary externally if
needed. When the approved batch is verified, close its plan and update the register accurately;
retain history and any separately deferred work.
