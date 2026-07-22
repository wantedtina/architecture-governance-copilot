# Exact Demo Actions

Use the local app at `http://localhost:8501/`, a 1920 × 1080 viewport, and deterministic demo
mode. Reset before every take.

| # | Action | Expected visible result |
| ---: | --- | --- |
| 1 | Open `Draft Solution Intent` | Stage 1 of 4 is active; synthetic-data notice is visible |
| 2 | Click `Load Sample Drafting Context` | SI template, source-code context, and supporting documents populate |
| 3 | Inspect `Source Code`, `Supporting Documents`, and `SI Template` | Synthetic source material is readable |
| 4 | Click `Generate SI Draft` | Processing overlay completes and editable Human Review appears |
| 5 | Inspect the generated draft | Draft-only and human-accountability guidance remains visible |
| 6 | Click `Confirm SI Draft & Continue to Review` | Transition completes and Stage 2 Review Inputs opens |
| 7 | Click `Load Sample Transcript & Metadata` | Confirmed SI remains; transcript and review context populate |
| 8 | Inspect transcript and Solution Intent tabs | Timestamped discussion and confirmed SI are visible |
| 9 | Click `Analyze Review` | Processing overlay completes and Stage 3 Human Review opens |
| 10 | Inspect `Changes Requested`, counts, decisions, findings, evidence, risks, and missing information | Structured evidence-backed proposal is visible |
| 11 | In Actions, change the first owner from `Alex Chen` to `Taylor Kim` | Synthetic reviewer edit is preserved |
| 12 | In Questions, exclude `Should Redis be used as a cache?` | Question is omitted from the reviewed record |
| 13 | Click `Confirm Reviewed Record & Generate Outputs` | Processing completes and Stage 4 opens |
| 14 | Inspect generated review record | Taylor Kim is present and the Redis question is absent |
| 15 | Inspect `Azure DevOps Work Item Previews` | Two previews appear with a clear preview-only, not-submitted notice |
| 16 | Return to the top and hold | All four stages show complete |

If any deterministic value differs, reset and repeat the take; do not manually repair generated
content during recording.
