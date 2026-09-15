# Internal integration handoff review — 15 September 2026

Document status: `COMPLETED_DOCUMENT_REVIEW`.
Application implementation authority granted by this report: `NONE`.

## How to use this historical review in ADO

This report records the external repository review performed on 15 September. All commits, branch
inventories, commands, status labels, findings and test counts refer to that checkpoint. They do
not establish the current ADO implementation or approval state. Use ADO code/tests and maintained
internal decisions for continuation. Reassess findings before adding work; retain internal fixes,
resolved decisions and valid approvals. GitHub history, matching hashes, import records and source
clone comparison are not startup prerequisites. Create worktrees from the agreed ADO revision.
The current [startup guide](INTERNAL_OPENCODE_START_PROMPT.md) supersedes earlier transfer workflows.

## Result

The review updated the external handoff for the then-current layout and post-submission priority,
preserving integration scope and unresolved release decisions. Application code had not changed
since the original handoff. Two publication gaps were reproduced with in-memory fakes during this
review; their current internal status must be established from ADO evidence. No real service was
accessed and no application fix was implemented. This report is evidence for planning, not live acceptance.

## Historical external repository facts

| Fact | Verified result |
| --- | --- |
| Reviewed main revision | `67a60da0a528966909269ed06d616003a71e1944` |
| Original application baseline | `81835b9ced0c709f4003522557b6423bc4bdaa18` |
| Final-materials tag | `submission-2026-09-14-final-materials` resolves to `81835b9` |
| Remote synchronization | `git fetch origin --prune` succeeded; `main...origin/main` ahead/behind `0/0` |
| Original directory | Clean on `main`; preserved |
| Integration worktree | Existing `codex/internal-integration-plan`, fast-forwarded from `81835b9` to `67a60da`; handoff edits preserved |
| Additional observed local branch | `codex/next-stage-review-presentation` also at `67a60da`, checked out in its own worktree; preserved, contrary to the reported two-branch inventory |
| Implementation status | Active execution plan `NONE`; R9a Verified; R9b Deferred; R28 Needs decision |

The three added commits are `7acd709` (versioned media organization), `9cae0d6` (Ruff exclusions for
preserved production sources), and `67a60da` (retired external paths/local archives). The 146 changed
paths are media/archive work plus `.gitignore`, README navigation and production documentation.

`git diff --exit-code 81835b9..main -- app.py src tests pages samples pyproject.toml uv.lock
AGENTS.md SPEC.md docs/POST_BASELINE_REFINEMENT_PLAN.md docs/INTERNAL_INTEGRATION_HANDOFF.md`
returned no differences. This comparison concerns committed `main`; the handoff edits were
working-tree documents at review time and were subsequently published separately. No
media/script/slide source was modified by this review. The command above records a past check;
it is not a command to run in the independent ADO repository.

The user confirmed the submission materials are finalized. The existence of a tag does not by
itself prove every large final artifact is tracked: the new layout intentionally includes ignored
local binaries. Their completeness was not re-audited, and is not an integration prerequisite.

## Historical findings and proposed actions to reassess

| Priority / ID | Finding | Consequence and handoff action |
| --- | --- | --- |
| High / H1 | Old handoff starts from `81835b9` and speaks of preparing the 14 September submission. | The external handoff was updated to that reviewed source. For current ADO work, use its own agreed revision and approved plan; retain these IDs only as historical evidence. |
| High / H2 | The old P0 wording makes all D1–D8 decisions a prerequisite for every implementation phase. | Approve only the ready subset and apply stage-specific gates. A supervised synthetic live pilot may proceed after its own approvals while production remains disabled; it does not complete R9b. |
| High / C1 | GET identity mismatch can be reported as verified success. | Fix identity and trusted URL/revision verification before a live Create; add focused regression coverage. |
| High / C2 | HTTP 500 with a known Create ID is classified as definitely failed and not protected. | Preserve uncertainty and known IDs; stop repeated Create until reconciliation establishes an approved next action. Add status/partial-receipt tests. |
| High / C3 | `_analyze_current_inputs` checks exact confirmed input fingerprint after calling extraction. | Enforce policy, manifest and source eligibility before any real AIF call; current disabled UI alone is insufficient as the live execution boundary. This remains a source-inspection finding. |
| High / C4 | Runtime and rendering still construct only Offline/Internal fake; production is blocked by `drafting_allowed`, and fake gateway construction is in the submission handler. | Explicit live dependency injection and route/capability separation are required. Adding an enum/config value is not sufficient and must never fall through to fake construction. |
| High / C5 | Existing action correlation is session/package-oriented; AIF reordering/evidence changes can change it, and lookup-before-Create is not atomic. | D7 must define reanalysis/restart identity, lookup completeness, unknown-result recovery and publisher serialization. A database or identity subsystem is not silently authorized. |
| Medium / H3 | At review time the handoff was uncommitted; a documents ZIP alone omits the runnable repository and local skills. | The documents were subsequently published. ADO is now the development workspace; no recurring GitHub transfer, source-history comparison or ZIP import is required. |
| Medium / H4 | Legacy adapter prose says zero matches permits Create and assumes uniquely assigned evidence references. | Qualify zero matches with completeness/retained attempts; preserve valid ambiguous quotes without fabricated references and decide production treatment internally. |

