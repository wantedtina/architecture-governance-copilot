# Architecture Governance Copilot — V2 Human Voice

Date: 14 September 2026

The video uses all twelve recordings supplied in `voice-records/`, at their original speed. The original V2 video and the recordings were preserved. This is a separate export.

## Files

- `architecture-governance-copilot-v2-human-voice.mp4`: 3:39, 1920×1080, 30 fps, H.264/AAC; human narration and burned-in English captions.
- `architecture-governance-copilot-v2-human-voice.srt`: matching external captions.
- `NARRATION_HUMAN_VOICE.md`: updated script and chapter times.
- `edit-timeline.json`: exact chapter timing and picture-to-voice anchors.
- `VERIFICATION.json`: technical checks.
- `SHA256SUMS.txt`: export hashes.

## Revision

The user omitted “That's our response to the feedback.” from What we strengthened. The sentence is removed from both the video captions and the SRT/script. Other approved script wording remains unchanged. Two adjacent caption fragments in the evidence section are combined into one complete sentence.

Pictures follow the human speech, while retaining the accepted chapter order, full demo, original UI states, highlights, branding and architecture. The native recordings run at 1.0×; only chapter-ending silence and volume normalization were added. Picture timing accounts for the faster spoken delivery, shortening the export from 3:58 to 3:39. No new application capture or application modification was needed.

Audio normalization measured -16.1 LUFS integrated and -4.4 dBFS true peak in the final AAC export. Complete decoding passed for all 6,570 frames. All 47 caption cues are in bounds and do not overlap. Targeted visual checks covered the first frame, evidence quote, confirmed owner, create control, receipt, invalidation message, shortened feedback caption and closing.

Local speech recognition supplied timing hints; waveform pauses were used to correct boundaries. Recognition mistakes in project terminology were not copied into the captions. This is assisted timing verification, not a claim of perfect automatic transcription or an independent human listening review.

No upload, submission, commit, push or company access action was performed. The application baseline remains `81835b9ced0c709f4003522557b6423bc4bdaa18`. System-design and demo-capability boundaries remain those of the accepted V2.
