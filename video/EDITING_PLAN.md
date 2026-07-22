# Editing Plan for macOS

## Source preparation

1. Use the five 1920 × 1080 PNG frames and the updated editable PowerPoint source:
   `presentation/Architecture_Governance_Copilot_Video_Deck_Revised.pptx`.
2. Record the real local app at 1920 × 1080 and 30 fps.
3. Record final human narration as 48 kHz WAV or AIFF. The supplied offline TTS is provisional
   and replaceable.
4. Keep the standalone SRT beside the project.

## Practical Mac workflow

Use iMovie, Final Cut Pro, DaVinci Resolve, or Keynote plus QuickTime. FFmpeg may reproduce the
review draft with `video/tools/render_draft.sh`.

1. Create a 1080p, 30 fps project.
2. Place frames and app recording in the order defined by `SHOT_LIST.md`.
3. Remove pauses, retries, dead scrolling, and browser setup.
4. Use clean cuts for tab changes and short dissolves between presentation frames and app footage.
5. Keep any crop move subtle and within 103–108%.
6. Place final narration first, then adjust picture edits to sentence pauses.
7. Add only the approved concise callouts.
8. Import and re-time `SUBTITLES_DRAFT.srt` after final human voice recording.
9. Burn subtitles for the shareable review copy and preserve the standalone SRT.

## Audio

Default to no music. If music is approved, use only built-in or properly licensed material,
document the source, and keep it well below narration. Normalize narration to approximately
-16 LUFS integrated with peaks below -1 dBTP.

## Export

- Container: MP4
- Video: H.264
- Resolution: 1920 × 1080
- Frame rate: 30 fps
- Audio: AAC, 48 kHz, stereo
- Duration: target 03:42; hard maximum 03:55
- Use a bitrate that preserves UI text; approximately 8–12 Mbps is suitable for the final review
  export.

## Quality checks

- Watch the full export without skipping.
- Replay once muted to validate subtitle-only comprehension.
- Check the smallest evidence text and action-owner edit at 100% display scale.
- Confirm no personal data, local path, notification, or unsupported claim is visible.
- Confirm team identity, ADO preview-only disclosure, synthetic-data disclosure, and Domain Architect
  authority.
- Replace provisional TTS before final submission unless the team explicitly approves it.
