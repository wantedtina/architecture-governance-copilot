# V2 production sources

This external workspace implements the approved targeted V2 proposal. It does not change the application or accepted V1.

## Contents and commands

`assets/` contains 67 verified copies of the required V1 inputs. `source/asset-manifest.json` records original paths, local paths and SHA-256 values. `source/story.json` preserves accepted wording. `source/timeline.json` records paragraph/caption timing. `source/edit-list.json` records source shots and focus regions. `source/*-command.json` and `.fffilter` files record executed render commands and filters. `audio/` and `clips/` are generated working files; `qa/` contains checks and logs.

Run from this external workspace root, never from the application environment:

```bash
cd /Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2
uv run --offline --no-project --python 3.12 --with resvg-py==0.5.0 --with pymupdf==1.28.2 --with reportlab==5.0.1 python production/source/prepare.py
python3 production/source/render.py
python3 production/source/verify.py
```

Preparation re-reads the preserved original inputs and requires their recorded paths and locked application HEAD. Rendering uses local copied assets. Re-running these commands replaces only generated V2 outputs, so preserve an accepted V2 before further changes. For a selective picture revision, pass section IDs to `render.py`; the final mux is regenerated when all section clips exist. A narration/caption change requires rendering all affected sections and re-running verification.

FFmpeg 7.1 is selected by its existing cached binary path in `source/runtime.json`. There are no new application dependencies. The Python production packages above use an isolated uv invocation. They must already be cached for the offline command. No Remotion SDK, account, paid service or license acceptance was used. Existing AIFF voice inputs were reused rather than regenerated.

## Tool usage and limits

Build Web Data Visualization's architecture/layout guidance informed the limited connector and focus changes. Editable SVG sources were rendered with resvg; ReportLab exported the matching PDF and PyMuPDF rendered it for inspection. The PDF contains the raster architecture image; use SVG for vector editing.

Presentations successfully passed a separate neutral PPTX/PNG capability check. A companion PowerPoint rebuild was optional and was not needed for this video. Playwright passed a neutral click/recording check, but real application capture in this session was not verified because local HTTP access failed; no pickup was needed. The desktop Remotion plugin and its skills are installed/discoverable, while its SDK rendering runtime was not installed or tested. FFmpeg performed production assembly using the approved fallback. Do not describe this export as Remotion-rendered.

Each section was encoded from the original copied raw footage or slide image. Encoded video sections were joined by stream copy; AAC narration was muxed once. Source footage remains 1600×900/25 fps within the 1920×1080/30 fps output. Small supporting UI text is best reviewed full-screen; no resolution beyond the source capture is claimed.

The finite audio construction allocates exactly the required PCM samples per chapter, followed by concatenation and loudness normalization. The final WAV measured -15.8 LUFS integrated, 3.0 LU loudness range, and -1.5 dBFS true peak. Caption alignment combines measured pauses with proportional estimates; no forced alignment or speech-transcription test is claimed.

## Preservation and pending work

Application HEAD: `81835b9ced0c709f4003522557b6423bc4bdaa18`.
Original repository: `/Users/wantedtina/Repos/architecture-governance-copilot`.
Materials worktree: `/Users/wantedtina/Repos/architecture-governance-copilot-submission-materials`.
Both remained at the locked HEAD. The original was clean; the materials worktree retained its pre-existing untracked `docs/submission/`. Both passed `git diff --check`. No remote fetch or company access action was performed.

Accepted V1: `/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.2/export/architecture-governance-copilot-v2.2-narrated.mp4`.
SHA-256: `fe52d4bdf9cf42114a77d9646af4a27f2de2bc82108e845491cdc8f89282068a`.
V1 backup: `/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2-preparation/V1_BACKUP_2026-09-14/`.
Historical constraints: `/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2-preparation/VIDEO_HANDOFF.md` and `TOOLING_SETUP.md`.

No model or reasoning-setting switch was performed. Exact active and historical settings are not exposed for independent equivalence verification.

Pending: user review, replacement with the user's voice, and subsequent audio/picture/caption verification. Upload, submission and internal access remain with the user. No application defect was established during this footage-only edit; no app workstream changes are requested.
