# Review v2.2 - clearer flow and presenter narration

Application revision: `81835b9ced0c709f4003522557b6423bc4bdaa18`.

## Changes

- The process slide uses a continuous snake: 1, 2, 3 across the top, then down to 4,
  then left to 5 and 6. Each step has an action description and a labelled Tool or Owner.
- The solution slide explicitly identifies Confluence as the SI source of truth. The app
  produces drafts and suggested changes; users decide what to use and edit Confluence themselves.
  The app does not write or edit Confluence. This is a design boundary, not a claim of compliance certification.
- Project Team and Domain Architect have equal actor boxes and typography in the architecture,
  with different responsibilities and role-based permissions. There is no Primary users label.
  The Confluence adapter is read-only; manual user edits take place in Confluence UI.
- Narration is rewritten as a direct presentation to judges, with a greeting, first-person
  demo walkthrough and a spoken thank-you. It retains evidence, human edits, finding exclusion,
  controlled delivery and changed-input invalidation. No quantified benefit is invented.
- The video starts on the title slide and lasts 3:58. The full demo footage, cursor halo and
  click highlights are retained. Narration and captions are regenerated against the new timeline.

## Deliverables

- `architecture-governance-copilot-v2.2-narrated.mp4`: 1080p, 30 fps, H.264/AAC,
  temporary Daniel English narration and burned-in English captions.
- `architecture-governance-copilot-v2.2.srt`: matching standalone captions.
- `NARRATION_V2.2.md`: complete recording script with section times.
- `system-architecture.pdf`, `.png`, `.svg`: architecture diagram and editable source.
- `process.png`, `.svg`, `solution.png`, `.svg`: revised slide images and editable sources.
- `FORM_TEXT.md`: unchanged approved three-field text.
- `edit-timeline.json`: section times and preserved demo edit mapping.

## Scope

The architecture represents the agreed system design, including persistence and enterprise controls;
it does not assert production deployment or live integration acceptance. Teams transcripts remain
manual imports. This session changes presentation materials only. No application code, tests,
fixtures, dependencies, refinement register, historical media or tags were changed. Previous exports
are retained. Nothing was committed, pushed, uploaded or submitted.

Final human voice replacement remains pending the user's recording.

## Verification

- The final export decodes in full: 238.00 seconds, 1080p, 30 fps.
- Video size: 23,372,953 bytes.
- All 48 captions are ordered, within the video duration, and at most two lines.
- Six-second interval contact sheets cover the full sequence. Full-size slide and demo samples
  were inspected; final opening and drafting subtitle regrouping received separate checks.
- The architecture PDF was rendered back to PNG and visually inspected.
- Approved form text matches v2.1 byte-for-byte. The original checkout is clean at the locked
  commit and the historical submission tag is unchanged.
