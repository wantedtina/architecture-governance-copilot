# Video materials

Start here for accepted versions and future revisions.

| Version | Accepted video | Slides and architecture |
| --- | --- | --- |
| [V1](v1/README.md) | Initial accepted base, 3:58, temporary Daniel narration | Actual slide artwork and architecture PDF/PNG/SVG; historical PPTX files do not match every accepted revision |
| [V2](v2/README.md) | Final 14 September submission, 3:39, user narration | Matching six-slide PPTX and architecture PDF/PNG/SVG |
| [Before V1](archive/pre-v1/README.md) | Earlier video iterations and human narration | Nine historical PPT iterations and earlier diagram sources |

Each version contains actual local files under `deliverables/`, `slides/`, `architecture/`, `narration/`, and `production/`. Large files and raw audio are Git-ignored; a Git clone alone does not contain the complete local archive.

## Git and local archive

Git preserves directory moves of previously tracked historical files, confirmed requirements, final scripts/captions, editable SVGs, production code, manual timing data, deck build sources and key manifests. New videos, decks, raw/generated audio, disposable command/filter files, TTS sentence files and duplicate historical drafts remain local and ignored. The V2 ASS caption header `title.ass` is retained because the human-voice script reads it as an input. Dependencies and application behavior are unchanged.

## Shared guidance

- [Confirmed requirements and V3 handoff](VIDEO_HANDOFF.md).
- [Tooling and reproduction status](TOOLING_SETUP.md).
- [Shared visual direction](BRAND_AND_VISUAL_GUIDE.md).
- `assets/` contains the shared accepted cover and closing artwork, kept at compatible paths.
- `ARCHIVE_MANIFEST.json` records source paths, sizes and SHA-256 checksums for preserved files.
- `PATH_DEPENDENCIES.json` records machine-specific references in historical scripts.
- Run `python3 video/verify_archive.py --scope tracked` from the project root for a checkout-only check. Run without arguments to check the complete local archive, including ignored media. Neither command renders or changes files.

The 15 September reorganization preserves external originals, the protected V1 backup and a pre-migration project snapshot at `/Users/wantedtina/Deliverables/architecture-governance-copilot/archive-reorganization-2026-09-15/`. Previous date-named and external version archives remain historical copies; use this directory as the main browsing entry point.

The final published attachments are on the [GitHub Release](https://github.com/wantedtina/architecture-governance-copilot/releases/tag/submission-2026-09-14-final-materials). The user reported successful company-computer download and making the repository private. No additional upload or publication was performed during reorganization.
