# Exact Demo Actions

Use the local app at `http://localhost:8501/`, a 1920 × 1080 viewport, 100% browser zoom, and the
default deterministic mode. Reset the demo before every take.

The selected human edits are:

1. Change the first action owner from `Alex Chen` to `Taylor Kim`. `Taylor Kim` is a clearly
   synthetic reviewer-approved demo value.
2. Exclude `Should Redis be used as a cache?` by clearing `Include in reviewed record`.

| # | UI control / section | Exact action | Expected visible result | Narration cue | Duration | Scroll / cursor / crop | Recovery if wrong |
| ---: | --- | --- | --- | --- | ---: | --- | --- |
| 1 | Initial `Stage 1 — Review Inputs` | Pause on the page | Synthetic-data notice, three-stage stepper, and empty inputs are visible | “The application begins…” | 3s | Top; cursor rests away from text | Click `Reset Demo` and reload |
| 2 | `Load Sample Review` | Single click | Review context appears; Solution Intent is populated; status says `Synthetic sample loaded · Inputs are editable` | “I load the bundled review package…” | 4s | Cursor moves deliberately to button | If empty, click `Reset Demo`, then load once |
| 3 | `Solution Intent` tab | Show the synthetic disclaimer and headings | Synthetic SI content and version 1.2 context are visible | Continue package sentence | 3s | Keep top of text area visible | Reload sample if content differs |
| 4 | `Review Transcript` tab | Single click | `Synthetic Teams-style Review Transcript` shows speakers and timestamps | “…and a timestamped transcript.” | 3s | Do not expose local paths | Return to SI and retry tab click |
| 5 | `Solution Intent` tab | Single click | SI input returns | Short pause | 2s | Top | None |
| 6 | `Analyze Review` | Single click | Three-step processing overlay appears, then route becomes `/human-review` | “Analyze Review validates…” | 5s | Cursor remains still during processing | If analysis errors, reset and load untouched sample |
| 7 | `Changes Requested` and metrics | Point, do not click | Outcome and counts show 1 decision, 3 findings, 1 risk, 2 actions, 1 question, 2 missing information | Read outcome and counts | 7s | Top of Stage 2 | If route is wrong, use `← Back to Review Inputs`, reanalyze |
| 8 | `Decisions · 1` | Select and hold | PostgreSQL decision is visible | “The decision accepts managed PostgreSQL…” | 5s | Keep statement in center crop | Re-select tab |
| 9 | `Findings · 3` | Select | Three editable findings are available | “Findings identify…” | 6s | Scroll only enough to show first finding | Re-select tab |
| 10 | First `Supporting evidence (3)` | Expand | SI and transcript evidence for failover is visible and read-only | “Every item retains a source quote…” | 5s | Crop to evidence, not overlaying text | Collapse other expanders |
| 11 | `Risks · 1` | Select | Database-sizing risk and evidence controls appear | “Database sizing is a release risk.” | 4s | Center risk description | Re-select tab |
| 12 | `Missing Info · 2` | Select briefly | RTO/RPO and support-ownership missing information are visible | Continue findings sentence | 4s | Natural page scroll is acceptable | Re-select tab |
| 13 | `Actions · 2` | Select | Two action items appear | “The reviewer can inspect evidence…” | 4s | First action centered | Re-select tab |
| 14 | First `Owner (optional)` | Select all `Alex Chen`; type `Taylor Kim` | Field now reads `Taylor Kim` | “I change the first action owner…” | 5s | Pause after edit | Restore exact value; do not use a real employee name |
| 15 | `Questions · 1` | Select | Redis question is visible and included | “…then exclude the unresolved Redis question.” | 3s | Keep checkbox and question together | Re-select tab |
| 16 | `Include in reviewed record` | Clear the visible checkbox | Redis question is marked for omission | “Evidence stays read-only.” | 4s | Use visible checkbox row/label; pause after | If still checked, use keyboard Space on focused checkbox |
| 17 | `Confirm Reviewed Record & Generate Outputs` | Single click | Three-step output overlay appears, then route becomes `/generated-outputs` | “Only now do I confirm…” | 5s | Fixed button is visible; no scrolling required | If validation fails, restore `Taylor Kim` and the exclusion |
| 18 | `Governance package ready` | Hold | Stepper and workflow cards all show `Complete`; outcome is `Changes Requested`; 2 mock work items | “The application preserves those choices…” | 4s | Top of Stage 3 | Use `← Back to Human Review` only if edit is wrong |
| 19 | `Generated Review Record` | Show `Action Items` area or use a prepared clean cut | First action owner is `Taylor Kim`; Redis is absent | “…Taylor Kim appears in the review record…” | 4s | Crop to readable record section | Return to Human Review and regenerate if values differ |
| 20 | `Mock Azure DevOps Work Items` | Scroll into view | Warning says `No real Azure DevOps work item has been created.`; first item assigned to Taylor Kim | “Two mock Azure DevOps actions…” | 5s | Hold warning and first card | If count differs, restart the deterministic take |
| 21 | Completion panel | Return to top and hold | Workflow remains complete; `Start New Review` is visible | End demo segment | 3s | Do not click restart | None |

## Automation note

Streamlit styles the checkbox with a wrapper. In automated recording, target the visible
checkbox row or use the CLI's `uncheck` action rather than clicking the small internal SVG. This
does not affect normal manual use.
