# Architecture Governance Copilot

Document role: `CURRENT_PRODUCT_DESCRIPTION`. Current behavior is determined by the checked-out Git
revision, application code, tests, and synchronized maintained documentation. Roadmap language and
historical records do not independently authorize implementation.

Architecture Governance Copilot is a hackathon proof of concept with two independent tasks for
drafting and reviewing a Solution Intent (SI). The drafting workflow turns a synthetic SI template,
selected source-code context, and supporting notes into a human-confirmed Markdown artifact for
manual transfer. The review workflow starts separately from an authoritative, read-only synthetic
SI snapshot, a transcript, and explicit review metadata.

A human Domain Architect remains responsible for reviewing, editing, and making the formal
governance decision. Only a validated, human-confirmed reviewed record generates standardized
review minutes and mock Azure DevOps outputs.
The submission baseline supports the video and repository deliverables due on 14 September 2026.

## Business problem

A Solution Intent is the project's detailed design document, covering areas such as conceptual
and detailed design, deployment, resilience, security, observability, and data. Product Owners
and development teams maintain it while a Domain Architect reviews it over one or more rounds.

Findings, decisions, risks, actions, and questions are often spread across the SI, review
meetings, and governance tracking. Turning those sources into a traceable review record manually
is slow, and findings can lose their SI-section context or supporting evidence.

## Proposed solution

The implemented deterministic Solution Intent Copilot can:

1. inspect a read-only governed SI template and governance metadata, select a repository and
   revision from synthetic inventory, and add editable notes or UTF-8 TXT/Markdown evidence;
2. validate and confirm a fingerprint-bound source-package manifest, then generate a known SI
   draft behind a provider interface;
3. let a human edit, confirm, inspect provenance for, and download that unpublished draft;
4. independently load a versioned authoritative SI snapshot, transcript, and review metadata in
   any order;
5. show component provenance and readiness, then require confirmation of the exact input manifest;
6. analyze the confirmed review package with the deterministic fixture-backed extractor;
7. display the outcome, findings, decisions, risks, actions, open questions, and missing
   information;
8. identify supporting evidence as either SI or transcript evidence;
9. map findings to SI sections where supported;
10. let a reviewer edit fields and exclude proposed items while evidence remains read-only and
    live, unconfirmed change indicators show the affected sections; and
11. validate the human-reviewed record before generating Markdown minutes and mock ADO action
   work items.

The landing page presents two peer workflows. **Draft a Solution Intent** uses **Project Context →
Draft Solution Intent**. **Review a Solution Intent** uses **Review Inputs → Human Review →
Generated Outputs → Work Item Delivery**. Local review completion occurs at Generated Outputs;
delivery is a conditional fourth step with its own status. Each workflow has local progress and reset semantics; neither reports the
other as skipped or complete. A confirmed draft is never silently promoted to an authoritative
review source.
Analysis navigates to `/human-review`, and review confirmation navigates to
`/generated-outputs`. Browser history and Back actions therefore behave like page navigation
while shared session state preserves the current draft and review.

The MVP demonstrates one review round only. It does not compare SI versions, persist review
history, resolve findings automatically, or implement a multi-round workflow.

## Architecture

```text
Synthetic template + source context + supporting notes
                         |
                         v
             SI drafting provider/service
                         |
                         v
              Editable SI draft → Human confirm → Markdown download

Authoritative synthetic SI snapshot + transcript + review metadata
                         |
                         v
             Confirmed review-input manifest
                         |
                         v
                    Streamlit UI
                         |
                         v
                 Governance service
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
Extractor provider                 Pydantic models
  - deterministic default            - review context
  - opt-in internal fake              - findings and evidence
                                      - decisions, risks, actions
        |                                 |
        +----------------+----------------+
                         |
             +-----------+-----------+
             v                       v
       Review minutes          Mock ADO previews
                                      |
                           guarded fake Create
```

