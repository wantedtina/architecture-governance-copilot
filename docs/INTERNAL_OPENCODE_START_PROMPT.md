# OpenCode internal integration handoff

Updated: 2026-09-15

Document status: `READY_FOR_INTERNAL_PLANNING_HANDOFF`.
Implementation authority: `NONE`.

## Transfer instructions for the user

### Current receiving arrangement

The user has cloned `codex/internal-integration-plan` onto the company MacBook and copied selected
project files into a separate company Azure DevOps repository. The GitHub clone is the local source
reference; the ADO repository is the development target. Successful app startup in the ADO copy was
reported by the user, but file completeness, regression results and import provenance still need
verification. Git history was not necessarily imported with the files.

Original published handoff commit: `f7eb8b6e931dafa0dd20bce76235d1d653b4a22e`.
Reviewed GitHub main base: `67a60da0a528966909269ed06d616003a71e1944`.
Unchanged source application baseline: `81835b9ced0c709f4003522557b6423bc4bdaa18`.
The final-materials tag `submission-2026-09-14-final-materials` targets that application baseline.
These are source references, not required ADO commit IDs. Any copied or internally modified files
must be compared before claiming equivalence to the reviewed source application.

### Update the source clone, then copy the maintained documents

Run the following only inside the existing GitHub source clone, using approved GitHub access:

```bash
git status --short --branch
git remote -v
```

Confirm that the checkout is clean, the branch is `codex/internal-integration-plan`, and `origin`
is the expected GitHub source repository. If anything differs, inspect it before proceeding.
Then update without rewriting history:

```bash
git pull --ff-only origin codex/internal-integration-plan
git log -1 --oneline
git rev-parse HEAD
```

Record this source-document revision. Do not run these GitHub update commands in the ADO target,
change the ADO remote to GitHub, or replace the ADO `.git` directory. Do not reset either repository
to an older source commit just to match this document. If the source clone has local edits, retain
and inspect them rather than overwriting them.

Ensure the ADO target contains these seven current files at their repository-relative paths:

- `docs/INTERNAL_OPENCODE_START_PROMPT.md` — this transfer guide and standalone receiving prompt.
- `docs/exec-plans/README.md` — execution-plan lifecycle and recovery rules.
- `docs/exec-plans/INTERNAL_INTEGRATION_BATCH_01.md` — bounded proposal and decision gates.
- `docs/POST_BASELINE_REFINEMENT_PLAN.md` — requirement register and sole active-plan pointer.
- `docs/INTERNAL_INTEGRATION_HANDOFF.md` — adapter reference.
- `docs/FINAL_STAGE_DEVELOPMENT_PLAN.md` — post-submission navigation and priority.
- `docs/INTERNAL_INTEGRATION_REVIEW_2026-09-15.md` — source review findings and verification.

Compare existing ADO documents before copying; merge deliberately if internal decisions or edits
already exist. Never overwrite a newer active plan or company instructions. Retain historical
references where available: `docs/SUBMISSION_BASELINE.md`, `docs/FINAL_STAGE_IMPLEMENTATION_PLAN.md`
and completed `docs/exec-plans/POST_BASELINE_REFINEMENT_BATCH_*.md`. They are evidence, not active
implementation instructions. Course notes and video-production materials are not prerequisites.

Verify the complete application/development set: `AGENTS.md`, `README.md`, `SPEC.md`, `app.py`,
`pages/`, `src/`, `samples/`, `tests/` (including `conftest.py` and `fixtures/`), `assets/`,
`.streamlit/config.toml`, `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore` and a
placeholder-only `.env.example`. Run from the source checkout; a built wheel alone is not the
supported receiving package. Use company-approved Python/package sources for verification.

