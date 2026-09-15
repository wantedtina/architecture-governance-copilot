# OpenCode internal integration handoff

Updated: 2026-09-15

Document status: `READY_FOR_INTERNAL_PLANNING_HANDOFF`.
Implementation authority: `NONE`.

## Transfer instructions for the user

Use the company-approved transfer mechanism to make the baseline repository and these documents
available on your company MacBook. Do not transfer an external `.env`, `.venv`, credential store,
browser profile, logs or generated recordings. Do not assume the receiving repository has the same
absolute path as the external workstation.

Reviewed main base revision: `67a60da0a528966909269ed06d616003a71e1944` (reviewed `main`).
Its application code/tests/fixtures/dependencies are unchanged from
`81835b9ced0c709f4003522557b6423bc4bdaa18`, the target of
`submission-2026-09-14-final-materials`. Use the newer repository revision for its current layout
and tooling rules; do not reset to the submitted tag merely to match the original handoff.

External handoff workspace:
`/Users/wantedtina/Repos/architecture-governance-copilot-internal-integration`.
External handoff branch: `codex/internal-integration-plan`.
The primary handoff is the committed GitHub branch, containing the application and all six
handoff documents together. Record the exact received commit with `git rev-parse HEAD`; that
handoff commit descends from the reviewed main base above. Do not reset to the base and lose the
handoff documents. A Draft PR is a review entry point, not implementation approval.

After confirming that GitHub access is approved on the company machine, obtain a fresh checkout:

```bash
git clone --branch codex/internal-integration-plan https://github.com/wantedtina/architecture-governance-copilot.git
cd architecture-governance-copilot
git status --short --branch
git log -1 --oneline
git rev-parse HEAD
git merge-base --is-ancestor 67a60da0a528966909269ed06d616003a71e1944 HEAD
```

Compare the received HEAD with the commit recorded in the external handoff message. Stop and
inspect any difference before creating the internal implementation worktree. For an existing
internal checkout, inspect its work and approved remote setup first; do not overwrite it with a
fresh copy or blindly switch branches.

The branch includes these six maintained handoff files:

- `docs/INTERNAL_OPENCODE_START_PROMPT.md` — this receiving-agent prompt and transfer guide.
- `docs/exec-plans/INTERNAL_INTEGRATION_BATCH_01.md` — bounded proposal, decisions, code gaps,
  implementation sequence, tests and acceptance criteria.
- `docs/POST_BASELINE_REFINEMENT_PLAN.md` — planning intake and unchanged `NONE` active pointer.
- `docs/INTERNAL_INTEGRATION_HANDOFF.md` — adapter reference and new handoff navigation.
- `docs/FINAL_STAGE_DEVELOPMENT_PLAN.md` — updated post-submission navigation and priority.
- `docs/INTERNAL_INTEGRATION_REVIEW_2026-09-15.md` — comparison, findings and fresh check results.

Keep Git history and preserve the finalized submission materials. Create the internal worktree
from the verified handoff commit, using an unused `codex/` branch and directory. For a fresh clone
with no local edits, after validating the received revision:

```bash
git worktree add ../architecture-governance-copilot-internal -b codex/internal-integration-implementation HEAD
```

Open that new worktree in OpenCode. Keep internal development, configuration, contracts and evidence
in the approved internal repository/storage. Cloning this GitHub repository does not authorize
pushing internal changes back to it. Only explicitly approved non-sensitive changes may return.

Synchronize with `main` at deliberate handoff or development checkpoints. Inspect incoming changes
and merge required updates with ordinary merges, preserving history and rerunning relevant checks.
Do not automatically move an active internal implementation baseline, rebase a shared branch or
force-push. Record the revision after each accepted synchronization.

The local 15 September ZIP is an earlier document snapshot retained for backup; it is not required
for the GitHub handoff and must not be overlaid onto the newer committed documents. Its manifest
and patch apply only to its declared base and payload. Local ZIPs, output directories and generated
artifacts are not part of the branch. Verify that the received repository has `app.py`, `pages/`,
`src/`, `samples/`, `tests/`, `.streamlit/config.toml`, `pyproject.toml`, `uv.lock` and maintained docs.
Run from the source checkout; a built wheel alone is not this handoff's supported runnable package.

Do not restore old external media paths or regenerate missing ignored videos/PPTs to run tests.
Retain `video/.ruff.toml`, which excludes preserved production sources from active Ruff checks.
No media tool, codec, render engine or presentation dependency is required by the application.

Paste the section below as the first message to OpenCode + GPT-5.4 after opening the internal
repository. It is intentionally read-only/planning first. No credentials belong in the prompt.

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

First read all of `AGENTS.md`, including any applicable instructions in parent/subdirectories.
Identify the repository root. Inspect Git status (including untracked files), branch, HEAD,
upstream, remotes, worktrees and recent history. The reviewed main base is
`67a60da0a528966909269ed06d616003a71e1944`; expect the handoff branch to contain a later
document-only commit. Verify HEAD against the supplied handoff commit and inspect the difference
from that base; the application is unchanged from the finalized `81835b9` baseline. Branch inventories are observations, not instructions to delete branches:
the external review also found `codex/next-stage-review-presentation` at `67a60da` and left it alone.
Inspect locally cached remote state first; confirm
which repository remote operations are approved before fetching from this internal environment.
Report unavailable live synchronization explicitly. If state differs, report the difference and
preserve it; never discard edits, reset hard, rewrite history, force-push or repurpose another
session's branch. Create a separate worktree and `codex/` branch at the verified agreed revision,
using an unused path/name, unless the user already created that isolated worktree from the
verified handoff commit. In that case, inspect and use it without creating a redundant worktree.
The six handoff documents should already be tracked; report missing documents rather than
restoring an older ZIP over current work.

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

- exact code revision and clean/dirty state;
- approved scope, completed phase and unresolved D1–D8 decisions;
- offline/synthetic test and browser results;
- separately authorized live checks and internal evidence references;
- production policy/release decision, including explicit non-acceptance where applicable;
- known Create IDs/correlations, unknown results and reconciliation owner, retained internally;
- next permitted action and any approval still required.

Do not export internal values or evidence bodies back to the external session. An approved
sanitized summary is sufficient for external coordination.