The deterministic extractor is the required offline demo path. It validates the bundled
SI/transcript pair and review metadata, then returns an independent copy of the known structured
result. It supports only this frozen synthetic scenario and does not perform semantic extraction
of arbitrary text. Pure deterministic generators now transform a validated result into Markdown
review minutes and typed mock ADO action work items. `GovernanceReviewService` intentionally
keeps analysis separate from output generation so the Streamlit UI can place human review and
editing between them. Explicit session state holds only the current one-round inputs, analysis,
reviewed record, generated outputs, stale-input fingerprint, and active route stage; there is no
database.

An opt-in internal fake mode exercises Confluence read, AIF analysis, and guarded ADO Create
contracts entirely in memory without network access. Its separate Synthetic Order Routing Service
package contains a 1,083-word SI, a 28-line four-participant transcript, and representative
nonempty findings, decisions, risks, actions, questions, and missing evidence. It is an
integration-development aid, not evidence of live enterprise connectivity or general semantic
extraction. Microsoft Teams ingestion and every real transport remain deferred.

See [SPEC.md](SPEC.md) for the complete domain and technical design and [DEMO.md](DEMO.md) for
the planned recording flow.

## Repository structure

```text
architecture-governance-copilot/
├── app.py
├── pages/
│   ├── solution_intent_drafting.py
│   ├── review_inputs.py
│   ├── human_review.py
│   ├── generated_outputs.py
│   └── work_item_delivery.py
├── pyproject.toml
├── uv.lock
├── README.md
├── SPEC.md
├── DEMO.md
├── .gitignore
├── src/
│   └── architecture_governance_copilot/
│       ├── __init__.py
│       ├── models.py
│       ├── extractors.py
│       ├── governance_service.py
│       ├── si_drafting.py
│       ├── ui_support.py
│       ├── minutes_generator.py
│       ├── ado_generator.py
│       ├── evidence_validation.py
│       ├── publication.py
│       ├── runtime_dependencies.py
│       └── integrations/
│           ├── confluence.py
│           ├── aif.py
│           └── azure_devops.py
├── samples/
│   ├── si_template.md
│   ├── source_context.txt
│   ├── supporting_context.md
│   ├── solution_intent.md
│   ├── review_metadata.json
│   ├── review_transcript.txt
│   └── expected_result.json
└── tests/
    ├── test_models.py
    ├── test_sample_data.py
    ├── test_extractors.py
    ├── test_governance_service.py
    ├── test_si_drafting.py
    ├── test_ui_support.py
    ├── test_app.py
    ├── test_minutes_generator.py
    ├── test_ado_generator.py
    ├── test_evidence_validation.py
    ├── test_confluence_integration.py
    ├── test_aif_integration.py
    ├── test_azure_devops_integration.py
    └── test_publication.py
```

The samples freeze one fully synthetic Digital Payment Notification Service review scenario.
Automated tests validate its metadata, model compatibility, evidence quotes, scenario
cardinality, and basic data safety.

## Setup and commands

Prerequisites:

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/)

Synchronize the environment:

```bash
uv sync
```

Run the Streamlit application:

```bash
uv run streamlit run app.py
```

The PoC deliberately uses one project-level light theme. It remains light when the browser or
operating system prefers Dark mode; there is no supported in-app theme switch. Dark-mode support
may be reconsidered only as a separately approved future refinement.

The local demo uses a 0.4-second pause for each visible processing phase, producing an
approximately 0.8-second transition after SI confirmation and 1.2-second transitions after
Analyze and reviewed-record confirmation. To rehearse with a different per-phase delay:

```bash
AGC_DEMO_STEP_DELAY_SECONDS=0.6 uv run streamlit run app.py
```

Use `AGC_DEMO_STEP_DELAY_SECONDS=0` to disable transition pauses.

The deterministic offline path is the required submission path and needs no environment
configuration. To exercise the explicitly labelled, no-network integration fakes during
development:

```bash
AGC_INTERNAL_FAKE_ENABLED=1 uv run streamlit run app.py
```

