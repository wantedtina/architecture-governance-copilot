# Internal integration handoff review — 15 September 2026

Document status: `COMPLETED_DOCUMENT_REVIEW`.
Application implementation authority: `NONE`.

## Result

Update the handoff to the current repository layout and post-submission priority. Preserve the
existing integration scope and unresolved production release decisions. Application code has not
changed since the original handoff, but critical publication gaps remain and two were reproduced
with in-memory fakes during this review. No real service was accessed and no application fix was
implemented. This report is evidence for planning, not live acceptance.

## Repository facts

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
working-tree documents at review time and are now prepared for a separate document-only commit. No media/script/slide source was modified by this review.

The user confirmed the submission materials are finalized. The existence of a tag does not by
itself prove every large final artifact is tracked: the new layout intentionally includes ignored
local binaries. Their completeness was not re-audited, and is not an integration prerequisite.

## Findings and required actions

| Priority / ID | Finding | Consequence and handoff action |
| --- | --- | --- |
| High / H1 | Old handoff starts from `81835b9` and speaks of preparing the 14 September submission. | Start from reviewed `67a60da`, retain the unchanged application/submission baseline separately, and record internal integration as the highest-priority post-submission workstream. |
| High / H2 | The old P0 wording makes all D1–D8 decisions a prerequisite for every implementation phase. | Approve only the ready subset and apply stage-specific gates. A supervised synthetic live pilot may proceed after its own approvals while production remains disabled; it does not complete R9b. |
| High / C1 | GET identity mismatch can be reported as verified success. | Fix identity and trusted URL/revision verification before a live Create; add focused regression coverage. |
| High / C2 | HTTP 500 with a known Create ID is classified as definitely failed and not protected. | Preserve uncertainty and known IDs; stop repeated Create until reconciliation establishes an approved next action. Add status/partial-receipt tests. |
| High / C3 | `_analyze_current_inputs` checks exact confirmed input fingerprint after calling extraction. | Enforce policy, manifest and source eligibility before any real AIF call; current disabled UI alone is insufficient as the live execution boundary. This remains a source-inspection finding. |
| High / C4 | Runtime and rendering still construct only Offline/Internal fake; production is blocked by `drafting_allowed`, and fake gateway construction is in the submission handler. | Explicit live dependency injection and route/capability separation are required. Adding an enum/config value is not sufficient and must never fall through to fake construction. |
| High / C5 | Existing action correlation is session/package-oriented; AIF reordering/evidence changes can change it, and lookup-before-Create is not atomic. | D7 must define reanalysis/restart identity, lookup completeness, unknown-result recovery and publisher serialization. A database or identity subsystem is not silently authorized. |
| Medium / H3 | At review time the handoff was uncommitted; a documents ZIP alone omits the runnable repository and local skills. | Commit the six documents on the handoff branch for GitHub transfer with repository history and a recorded handoff commit. Retain the previously validated ZIP as a historical backup; local skills remain separate. |
| Medium / H4 | Legacy adapter prose says zero matches permits Create and assumes uniquely assigned evidence references. | Qualify zero matches with completeness/retained attempts; preserve valid ambiguous quotes without fabricated references and decide production treatment internally. |

Other source-inspected gaps from the original proposal remain: Confluence origin/completeness
validation against the deployed contract, exact field-type-aware ADO read-back, human outcome and
evidence provenance, approved audit storage, and live/synthetic state isolation. They have not been
implemented or accepted by passing the demo regression suite.

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

## Fresh verification

Executed in the isolated worktree on 2026-09-15, using Python 3.12.7 and the existing lockfile:

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

Document links, authority markers, whitespace, package hashes and ZIP integrity are checked during
packaging. `git diff --check` must also pass at final handoff. Runtime/build artifacts stay ignored.

## Updated handoff and next action

Six documents form the maintained handoff: receiving prompt, bounded proposal, refinement register,
adapter handoff, final-stage navigation index and this report. Following the user's explicit
publication authorization, prepare them for a document-only commit on
`codex/internal-integration-plan`, push that branch and use a Draft PR for review. The receiving
prompt now describes GitHub checkout and deliberate main synchronization. Record the final commit
and publication result in the handoff message; publication does not activate implementation.

The original 11 September ZIP and validated 15 September ZIP remain local historical backups.
The latter includes its manifest, tracked-document patch and synthetic probe results, but predates
the GitHub transfer instructions. Do not overlay it onto the committed branch. No ZIP, generated
output, application change or submission material belongs in this document commit.

Next, transfer through the approved company channel and start OpenCode + GPT-5.4 with the updated
prompt. Resolve internal D1–D5 plus the applicable D6/D7 pilot decisions, obtain approval for the
ready implementation scope and start the bounded phases. D8 and full production D6/D7 remain
mandatory before R9b activation. Public demonstration of internal connectivity or screenshots also
requires approved presentation/data boundaries; do not show credentials, internal URLs, identities
or confidential evidence to the competition audience by implication.

No application implementation, real access, write or release approval is granted by this report.
