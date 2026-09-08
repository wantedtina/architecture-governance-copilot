# Codex Handoff — Architecture Governance Copilot

Last verified: 24 July 2026

Repository: `/Users/wantedtina/Repos/architecture-governance-copilot`

Branch: `main`

Baseline commit before this handoff: `022476d` (`Enhance human voice video timing`)

## Project objective

Architecture Governance Copilot is a short-hackathon proof of concept that demonstrates one
reliable, human-controlled architecture-governance workflow using synthetic data.

The implemented workflow:

1. opens a synthetic project context package;
2. drafts a Solution Intent (SI) from a template, selected repository context, and supporting
   notes;
3. lets a human edit and confirm the SI;
4. analyzes the confirmed SI together with a synthetic Teams-style review transcript and review
   metadata;
5. presents source-backed findings, decisions, risks, actions, questions, missing information,
   and the review outcome for human review;
6. lets the reviewer edit or exclude proposed items; and
7. generates standardized Markdown review minutes and Azure DevOps work-item previews only after
   human confirmation.

This is not a production platform. It has no database, authentication, real enterprise
integrations, or live LLM call. The primary demo path is deterministic and remains usable
offline.

## Current architecture and key components

### User interface and routing

- `app.py` contains the Streamlit shell, visual theme, stage renderers, transitions, and most UI
  event handling.
- `pages/` contains five thin Streamlit route wrappers:
  - `project_context.py`
  - `solution_intent_drafting.py`
  - `review_inputs.py`
  - `human_review.py`
  - `generated_outputs.py`
- Each route wrapper executes `app.py` with `runpy.run_path()` and invokes its corresponding
  private renderer. This gives the demo browser-style page navigation through
  `st.switch_page()` while preserving shared Streamlit session state.
- `src/architecture_governance_copilot/ui_support.py` owns workflow constants, sample loading,
  session-state initialization/reset, fingerprints, stale-result handling, project-context
  readiness, human-edit reconstruction, and output storage.

The visible workflow is:

```text
Project Context
    → Draft Solution Intent
    → Review Inputs
    → Human Review
    → Generated Outputs
```

An existing-SI shortcut skips the first two stages and moves directly to Review Inputs.

### Domain and service layer

- `models.py` defines strict Pydantic models and enums. Unknown fields are forbidden, strings are
  stripped, required text is non-empty, and source evidence is mandatory for review items where
  appropriate.
- `si_drafting.py` defines the `SolutionIntentDrafter` protocol,
  `DeterministicDemoDrafter`, and `SolutionIntentDraftingService`.
- `extractors.py` defines the `GovernanceExtractor` protocol and
  `DeterministicDemoExtractor`.
- `governance_service.py` separates review analysis from post-review output generation so the
  human-review step remains between them.
- `minutes_generator.py` deterministically produces Markdown review minutes.
- `ado_generator.py` deterministically produces typed Azure DevOps work-item previews. It makes
  no network request.

### Deterministic data path

The default providers compare their inputs with the bundled files in `samples/` and return a deep
copy of a validated known result:

```text
SI template + repository excerpt + supporting notes
    → deterministic SI draft
    → human confirmation
    → confirmed SI + transcript + review metadata
    → deterministic governance result
    → human edit/include/exclude
    → minutes + ADO previews
```

The fixture-backed providers intentionally do not perform semantic analysis of arbitrary text.
Provider protocols are the extension boundaries for a future approved LLM implementation.

### Production-shaped target architecture

The presentation materials describe a future architecture rather than implemented integrations:

- AGC front end on Service Bench;
- AGC backend API on SKE;
- permission-aware Confluence, Teams, and Azure DevOps connectivity;
- an AIF (AI Factory) LLM provider adapter;
- a database for state and audit history; and
- enterprise identity, secrets, audit, monitoring, and data-policy controls.

In the current PoC all of those external connections and persistence capabilities are simulated
or absent.

## Work completed in this thread

The repository progressed from a planning scaffold to a routed, deterministic working PoC:

- established the Python 3.12, `uv`, `pyproject.toml`, src-layout project;
- documented the product, domain model, architecture, demo, and implementation phases;
- implemented strict governance models and validation tests;
- created the synthetic SI, transcript, metadata, and expected-result fixture;
- implemented the deterministic extractor provider;
- implemented deterministic review-minutes and ADO-preview generators;
- implemented governance-service orchestration with analysis and generation separated;
- implemented the Streamlit human-review flow;
- added edit, exclude, evidence display, stale-input protection, and reset behavior;
- converted the UI to routed stage navigation with visible processing effects;
- applied an internal enterprise visual treatment and Standard Chartered presentation branding;
- added pre-review SI drafting behind a provider interface;
- added production-shaped Project Context selection and confirmation;
- added and repeatedly updated the video-production package, system architecture, deck, demo
  recording, narration, subtitles, and rendered review videos; and
