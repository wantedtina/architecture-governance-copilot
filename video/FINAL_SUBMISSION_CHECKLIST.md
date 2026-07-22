# Final Submission Checklist

## Identity and timing

- [ ] Duration is below four minutes and no longer than 03:55
- [ ] Opening shows `Architecture Governance Copilot`
- [ ] Opening and closing show `Two Tokens One Brain`
- [ ] Opening shows `Accelerate 3.0 Hackathon`
- [ ] Opening and closing show `Zhang1, Yang — Team Lead`
- [ ] Opening and closing show `Wang, Ted — Team Member`

## Story and boundaries

- [ ] SI is correctly described as officially maintained in Confluence
- [ ] Synthetic Markdown is described as normalized internal representation, not a second official copy
- [ ] Teams transcript is described as available only when transcription is enabled and permitted
- [ ] Microsoft 365 Copilot is not described as always creating transcripts
- [ ] Synthetic-data disclosure is visible
- [ ] Deterministic fixture-backed extraction is disclosed once
- [ ] No arbitrary-document or production enterprise LLM claim
- [ ] No real Confluence, Teams, or Azure DevOps integration claim
- [ ] Azure DevOps outputs are clearly identified as preview-only
- [ ] No automatic approval claim
- [ ] Domain Architect authority is explicit
- [ ] No unsupported metrics

## Demo

- [ ] Real app UI is readable
- [ ] `Load Sample Drafting Context` populates all three drafting inputs
- [ ] SI draft confirmation carries the draft into Review Inputs
- [ ] `Load Sample Transcript & Metadata` populates the review context
- [ ] `Analyze Review` routes to Human Review
- [ ] Outcome, decisions, findings, risks, actions, questions, and missing information are shown
- [ ] Supporting source evidence is shown
- [ ] First action owner becomes `Taylor Kim`
- [ ] Redis question is excluded
- [ ] `Confirm Reviewed Record & Generate Outputs` routes to Generated Outputs
- [ ] Human edits are preserved
- [ ] Review record and two Azure DevOps work-item previews are shown
- [ ] No real ADO item is created

## Visual, audio, and data safety

- [ ] No unapproved official logo, media-library image, or proprietary template
- [ ] UI and frames remain readable at 1080p
- [ ] English voice-over is complete and understandable
- [ ] Provisional TTS replaced or explicitly approved
- [ ] Subtitles synchronized and safe
- [ ] No copyrighted commercial music
- [ ] No confidential or real internal data
- [ ] No username, local path, email, token, or secret visible

## Technical verification

- [ ] `uv run pytest` passes
- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format --check .` passes
- [ ] Every visual frame is 1920 × 1080
- [ ] SVG sources are valid XML
- [ ] MP4 is H.264, 1920 × 1080, 30 fps, with AAC audio
- [ ] Standalone SRT is valid and matches final voice
- [ ] Complete end-to-end playback reviewed
- [ ] Upload completes and the uploaded file plays correctly

Do not upload until all manual-confirmation placeholders are resolved and the final human
narration is approved.