Other gaps recorded at the external checkpoint included: Confluence origin/completeness
validation against the deployed contract, exact field-type-aware ADO read-back, human outcome and
evidence provenance, approved audit storage, and live/synthetic state isolation. They have not been
closed by that demo regression suite; current internal resolution is outside this report.

## Targeted reproduction evidence

Both probes used `build_review_runtime(ReviewMode.INTERNAL_FAKE, {"AGC_INTERNAL_FAKE_ENABLED": "1"})`,
the bundled synthetic package, `build_ado_publication_preview`, separate confirmation and
`AdoPublicationCoordinator`. No network transport or company data was used.

### C1 — Mismatched GET ID

1. Produce a valid synthetic Create response for ID `7001` using `InMemoryFakeAdoGateway`.
2. Configure `FakeAdoGateway` to return that Create response, but answer GET for `7001` with the
   same fields/relations and ID/API/browser links changed to `7999`.
3. Call `publish` with the valid preview, confirmation, reviewed result, snapshot and target.

Observed: status `succeeded`, receipt ID `7001`, `verified=true`, despite response ID `7999`.
`publication.py::_verify_known_item` compares fields through `_verification_mismatches`, but does
not compare the returned work-item ID to the requested ID. Required behavior: retain known ID,
reject verification and require reconciliation without another Create.

### C2 — Unprotected partial Create receipt

1. Configure a fake Create response with status `500`, JSON Content-Type and body
   `{"id": 7200, "rev": 1}`.
2. Call `publish` with the same valid bindings.
3. Supply the resulting operation as prior history and call again while the fake correlation
   lookup returns no matches, modelling an incomplete/not-yet-visible lookup.

Observed: first status `definitely_failed`, retained ID `7200`, status absent from
`PROTECTED_PUBLICATION_STATUSES`; a second call enters Create and increases fake Create count to 2.
This is a demonstrated possibility at the coordinator boundary, not a claim that any real service
returned such a response. No UI automation retry or real duplicate was attempted. Required
behavior: classify unresolved outcomes conservatively and protect known IDs independently of an
overly broad HTTP failure classification.

## Historical external verification

Executed in the external isolated worktree on 2026-09-15, using Python 3.12.7 and its lockfile:

| Command / check | Result |
| --- | --- |
| `uv sync --locked --offline` | Passed; environment created from available local cache; no dependency file changes |
| `uv run --offline pytest` | 558 passed in 106.92 seconds, including Streamlit AppTest coverage |
| `uv run --offline ruff check .` | Passed |
| `uv run --offline ruff format --check .` | Passed; 48 files already formatted |
| `uv build --offline` | Passed; wheel and source distribution built |
| `git diff --check` | Passed for the handoff document changes |
| In-memory probes C1/C2 | Reproduced both gaps; no fixes applied |

The `--offline` flag prevents uv package downloads; it is not a network sandbox for Python code.
The inspected tests and probes use the repository's synthetic providers. No company service was
contacted. No fresh desktop/narrow browser acceptance was run because this review changes only
documentation; AppTest coverage is not described as real-browser acceptance. Build success does
not establish wheel-only runtime support; transfer and run the source checkout with its samples.

Document links, whitespace, package hashes and ZIP integrity were checked during external packaging.
These checks and the suite above do not replace validation of the current ADO revision.

## Current internal continuation

The initial GitHub publication and older ZIPs are historical delivery records. Maintain subsequent
plans, implementation and acceptance in ADO. Do not restore old ZIPs, match source hashes, reset an
internal register to NONE or repeat completed work to reproduce this external checkpoint.

Follow the ADO startup guide: inspect current internal state, recover established approval, and
continue its unfinished scope. If no implementation plan is approved, prepare the smallest ready
bounded plan. Resolve only missing prerequisites for the next phase. Real access, exact Create
confirmation and production release retain their respective authorization and evidence requirements.
Public demonstration of internal connectivity or screenshots requires approved presentation/data
boundaries; it does not permit exposing confidential evidence or credentials.

This report grants no new application implementation, real access, write or release approval and
does not revoke valid internal approvals already recorded.
