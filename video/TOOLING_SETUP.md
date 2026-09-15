# Video production tooling

Document role: `CURRENT_TOOLING_HANDOFF`. Updated 15 September 2026. No installation, model switch, app recording or video render occurred during archive reorganization.

| Component | Recorded state and actual use | Next-session check |
| --- | --- | --- |
| Build Web Data Visualization | Desktop 0.1.21 installed/discoverable in the prior session; architecture guidance used for V2 | Confirm current skill catalog and read only relevant guidance |
| Presentations | Bundled 26.904.11930, Artifact Tool 2.8.59 recorded; neutral capability check and final six-slide PPTX export/render validation completed | Resolve current bundled Node/runtime; verify import before editing |
| Playwright | CLI 0.1.19, dependency 1.63.0-alpha-2026-08-31 recorded; neutral recording check passed | Real-app pickup failed on local HTTP in the V2 session; V2 reused accepted footage. Recheck app access before new capture |
| Remotion | Desktop 1.0.7 skills installed/discoverable; guidance used, SDK/Studio/renderer not installed or tested | Do not call the accepted video Remotion-rendered; assess need before installing runtime |
| FFmpeg | 7.1 cached executable recorded in V2 runtime JSON; actual video assembly and human-voice replacement | Re-resolve executable; do not assume a cache path survives |
| Python media tools | Isolated uv invocation: resvg-py 0.5.0, PyMuPDF 1.28.2, ReportLab 5.0.1 | Recheck installed/cached availability without modifying app dependencies |
| whisper.cpp | Local 1.9.4-dev, commit f133970bbb8c034ad9055a70afb97d61c24038f9, base.en model; timing hints only | Build/model remain external; re-resolve only if needed. ASR was not an authoritative transcript |

Installed, discoverable and successfully tested are distinct states. Versions above are production records, not fresh execution checks. The current session has not independently established model/reasoning equivalence. No paid services, new account authorization or license acceptance is covered by earlier setup; ask before those steps. No draw.io installation is needed for existing editable SVG.

## Source and command records

- `v1/production/history/VIDEO_HANDOFF.original.md` contains historical V1 commands and known manual caption adjustments.
- `v2/production/history/TOOLING_SETUP.original.md` records installation history and corrections.
- `v2/production/tool-assisted-v2/production/README.md` records the original SVG/FFmpeg pipeline.
- `v2/production/tool-assisted-v2-human-voice/README.md` records voice normalization, retiming and local transcription.
- `v2/slides/build/build.mjs` and `finalize.mjs` preserve PPTX construction/finalization sources. The bundled runtime link was intentionally not copied.
- `PATH_DEPENDENCIES.json` identifies fixed paths requiring review. Original scripts remain byte-identical historical sources.

The two V2 production workspace names remain siblings in the new layout, preserving their relative relationship. Some paths, including deck inputs, cached tools, V1 audio/frames and original metadata, still refer to original locations or layouts. Do not run scripts over accepted assets. Copy into V3, rebase inputs/outputs and verify prerequisites first. The full external workspaces and protected V1 backup remain available.

## Verification status

Archive checks: hashes, local file presence, primary document links, 12 original recording copies, final deliverable identity and Git-ignore coverage. No migrated pipeline rerender, native PowerPoint playback, new browser capture or fresh plugin execution was performed. Existing final-decode/render receipts are historical production evidence.
