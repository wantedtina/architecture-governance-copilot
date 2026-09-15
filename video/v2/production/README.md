# V2 production sources

`tool-assisted-v2/` contains the temporary-voice video pipeline, original footage, SVG/PNG assets, edit list, generated chapter clips, narration timing and QA records. `tool-assisted-v2-human-voice/` contains the accepted replacement pipeline, raw source copies, timing anchors, normalization data, captions and QA. `intermediate-exports/` contains the temporary narrated preview, not the final submission. `history/` preserves proposals, previous indexes, form text, release receipt and earlier documents with their historical status language unchanged.

The final files are in `../deliverables/`; deck construction sources are in `../slides/build/`. The user-recorded originals are directly accessible in `../narration/raw/` and match production copies. The transcription engine/build/model and bundled runtime dependencies were not copied; original paths are recorded in the source README and shared tooling handoff.

The sibling workspace names are preserved, but cached executable paths and deck input paths require validation/rebasing for a new version. The scripts are historical source copies and were not executed after migration. Start V3 from a copy, choose output paths that cannot overwrite accepted files, and consult `../../TOOLING_SETUP.md`.

## Version-control selection

The complete local source snapshot remains here. Git tracks code, source timeline/story data, voice mapping, runtime/provenance manifests and the required provisional `audio/title.ass` header. Other generated chapter ASS files, render commands/filters, concatenation lists, TTS sentence inputs, duplicate exported scripts/SVGs and copied submission drafts are local-only. The canonical final script/captions and editable SVGs are in the version-level narration, slides and architecture folders. The deck build sources are explicitly included despite the generic build-directory ignore rule.
