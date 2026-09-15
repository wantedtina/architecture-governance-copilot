# V1 production sources

`original-workspace/` preserves scripts, story, clips and QA from the accepted historical v2.2 workspace. Narration audio/timing is collected in `../narration/working/`, slide artwork in `../slides/`, and architecture in `../architecture/`. `footage/`, `prior-edited-clips/` and `capture-source/` preserve the earlier recordings and capture/edit code reused for accepted V1. `history/` preserves the handoff, final-export metadata and prior index snapshots.

This organized source collection is not directly executable in its new layout. Original scripts use relative `audio/`/`frames/` paths and fixed paths to older workspaces, cached FFmpeg and the original project. `revise.py` is non-idempotent. Final captions include manual adjustments that `voice.py` would overwrite. Do not run those scripts as an archive check. The original full workspace and protected V1 backup remain in Deliverables; the original command record is in `history/VIDEO_HANDOFF.original.md`.

For future revisions use the accepted V2 as the normal base. Rebuild a disposable workspace and resolve dependencies before running historical V1 code.
