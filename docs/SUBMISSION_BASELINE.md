# 14 September 2026 Submission Baseline

Document status: `COMPLETED_BASELINE_EVIDENCE`

Execution authority: `NONE`. This document records what was frozen and verified; it is not a source
of current implementation tasks.

## Identified version

- Branch: `codex/final-stage-i2-review-summary`
- Frozen implementation and content commit: `ce5fd3f2a760504da40440558180c5245ed291e9`
- Release tag: `submission-2026-09-14-r1`
- Scope: I1–I8 and I10 complete; I9 conditionally deferred

The tag identifies this record plus the frozen implementation commit above. It supersedes the
historical `submission-2026-09-14` candidate, which remains unchanged after a real-browser
demonstration exposed a pending-form navigation defect. Presentation, media, conference, and
Shark Tank work are not part of this baseline.

## Gate status

| Gate | Status | Evidence |
| --- | --- | --- |
| G1 — Offline | Passed | Deterministic five-stage and shortcut flows, human edit/exclusion propagation, immutable evidence, change summary, comparison view, input invalidation, route guards, and full automated checks passed without credentials or an LLM API. |
| G2 — External preparation | Passed | No-network Confluence/AIF/ADO fakes, strict adapter contracts, shared validation, exact publication preview, separate confirmation, correlation reconciliation, single-Create protection, GET verification, and safe failure states are implemented and tested. |
| G3 — Internal live | Not run | No approved live endpoint, authentication, mapping, or designated controlled target was added to this repository. Fake results are not live acceptance evidence. |

Because G3 has not passed, conditional I9 ADO Update and Confluence review-page write-back remain
deferred and no controls for those operations are exposed. Microsoft Teams/Graph ingestion also
remains deferred.

## Verification record

Run on 9 September 2026 from the repository root with Python 3.12 and `uv`:

| Check | Result |
| --- | --- |
| `uv sync` | Passed; 54 packages resolved and 51 checked. |
| `uv run python --version` | `Python 3.12.7`. |
| `uv run streamlit run app.py --server.headless true --server.port 8510` | Started successfully; stopped after the startup check. |
| `uv run pytest` | Passed: 368 tests. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed: 37 files already formatted. |
| `uv build` | Passed; source distribution and wheel built successfully. |
| `git diff --check` | Passed. |
| `test ! -e requirements.txt` | Passed. |
| `git diff --exit-code -- uv.lock` | Passed; `uv.lock` is unchanged. |

Real-browser verification used clean local Streamlit sessions and synthetic data:

- The normal Project Context → Draft Solution Intent → Review Inputs → Human Review → Generated
  Outputs path completed successfully.
- The existing-SI shortcut completed successfully. The approved demonstration edit changed the
  first action owner from Alex Chen to Taylor Kim and excluded the Undefined production support
  ownership finding. The change summary, reviewed model, minutes, ADO preview, and
  evidence-to-output comparison agreed; the original evidence remained unchanged and the related
  Missing Information entry remained present.
- Browser Back and Forward preserved the routed workflow state.
- Pending Human Review edits and exclusions survived Back to Review Inputs and Return to Human
  Review without confirming the record or generating outputs.
- Returning from outputs through Human Review to Review Inputs restored both source texts without
  false invalidation. A subsequent substantive SI edit invalidated the old analysis and outputs.
- A clean deep link to `/generated-outputs` safely returned to Review Inputs with recovery guidance.
- The opt-in internal fake path completed Confluence read, AIF analysis, exact ADO preview,
  separate confirmation, one in-memory Create, and GET verification without a network request.
- Browser console inspection reported no warnings or errors in the verified sessions.

Automated `AppTest` coverage additionally verifies unsubmitted review edits, form reconstruction,
stale-input and mode/source/provider invalidation, reset behavior, publication duplicate guards,
and definite-failure and unknown-result states.

## Operation and reset

Required offline startup:

```bash
uv sync
uv run streamlit run app.py
```

Optional fake-integration development startup:

```bash
AGC_INTERNAL_FAKE_ENABLED=1 uv run streamlit run app.py
```

The optional flag enables in-memory fakes only. It does not configure or contact enterprise
services.

Reset and Start New Review clear local workflow state, current analysis, confirmed outputs, and
unsubmitted publication previews. Publication operations that could identify a remote outcome are
retained within the current session for reconciliation. A process restart is never proof that a
real Create did not occur; an internal implementation must reconcile using the recorded
correlation. The current fake gateway is intentionally non-durable.

## Known limits

- Deterministic drafting and extraction support only the bundled synthetic scenario.
- The application has no live Confluence, AIF/LLM, Microsoft Teams/Graph, or Azure DevOps
  transport, credential handling, authentication, database, or audit store.
- Exact quote and locator validation proves source presence and consistency, not semantic truth.
- The workflow supports one active review round and does not compare versions or carry findings
  forward.
- Provider output is always a proposal. Formal architecture approval remains a human Domain
  Architect responsibility.