This flag enables only in-memory fakes. It does not accept credentials or connect to Confluence,
AIF, Microsoft Teams, or Azure DevOps.

### Local environment file

To keep local settings together, copy the committed template once, only if you do not already
have a local `.env`:

```bash
cp -n .env.example .env
uv run --env-file .env streamlit run app.py
```

The template uses `demo` with fake disabled. For local fake development, change these two values
in `.env` together:

```dotenv
AGC_DEPLOYMENT_PROFILE=development
AGC_INTERNAL_FAKE_ENABLED=true
```

The template also documents the optional processing delay and fake provider identity. Restart the
application after editing `.env`. The application does not automatically read this file; `uv`
loads it only when requested with `--env-file`. Existing shell environment variables take precedence
over file values, so unset conflicting exported `AGC_` settings before using the file.

Keep `.env` local; Git ignores it and `.env.*` except the documented `.env.example` template.
Commit only synthetic defaults and comments in the template, never credentials or confidential
values. Plain `uv run streamlit run app.py` remains the zero-configuration offline entry point
when no overriding environment is set. No additional dotenv dependency is required.

### Deployment profiles

Set `AGC_DEPLOYMENT_PROFILE` before starting the process. Restart after changing configuration;
there is no in-app policy editor. The validated policy is checked before every routed workflow and
provider action. Training uses a separate demo deployment.

| Profile | Offline review / synthetic drafting | Internal fake | Current production capability |
| --- | --- | --- | --- |
| `demo` (default) | Available | Not allowed | None |
| `development` | Available | Explicit fake flag required | None |
| `test` | Available | Explicit fake flag required | None |
| `production` | Disabled | Not allowed | Unavailable until separately approved live acceptance |

With no profile and no enabled fake flag, launch remains the zero-configuration demo. The existing
`AGC_INTERNAL_FAKE_ENABLED=1` command without a profile resolves to development. An explicit demo
or production profile combined with an enabled fake flag fails configuration validation.

Boolean settings accept `1/true/yes/on` and `0/false/no/off`, ignoring surrounding whitespace and
case. An absent fake flag is false. Explicit blank/unknown profiles or booleans fail closed; an
explicit blank `AGC_INTERNAL_FAKE_PROVIDER_ID` is rejected when fake is enabled. Diagnostics do not
print environment dumps. Only development/test can enable fake; the flag alone never connects a
real service.

Production currently shows **Production capabilities unavailable** and offers no synthetic input,
draft, analysis, confirmation, export, or delivery controls, including through direct page URLs.
This is a verified policy foundation, not live integration acceptance or production readiness.
Invalid configuration instead shows **Deployment configuration error** with operator guidance.

One allowed review mode is shown as capability status; a selector appears only when both modes
are allowed. If an existing mode is removed, incompatible inputs, outputs, and confirmations are
revoked and the user must explicitly start an allowed review. There is no automatic Offline
fallback. Compatible independent drafting work and protected session-local delivery facts are
retained; production invalidates both synthetic workflows and hides their controls. Changing the
provider identity invalidates its bound review package. A new process may lose all session state;
this is not durable recovery or proof that a prior Create did not happen.

Run tests:

```bash
uv run pytest
```

Run lint checks:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

The drafting flow is: **Draft a Solution Intent → Open Demonstration Project → select authorized
sources → inspect the exact Selected Source Package manifest → Confirm Context & Continue →
Generate SI Draft → human edit/confirm → inspect provenance or download Markdown**.

The review flow is: **Review a Solution Intent → load the authoritative SI, transcript, and metadata
in any order → Confirm review input manifest → Analyze review → edit or exclude items → Confirm
Reviewed Record & Generate Outputs**.
The application uses a synthetic workspace. Drafting accepts custom Evidence through offline
topic grouping; governance review remains fixture-bound. Human draft edits are preserved in the drafting workflow, but the deterministic offline
extractor can analyze only its unchanged authoritative SI snapshot and the fake AIF path accepts
only its separate fixed package; arbitrary SI analysis requires a future approved provider.

