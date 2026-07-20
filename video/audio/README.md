# Audio Assets

- `provisional_offline_tts.wav` is a **draft-only**, fully offline macOS TTS narration using the
  `Daniel` English voice. It is aligned to the 03:50 storyboard and contains no external service
  output.
- `provisional_tts_segments/` contains replaceable segment-level AIFF sources and aligned WAV
  files.
- Both paths are local, Git-ignored working files because they are large and reproducible. The
  committed review MP4 already contains the provisional narration.
- Replace the provisional track with approved human narration before final submission unless the
  team explicitly accepts the synthetic voice.

The final human narration should be placed at:

```text
video/audio/final_human_narration.wav
```

Then update `video/tools/render_draft.sh` to select that file and re-synchronize subtitles.