- added human-narration timing support in the latest commit.

Relevant recent commits:

| Commit | Summary |
| --- | --- |
| `022476d` | Human-voice narration timing and rendered review video |
| `34f2bd0` | Updated demo video and connected target architecture |
| `d731d7a` | Project Context intake workflow |
| `b35131c` | Enterprise UI and video polish |
| `1e68010` | Solution Intent drafting workflow |
| `6f460e2` | Initial video-production package |
| `efbf53e` | Routed Streamlit experience |
| `e7578b7` | Streamlit human-review workflow |
| `190496b` | Governance review service |
| `7359fb1` | Deterministic output generators |
| `541684e` | Deterministic governance extractor |

## Important design decisions and rationale

### Deterministic offline providers are the primary demo path

The hackathon prioritizes a reliable demonstration over arbitrary-input capability. Exact fixture
matching makes the outcome repeatable and avoids network, credentials, latency, and model-output
variability. Both drafting and extraction remain behind small provider protocols so a real
provider can be added later without rewriting the domain or UI.

### Humans retain formal accountability

AI/provider output is always proposed content. The user must review and confirm the SI draft and
the governance record. The application does not claim to approve architecture and does not
publish to Confluence or Azure DevOps.

### Evidence remains attached and read-only during review

Every material extracted item retains its SI quote or transcript reference. Reviewers can edit
the structured proposal or exclude it, but the supporting source evidence is not silently
rewritten.

### Analysis and output generation are separate operations

`GovernanceReviewService.analyze_review()` produces a proposal. Outputs are generated later from
the reconstructed, human-reviewed `GovernanceResult`. This prevents generators from bypassing
human review.

### Session state replaces persistence

Streamlit session state is sufficient for the PoC and keeps the implementation small. Input
fingerprints invalidate stale analysis and outputs. There is deliberately no database or
multi-user history.

### Routed pages improve demo realism

The `pages/` wrappers exist to make stage changes behave like page navigation rather than
appending every stage to one long screen. They are routing entry points, not independent business
modules; changing or removing them will break `st.switch_page()` destinations.

### Project Context is simulated but production-shaped

The PoC lets a user select and inspect synthetic context explicitly. The target production flow
would retrieve only authorized, user-selected material through enterprise APIs. It would not
crawl arbitrary repositories or internal content.

### The current target diagram distinguishes direct APIs from the AIF adapter

Confluence, Teams, and Azure DevOps are depicted as backend-connected enterprise APIs. AIF is
behind the LLM provider adapter. Azure DevOps covers both Azure Repos context and Azure Boards
governance/work-item data.

### Video assets are presentation artifacts, not runtime dependencies

The application does not need `video/` to run. Large video files are nevertheless already
tracked in Git history. The team discussed moving presentation media outside the source
repository, but no cleanup or history rewrite has been approved or performed.

## Files added or modified

### Application and configuration

- `.gitignore`
- `app.py`
- `pyproject.toml`
- `uv.lock`
- `assets/standard_chartered_logo.png`
- all route wrappers under `pages/`
- all package modules under `src/architecture_governance_copilot/`
- all synthetic fixtures under `samples/`
- all tests under `tests/`

### Product documentation

- `README.md`
- `SPEC.md`
- `DEMO.md`

### Presentation and video package

- planning, scripts, subtitles, and checklists under `video/`
- slide images under `video/assets/`
- PowerPoint and Graphviz sources under `video/presentation/`
- demo recording under `video/recordings/`
- narration and render scripts under `video/tools/`
- rendered review MP4 and SRT files under `video/output/`

### Added for this handoff

- `AGENTS.md`
- `docs/CODEX_HANDOFF.md`

Use `git log --stat` and `git log --name-status` for the exact historical change list.

## Commands

Run all commands from the repository root:

```bash
cd /Users/wantedtina/Repos/architecture-governance-copilot
```

### Install/synchronize

```bash
uv sync
```

### Run the application

```bash
uv run streamlit run app.py
```

The app is normally available at `http://localhost:8501/`.

Optional transition timing:

```bash
AGC_DEMO_STEP_DELAY_SECONDS=0.6 uv run streamlit run app.py
AGC_DEMO_STEP_DELAY_SECONDS=0 uv run streamlit run app.py
```

The default delay is 0.4 seconds per visible processing phase.

### Test and lint

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

### Build the Python package

```bash
uv build
```

`build/`, `dist/`, and package metadata directories are ignored.

### Rebuild presentation video artifacts

Video work requires macOS `say`, FFmpeg at the location expected by the scripts (or an explicit
`FFMPEG` environment variable), and the Playwright CLI helper expected by `record_demo.sh`.

With the Streamlit app already running:

```bash
bash video/tools/record_demo.sh
bash video/tools/build_provisional_narration.sh
bash video/tools/render_draft.sh
```

The human-narration path additionally expects the eight local `.m4a` recordings under
`video/human_voice/`:

```bash
bash video/tools/build_human_narration.sh
```

`render_draft.sh` accepts environment overrides including `OUTPUT`, `SUBTITLE_OUTPUT`,
`SUBTITLE_SOURCE`, `NARRATION_AUDIO`, `WATERMARK_TEXT`, `ARCHITECTURE_DURATION`,
`DEMO_DURATION`, `BUSINESS_DURATION`, and `CLOSING_DURATION`.

## Current verification status

Verified on 24 July 2026:

- `uv run pytest`: **251 passed**;
- `uv run ruff check .`: **passed**;
- `uv run ruff format --check .`: **passed; 24 files already formatted**;
- `uv build`: **passed**, producing the ignored source distribution and wheel under `dist/`;
- `git diff --check`: **passed**;
- HEAD remains `022476d`;
- `main` remains aligned with `origin/main`; and
- the only working-tree additions are this handoff and `AGENTS.md`, both intentionally untracked
  until the user reviews and commits them.

Expected handoff status:

```text
## main...origin/main
?? AGENTS.md
?? docs/
```

## Known issues, risks, and unresolved questions

### Application limitations

1. **Arbitrary inputs are unsupported.** The deterministic drafter and extractor accept only the
   frozen synthetic fixture. An edited generated SI can be confirmed and carried forward, but the
   deterministic review analyzer then rejects it if it no longer matches the bundled SI.
2. **No real LLM provider exists.** The provider abstractions are implemented, but prompts,
   credentials, structured response handling, safety controls, and API-failure behavior are not.
3. **Project Context is simulated.** Confluence, Teams, Azure Repos, and Azure Boards are not
   queried.
4. **No persistence or audit history exists.** Refreshing/resetting the session loses workflow
   state. There is no multi-user or multi-round review history.
5. **ADO items are previews only.** No work item is created externally.
6. **No authentication or authorization exists.**
7. **The route wrappers are coupled to private functions in `app.py`.** This is acceptable for the
   PoC but not a production modularity pattern.
8. **Most UI code is concentrated in `app.py`.** Avoid a large refactor unless it directly serves
   an approved next objective; current tests rely on many helper functions.

### Video and repository risks

1. **The latest human-narrated video was not accepted.** The reviewer reported cut-out or unclear
   speech. The cloning/TTS alternative was discussed and explicitly deferred.
2. **The provisional generated voice sounds robotic.** It remains a fallback, not an approved
   final narration.
3. **Large media binaries are tracked.** MP4, WebM, and PowerPoint files materially increase
   repository size. Adding ignore rules does not untrack existing files or remove them from
   history.
4. **Repository cleanup is unresolved.** The preferred direction discussed was to keep source,
   tests, synthetic samples, configuration, and concise documentation in Git, while storing
   presentation media elsewhere. No deletion, Git LFS migration, or history rewrite has been
   authorized.
5. **A true size reduction would require history rewriting.** This would require explicit
   approval, backup, coordination, and a force push.
6. **Branding and internal architecture content should remain internal.** Reconfirm permission
   before any public distribution.

### Product questions

1. Which approved enterprise LLM/AIF endpoint and structured-output contract should implement
   arbitrary drafting and review?
2. What authorization model governs retrieval from Confluence, Teams, Azure Repos, and Azure
   Boards?
3. What SI template/version-selection rules are required across domains?
4. What persistence, retention, audit, and multi-round review model is required?
5. Should confirmed outputs be published to Confluence/ADO, or remain downloadable previews?
6. Should the video package remain in this repository, move to external storage, use Git LFS, or
   be removed through a carefully planned history rewrite?

## Exact recommended next steps

1. **Commit this handoff only after reviewing it.** Confirm `AGENTS.md` and this file accurately
   describe the desired repository conventions.
2. **Decide repository/media policy before more video work.** If source-only Git is preferred,
   back up presentation assets externally, agree whether history must be rewritten, and perform
   cleanup as a separate explicitly approved task.
3. **Choose the next product objective.** The smallest useful application increment is an
   optional real provider for arbitrary *synthetic* SI drafting/review, still behind the existing
   protocols and with deterministic mode retained as fallback.
4. **Define the approved provider contract first.** Specify endpoint, authentication,
   data-classification constraints, JSON schema, timeout/retry behavior, logging restrictions,
   and failure fallback before writing integration code.
5. **Add provider tests without network dependency.** Mock the provider boundary, validate
   structured responses with existing Pydantic models, and test fallback to deterministic mode.
6. **Only then consider enterprise connectors.** Implement permission-aware context retrieval
   separately from LLM processing; never introduce broad crawling.
7. **Treat video narration as a separate deliverable.** If resumed, use clean regenerated
   narration aligned to natural speech duration rather than forcing recorded audio into fixed
   scene lengths.

Do not proceed with production integrations, database work, repository history rewriting, or
external voice upload without explicit user authorization.
