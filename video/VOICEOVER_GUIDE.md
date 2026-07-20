# Voice-over Guide

## Recommended narrator

Prefer one human narrator with a calm, confident, conversational delivery. The narrator should
sound like a domain colleague explaining a useful control workflow, not a commercial announcer.
Use the same narrator throughout.

The review draft may use the included **provisional offline macOS TTS** track. It is not the final
approved narration and is designed to be replaced without changing the edit.

## Recording environment

- Record in a quiet, soft-furnished room with doors and windows closed.
- Disable notifications, fans, and nearby devices that create intermittent noise.
- Record 10 seconds of room tone before the first take.
- Use headphones to prevent playback bleed.

## Microphone placement

- Position the microphone 15–20 cm from the mouth and slightly off-axis.
- Keep distance and posture consistent.
- Use a pop filter where available.
- Record at 48 kHz, 24-bit WAV or AIFF; avoid clipping and aggressive input gain.

## Pace and delivery

- Target 125–135 spoken words per minute.
- Use short pauses at the segment boundaries in `STORYBOARD.md`.
- Pause immediately before `Load Sample Review`, `Analyze Review`, and
  `Confirm Reviewed Record & Generate Outputs`.
- Leave visual breathing room while the processing overlays and generated outputs appear.
- Emphasize `Changes Requested`, `evidence`, `human review`, `Taylor Kim`, `mock`, and
  `Domain Architect`.

## Pronunciation

- SI: “ess-eye”
- ADO: “A-D-O”
- RTO / RPO: pronounce each letter
- PostgreSQL: “post-gres-Q-L”
- Confluence: stress the first syllable
- Azure: use the narrator's natural professional pronunciation consistently

## Retakes

Record sentence-level takes rather than restarting the whole script. Mark each take with the
segment timestamp and sentence number. Keep one second of silence before and after every take.
Replace only the affected sentence during editing.

## Noise reduction and loudness

- Apply light high-pass filtering around 70–90 Hz only if needed.
- Capture a noise profile from room tone and use conservative reduction; avoid metallic artifacts.
- Use gentle compression for consistency, not audible pumping.
- Normalize the final narration consistently, targeting approximately -16 LUFS integrated for
  the shareable draft and peaks below -1 dBTP.
- Do not add background music unless it is properly licensed or built in, documented, and quiet
  enough that narration remains effortless to understand. The default decision is no music.

## Synchronization

1. Lock the final human narration before final subtitle timing.
2. Place each narration segment at its storyboard start marker.
3. Adjust picture edits to natural sentence pauses; do not time-stretch a human voice unless the
   change is imperceptible.
4. Re-time the SRT to the final waveform sentence by sentence.
5. Check muted playback for subtitle comprehension and audio playback for lip-free action sync.
6. Export a clean narration file separately from the mixed video.
