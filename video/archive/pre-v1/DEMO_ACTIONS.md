# Exact Demo Actions

Use the local app at `http://localhost:8501/`, a 1920 × 1080 viewport, and deterministic demo
mode. Reset before every take.

| # | Action | Expected visible result |
| ---: | --- | --- |
| 1 | Open the app | Stage 1 of 5, `Project Context`, is active; synthetic-data notice is visible |
| 2 | Click `Open Demonstration Project` | Governance reference, SI template version, repository branch, and source selections appear |
| 3 | Expand selected source previews; open each tab and deliberately scroll through its longer content; click `Refresh Context` | Synthetic local source material and validation status are visible |
| 4 | Click `Confirm Context & Continue` | Transition completes and Stage 2 Draft Solution Intent opens |
| 5 | Click `Generate SI Draft` | Processing overlay completes and the editable proposed SI appears first |
| 6 | Inspect the generated draft | Draft-only guidance is visible; `View drafting sources` remains collapsed |
| 7 | Click `Confirm SI Draft & Continue to Review` | Transition completes and Stage 3 Review Inputs opens |
| 8 | Click `Load Sample Transcript & Metadata` | Confirmed SI remains; transcript and review context populate |
| 9 | Inspect transcript and Solution Intent tabs | Timestamped discussion and confirmed SI are visible |
| 10 | Click `Analyze Review` | Processing overlay completes and Stage 4 Human Review opens |
| 11 | Inspect `Changes Requested`, counts, decisions, findings, evidence, risks, and missing information | Structured evidence-backed proposal is visible |
| 12 | In Actions, change the first owner from `Alex Chen` to `Taylor Kim` | Synthetic reviewer edit is preserved |
| 13 | In Questions, exclude `Should Redis be used as a cache?` | Question is omitted from the reviewed record |
| 14 | Click `Confirm Reviewed Record & Generate Outputs` | Processing completes and Stage 5 opens |
| 15 | Inspect generated review record | Taylor Kim is present and the Redis question is absent |
| 16 | Inspect `Azure DevOps Work Item Previews` | Two previews appear with a clear preview-only, not-submitted notice |
| 17 | Return to the top and hold | All five stages show complete |

If any deterministic value differs, reset and repeat the take; do not manually repair generated
content during recording.

Every recorded button, tab, checkbox, and editable-field interaction uses a short red click cue
before activation so the viewer can follow what triggered each state change.