Local `.env`, `.venv`, caches, tool state, credentials and generated output do not belong in the
ADO import commit. Do not open credential values to check file completeness. `.agents/` is ignored
in the source repository; use approved local guidance if present and report missing references.
Do not copy external environments or credential stores to make the app run. Video, slides and
recordings are not integration dependencies. If preserved Python production sources under `video/`
are copied, retain `video/.ruff.toml`; otherwise no video directory needs to be restored for tests.

### Establish the ADO import baseline

OpenCode should inspect the ADO target first and compare only the relevant approved project paths
against the local GitHub source. Record missing, changed and intentionally omitted files. Do not
scan unrelated company files or infer equality merely from a matching folder name or a working UI.
Keep the source clone as a reference, not a destination for internal changes.

Prepare `docs/INTERNAL_IMPORT_RECORD.md` inside the ADO project with source code/document revisions,
import scope, intentional omissions, local differences, verification results and the ADO import
commit when available. Until comparison is complete, mark provenance unverified. Commit only the
reviewed import/planning files according to internal repository policy; no blanket staging of all
local files. A worktree includes committed content, so do not create one from a target commit that
still omits required copied files. Do not commit another session's edits without authorization.

Create an independent worktree and unused `codex/` branch from the verified ADO import commit,
retaining the ADO history and remote. If an appropriate isolated ADO worktree already exists,
inspect and use it. Do not require shared Git ancestry with GitHub, merge unrelated histories,
force-push, or replace repository metadata.

Synchronize with the ADO mainline at deliberate checkpoints using its actual branch name and
ordinary merges where appropriate. Future GitHub changes are separately reviewed source imports
unless shared ancestry has been established; never treat a GitHub merge command as automatically
applicable to this independently initialized ADO repository. Record each accepted source import
and its corresponding ADO revision. No internal content may return to GitHub without approval.

The older ZIPs are historical local backups. Do not overlay them onto current GitHub or ADO
handoff documents. No new clone, ZIP import, media transfer or history migration is needed simply
to use this revised prompt.

### Start OpenCode in the ADO target

Open the ADO project or its prepared isolated worktree in OpenCode. Paste only the
**Receiving-agent startup prompt** section below, ending before **Expected internal handoff-back
record**. It already includes the independent-ADO context; the earlier conversational override is
no longer needed. Provide the local source-clone path inside the company if requested. Do not put
credentials or internal addresses into this external session.

## Receiving-agent startup prompt

Continue company internal integration planning for architecture-governance-copilot in this
repository. You are running through OpenCode with GPT-5.4 on my company MacBook inside the company
network. The 14 September submission materials are finalized; internal integration is now the
highest-priority development workstream for the final competition demonstration. Preserve the
submitted version and keep any later development revision separately identifiable.
Communicate with me in Chinese. Use English for every file, identifier, code comment,
test, UI label, commit and other deliverable.

Your first task is to validate this handoff, resolve internal prerequisites and finalize the bounded
execution plan for my approval. You are not yet authorized to implement application changes,
connect to real services, invoke AIF on internal content, create ADO items or deploy production.
Do not interpret this prompt, a reachable endpoint, configured credentials or a proposed plan as
authorization for those actions. Do useful permitted inspection before asking for decisions.

Repository context: this is the independent company ADO development target. I have also cloned
GitHub branch `codex/internal-integration-plan` locally and copied selected project files into this
ADO repository. GitHub history may be absent here. Do not require the ADO HEAD to equal a GitHub
commit or require GitHub ancestry checks to pass. If the opened directory is actually the GitHub
source clone, identify it and ask for the local ADO target path before doing target work. Do not
repurpose the source clone or change its remote to guess the intended target.

First read all of `AGENTS.md`, including applicable parent/subdirectory and company instructions.
Inspect the actual ADO root, status including untracked files, branch, HEAD, upstream, remotes,
worktrees and recent history. Preserve existing internal instructions and edits; report conflicts.
Inspect cached remote state first and establish approved remote operations before fetching.
Do not expose credential-bearing remote URLs in reports. Never replace `.git`, reset hard,
rewrite history, force-push, merge unrelated histories or push internal work to GitHub.

