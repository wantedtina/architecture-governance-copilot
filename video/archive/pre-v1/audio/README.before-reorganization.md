# Audio Assets

## Archive status

This directory contains earlier local audio assets, including `human_voice_narration.wav` and `human_voice_segments/`. The local recordings and generated audio are not tracked in Git. These materials predate the later accepted baseline explicitly named V1, which used temporary Daniel narration.

For the accepted V2 human recordings, use the [V2 narration archive](../versions/v2/AUDIO.md). Twelve unchanged recording copies are now in the separate [v2 subdirectory](v2/README.md) of the original project checkout. The guide records project and external paths, chapter mapping and checksums. Raw audio remains Git-ignored.

The instructions below are retained as historical production notes. They do not describe the final V2 workflow or request a new render.

## Historical production notes

- `provisional_offline_tts.wav` is a **draft-only**, fully offline macOS TTS narration using the
  `Daniel` English voice. It is aligned to the original 03:50 storyboard and contains no external service
  output.
- `provisional_offline_tts_revised.wav` emphasizes AI assistance, AI Factory, and governed context
  retrieval and is aligned to the revised 03:58 storyboard. Spoken audio is tempo-adjusted only when required and
  is never truncated at a scene boundary.
- `provisional_tts_segments/` contains replaceable segment-level AIFF sources and aligned WAV
  files.
- Both paths are local, Git-ignored working files because they are large and reproducible. The
  committed review MP4 already contains the provisional narration.
- Rebuild the provisional track with `bash video/tools/build_provisional_narration.sh`.
- Replace the provisional track with approved human narration before final submission unless the
  team explicitly accepts the synthetic voice.

The final human narration should be placed at:

```text
video/audio/final_human_narration.wav
```

Then update `video/tools/render_draft.sh` to select that file and re-synchronize subtitles.