## Governed work-item delivery

Generated Outputs remains complete and downloadable independently of delivery. Choose
**Continue to Work Item Delivery** to inspect the conditional fourth review step. Offline reports
**Unavailable** because no delivery provider is configured for its package; a review with no
confirmed actions reports **Not applicable**.

The opt-in Internal fake capability is bound to the exact confirmed synthetic source, provider,
transcript, metadata, and configured target. Each reviewed action shows its owner, mapped assignee,
nullable due date, priority, parent, and readiness blockers before request preparation. Review
ownership remains flexible; an unmapped owner blocks that action and provides **Back to Human
Review** for correction and renewed confirmation. Parent and target mappings are read-only.

Select one action independently of the Generated Outputs evidence comparison, then use
**Preview Azure DevOps request → Confirm request → Create work item**. Peer **Work item summary**
and **Request JSON** tabs expose the same prepared request, including all outgoing fields,
relations, correlation, and binding fingerprints. Create reconciles correlations first, submits
at most once per protected operation, and verifies the known identifier with GET. Each action has
its own receipt; another ready action may be delivered separately. Succeeded, submitting, and
unknown results block direct resubmission. Failed and unknown delivery do not erase local artifacts.

Original analyzed action positions survive exclusions for delivery correlation, while local output
indices remain compact. Legacy compact-position correlations are also checked so retained history
cannot silently lose duplicate protection. Changing a selected action or any bound result, source,
target, or mapping revokes the active request confirmation. Human Review action dates use a nullable
calendar control and an explicit **Clear due date** action; clearing preserves `None`, and no business date horizon is imposed.

All delivery remains in-memory and no-network. Session history is not a durable audit store;
process restart cannot establish whether a prior remote operation occurred. Formal architecture
approval remains a human responsibility.

## Current implementation status

**The deterministic routed PoC workflow is the verified 14 September submission baseline.**

Implemented:

- strict SI-drafting request/result models and a `SolutionIntentDrafter` provider protocol;
- a deterministic offline drafter for the bundled template, source excerpts, and supporting
  notes;
- a production-shaped Project Context stage with controlled authorized selection, exact resource
  identities and SHA-256 fingerprints, deterministic local validation, provider compatibility, and
  explicit source-package manifest confirmation;
- a first-class routed drafting stage with editable human confirmation;
- independent drafting and review workflow entry points with local progress and scoped reset;
- a human-confirmed, downloadable draft with provenance and no review-source handoff;
- a read-only, named, versioned authoritative synthetic SI snapshot;
- order-independent transcript and metadata intake with per-component provenance and readiness;
- exact review-input manifest confirmation before analysis;
- strict Pydantic models for one SI review round;
- SI lifecycle and review outcome enums;
- typed SI/transcript evidence;
- Solution Intent review metadata;
- SI-section-aware review findings;
- existing decisions, risks, actions, questions, and missing-information models;
- enriched mock ADO work-item preview fields;
- comprehensive model validation tests;
- a 1,136-word synthetic Solution Intent and 32-line matching review transcript;
- a distinct 1,083-word Internal fake SI and 28-line matching transcript with representative
  coverage across every review collection;
- validated review metadata, expected governance result, and evidence-consistency tests;
- a synchronous `GovernanceExtractor` protocol; and
- a fixture-validated `DeterministicDemoExtractor` for offline tests and the primary demo;
- deterministic Markdown SI review-minutes generation; and
- typed mock ADO work-item generation with no external request;
- an immutable `GovernanceOutputs` bundle; and
- `GovernanceReviewService`, with separate analysis and reviewed-result generation stages;
- two bounded route hierarchies, versioned session state, and stale-analysis protection;
- one deliberate project-level light theme for consistent native and branded surfaces;
- editable human review with live pending-change and validation awareness, item exclusion, a
  normalized confirmed change summary, and read-only evidence;