Use the local GitHub clone as a read-only reference for this initial investigation. Ask me for
its local path inside the company if unavailable; do not guess it or scan unrelated directories.
The original published handoff is `f7eb8b6e931dafa0dd20bce76235d1d653b4a22e`, based on reviewed
GitHub main `67a60da0a528966909269ed06d616003a71e1944`. Later handoff documentation revisions may
exist; inspect and record the actual source code and document revisions. The source application's
reviewed baseline is `81835b9ced0c709f4003522557b6423bc4bdaa18`. These are provenance references,
not required ADO revisions. Compare the copied project paths before asserting baseline equality.
If a referenced source revision is unavailable, report unverified provenance and continue other
permitted inspection; do not fabricate Git history or claim verification.

Check the seven maintained handoff/process files listed in this document's transfer guide, plus
AGENTS.md, README.md, SPEC.md, application code, pages, samples, assets, complete tests/fixtures,
Streamlit configuration, pyproject.toml, uv.lock, .python-version, .gitignore and placeholder-only
.env.example. Do not inspect .env contents, credential stores, unrelated internal files or media.
App startup alone does not prove import completeness or regression acceptance. Existing external
558-test results describe the reviewed source, not this ADO copy; verify locally before attributing
those results to the target. Inspect tests/configuration before running checks, use approved package
sources, and preserve the initial prohibition on live service calls.

Prepare or update an internal docs/INTERNAL_IMPORT_RECORD.md with the source revisions, copied
paths, omissions, differences and actual verification results. Identify the ADO import commit,
or mark it pending if required files are uncommitted. Keep local configuration, secrets, environments
and generated output out of version control. Do not stage or commit unrelated changes. Follow the
internal repository policy and existing authorization when preparing the import commit. Only after
required files are committed, use the verified ADO baseline for an independent worktree and unused
codex/ branch, unless a suitable isolated target worktree already exists. Continue useful read-only
inspection while import provenance or commit readiness remains unresolved.

Read these documents completely, using chunks if output would truncate:

1. `docs/POST_BASELINE_REFINEMENT_PLAN.md`.
2. `docs/exec-plans/README.md`.
3. `docs/exec-plans/INTERNAL_INTEGRATION_BATCH_01.md`.
4. `docs/INTERNAL_INTEGRATION_HANDOFF.md`.
5. `docs/FINAL_STAGE_DEVELOPMENT_PLAN.md`.
6. `SPEC.md` and `README.md`.
7. `docs/INTERNAL_INTEGRATION_REVIEW_2026-09-15.md`.

The expected active execution plan is `NONE`. R1–R8 and R10–R27 are Verified, R9a is Verified,
R9b is Deferred, and proposed R28 needs decisions. Completed plans and the frozen submission are
historical evidence. This handoff's plan was explicitly requested before implementation approval;
its existence is not an active batch. Preserve `NONE` until I approve a finalized plan. Do not
mark requirements Verified when implementation merely starts.

Validate the proposal against current code and relevant tests, especially:

- `src/architecture_governance_copilot/runtime_dependencies.py` and `models.py`.
- `integrations/confluence.py`, `integrations/aif.py`, `integrations/azure_devops.py` under the
  same package.
- `evidence_validation.py`, `publication.py`, `ui_support.py`, `governance_service.py`,
  `extractors.py`, the existing `SolutionIntentDrafter` boundary and output generators.
- `app.py` shared shell/renderers and thin `pages/` entry points.
- `tests/test_runtime_dependencies.py`, the three integration test modules,
  `test_publication.py`, `test_evidence_validation.py`, `test_models.py`, `test_app.py`,
  `test_ui_support.py` and related provider/generator tests.

Read the repository's Streamlit skill and relevant locally available references before application
edits. The original external directory had a local skill, but `.agents/` is ignored and does not
travel with Git; the isolated worktree had no session-state reference. Locate approved internal
guidance if the skill is absent; do not claim to have read a missing file. Use Python 3.12 and uv, with
`pyproject.toml` and `uv.lock`; do not create requirements.txt or a new specification framework.

Resolve decisions D1–D8 in the proposal with me and the appropriate internal owners. Confirm
the OpenCode/GPT-5.4 route's approved data handling before accessing confidential material, even
though the laptop is on the company network. Establish the approved internal locations for
configuration, contracts, test data, audit records and acceptance evidence. Ask for safe pointers
or configuration references rather than asking me to paste credentials. Do not read credential
values merely to prove their existence or echo environment dumps, cookies, raw provider errors,
confidential source content or internal identifiers into external artifacts. Only sanitized
non-sensitive progress may be returned to the external planning session.

Use the proposal's stage-specific readiness rules: finalize and request approval for the smallest
ready implementation subset; do not make final production release decisions a prerequisite for
all offline adapter work. Before any live pilot, explicitly approve its synthetic-data review
policy and operating controls. Production remains unavailable until production decisions and R9b
are accepted. Progress on the pilot never silently approves later stages.

Keep the implementation bounded to a single governance review round: designated Confluence read,
manual transcript/metadata intake, AIF review analysis, Human Review, local outputs, separately
confirmed single-action ADO Create, correlation reconciliation and GET verification, followed by
the R9b release decision. Use new synthetic inputs for the initial live acceptance. Do not expand
into Teams ingestion, ADO Update, Confluence write-back, live drafting, repository discovery,
databases, application authentication, RAG, agent frameworks or production infrastructure.
Approved service authentication for the three adapters is a separate necessity from adding login.

Preserve deterministic offline behavior, existing provider interfaces, mandatory human review,
strict source evidence, explicit confirmation and no silent synthetic fallback. Keep ordinary
resets from deleting remote reconciliation facts. The new-demo-run cleanup is for in-memory fakes
only. Treat session loss, reset, an empty lookup or changed analysis ordering as insufficient proof
that no remote work item exists. Do not claim atomic or exactly-once publication.

Do not inherit demo/development product decisions as production requirements. Resolve outcome
authority/provenance/evidence, confirmation identity and audit retention explicitly. Do not use
synthetic owner aliases or parent IDs for real ADO mappings. A successful local pilot does not
automatically satisfy production R9b. If durable audit or concurrency requirements cannot be met
within approved scope, keep release blocked and present the exact dependency, rather than adding
an unapproved subsystem.

Your first response should report repository facts, discrepancies, current capability truth and
the smallest set of internal prerequisite decisions needed next. Complete permitted investigation
and revise the proposed plan into a concrete reviewable implementation scope. Ask for my approval
of that scope only after the plan is ready. Keep service access and Create gates explicit; before
an actual Create, present the exact internal target/request and obtain the required separate
publication confirmation. Production release requires its own named authority and evidence.

After I approve implementation, update the register's sole active pointer and lifecycle correctly,
implement the bounded phases and maintain actual evidence in the living plan. Run required tests,
both Ruff checks, build, `git diff --check`, and relevant desktop/narrow browser acceptance. Keep
live tests opt-in and ordinary tests network-free. Record pass/fail and blockers accurately; never
present planned tests or injected responses as natural live-service acceptance. Preserve offline
regression and local outputs on delivery failure. Do not modify video or submission materials.

## Expected internal handoff-back record

At each approval or completion boundary, produce an internal record with:

- exact ADO code revision and clean/dirty state, plus source import/document revisions;
- approved scope, completed phase and unresolved D1–D8 decisions;
- offline/synthetic test and browser results;
- separately authorized live checks and internal evidence references;
- production policy/release decision, including explicit non-acceptance where applicable;
- known Create IDs/correlations, unknown results and reconciliation owner, retained internally;
- next permitted action and any approval still required.

Do not export internal values or evidence bodies back to the external session. An approved
sanitized summary is sufficient for external coordination.