- exact source-quote and supported-locator validation before Human Review;
- unified input, mode, source-version, and provider-identity invalidation;
- an evidence-to-output comparison joining source quotes, the confirmed action, its minutes entry,
  and its generated ADO preview;
- purpose-labelled rendered, editable, and exact-source Markdown views across drafting, review,
  and generated records, with safe structured-value interpolation;
- Azure DevOps work-item preview cards with exact JSON and request payload views; and
- an explicit completed-workflow panel with artifact counts and a safe **Start New Review**
  reset; and
- pure UI-support tests plus Streamlit `AppTest` workflow coverage;
- fake-only Confluence, AIF, and ADO boundaries with recoverable error contracts; and
- an exact ADO JSON Patch preview, separate confirmation, correlation lookup, single fake Create,
  GET verification, duplicate protection, and unknown-result handling.

Not yet implemented:

- general-purpose drafting from arbitrary repositories or documents;
- source repository cloning, scanning, or code execution;
- real Confluence retrieval or SI publication;
- a production enterprise LLM drafting provider;
- real AIF/LLM extraction;
- real ADO authentication or Create;
- Microsoft Teams or Graph ingestion;
- parent ADO governance-ticket update generation;
- Confluence review-page write-back; or
- any multi-round workflow behavior.

Drafting supports custom Evidence in the synthetic workspace; review remains fixture-bound;
they do not claim to draft from arbitrary repositories or analyze arbitrary documents. Offline
ADO work items remain local previews. Internal fake mode can submit one preview to an in-memory
gateway only; it never reaches Azure DevOps. Draft confirmation creates an unpublished artifact;
review-input confirmation binds the exact analysis package; reviewed-record confirmation controls
output generation. None formally approves the Solution Intent or replaces the Domain Architect.

**Reset semantics:** Each workflow reset clears only its local state. **Reset all local demo state**
clears both workflows. **Start New Review** clears review inputs, analysis, confirmation, previews,
and outputs. Publication operations that may identify a remote result are
retained for reconciliation within the current session. Restarting the process is not evidence
that an attempted remote Create did not happen. The current fake gateway is in memory and is not a
durable audit store.

Release gates at freeze: G1 offline **passed**; G2 external preparation with fakes and documented
adapter contracts **passed**; G3 internal live acceptance **not run**. Conditional I9 writes are
therefore deferred and no secondary-write controls are exposed. See
[`docs/INTERNAL_INTEGRATION_HANDOFF.md`](docs/INTERNAL_INTEGRATION_HANDOFF.md) for the bounded live
acceptance sequence.

## PoC and data statement

This is a hackathon PoC using synthetic data only. It must contain no real internal SI,
confidential architecture information, meeting transcript, personal data, secret, or API
credential. It is not production-ready and does not provide live Confluence, Microsoft Teams,
or Azure DevOps connectivity. The opt-in fakes make no network request and do not change this
statement.

Evidence changes require **Save evidence** before **Confirm Context & Continue**. Saving is local to
the session; the visible status changes back to unsaved after editing, adding, or removing content.
Valid saved custom evidence can reach the drafting step. The existing offline demo drafter accepts custom Evidence and reflects it in the draft.
No API or additional mode is required.

Custom Evidence drafting uses the existing demo workflow: save, confirm Context, generate, edit,
and human-confirm. English keyword grouping places literal source excerpts into template chapters;
unmapped text remains in the complete source appendix. Missing design details remain To be confirmed.
This is deterministic demo assembly, not semantic AI analysis; no external API is called. The exact
sample package retains its canonical output. Custom drafts do not become supported inputs for the
separate fixture-bound governance review extractor.

Project Context displays SI Template, Repository context, and Governance Metadata in independently
expanded sections by default; users may collapse them after review. Evidence appears once in its
editable input area. Governance metadata remains read-only. Source identity details and the full
source-package manifest are collapsed by default and remain available for traceability inspection.
