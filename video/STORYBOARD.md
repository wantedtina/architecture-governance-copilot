# Architecture Governance Copilot — Storyboard

Total duration: **03:50**. The real application occupies **01:10–03:05 (01:55)**, the largest
single segment. Exact application labels below were verified against the live local app.

| Time | Duration | Visual content | Narration | Exact UI action | On-screen text | Transition / recording notes |
| --- | ---: | --- | --- | --- | --- | --- |
| 00:00–00:12 | 12s | Frame 1: opening title | Opening paragraph | None | Project, team, hackathon, both members and roles | Fade up from navy; slow gradient accent; no official logo |
| 00:12–00:38 | 26s | Frame 2: current governance process | Process and input-origin paragraph | None | Confluence SI, Teams review, ADO ticket, normalization, Domain Architect authority | Simple left-to-right process reveal; keep all labels readable |
| 00:38–00:58 | 20s | Frame 2 alternate crop emphasizing manual handoffs | Pain-points paragraph | None | `Manual handoffs`, `Distributed evidence`, `Repeated administration` | Direct cut; no unsupported metric |
| 00:58–01:10 | 12s | Frame 3: proposed solution | Proposed-solution paragraph | None | `Evidence Traceability`, `Human Review`, `No Automatic Approval` | Short dissolve |
| 01:10–01:22 | 12s | Real Stage 1 app at 100% browser zoom | First demo paragraph begins | Click `Load Sample Review` | `Synthetic Data` | Cursor pause before and after click |
| 01:22–01:34 | 12s | Review context, Solution Intent, then transcript tab | First demo paragraph completes | Click `Review Transcript`, then return to `Solution Intent` | `Normalized SI + Transcript` | Show headings, speaker names, and timestamps; no local paths |
| 01:34–01:45 | 11s | Analyze overlay and routed Stage 2 | Second demo paragraph begins | Click `Analyze Review` | `Evidence-backed analysis` | Preserve real processing overlay and route change |
| 01:45–02:05 | 20s | `Changes Requested`, summary metrics, decision tab | Second paragraph completes; decision sentence begins | Point to outcome and counts; open `Decisions · 1` | `Changes Requested` | Hold long enough to read one decision |
| 02:05–02:28 | 23s | Findings, risk, and evidence | Findings/evidence paragraph | Open `Findings · 3`; expand first supporting evidence; open `Risks · 1` | `Evidence Traceability` | Use subtle crop toward content, never cover evidence |
| 02:28–02:44 | 16s | Actions tab and owner field | Human-review paragraph begins | Open `Actions · 2`; replace `Alex Chen` with `Taylor Kim` | `Human Review` | Show edit clearly; Taylor Kim is synthetic |
| 02:44–02:54 | 10s | Questions tab | Human-review paragraph completes | Open `Questions · 1`; clear `Include in reviewed record` | `Reviewer controls inclusion` | Show Redis question before exclusion |
| 02:54–03:05 | 11s | Generate overlay, routed Stage 3, fast clean cuts to record and mock ADO section | Output paragraph | Click `Confirm Reviewed Record & Generate Outputs`; show Taylor Kim and ADO warning | `Generated Review Record`; `Mock ADO Actions` | Preserve real route change; cut dead scrolling; show `No real Azure DevOps work item has been created.` |
| 03:05–03:27 | 22s | Frame 3 with app-output picture-in-picture or neutral value callouts | Business-value paragraph | None | `Consistent record`, `Traceable evidence`, `Human accountability` | Calm dissolve; qualitative claims only |
| 03:27–03:43 | 16s | Frame 4: implemented vs future architecture | Architecture paragraph | None | `Implemented now` and `Future — not implemented` | Future branch visually dashed and explicitly labelled |
| 03:43–03:50 | 7s | Frame 5: closing | Closing paragraph | None | Team and both members; concise close | Fade to navy; end cleanly at 03:50 |

## Recording notes

- Capture the application at 1920 × 1080, 30 fps, with only the local Streamlit page visible.
- Use the existing deterministic processing delay; do not simulate integrations.
- Show real UI state transitions and the actual human edits.
- The source recording may be longer than 01:55; use clean cuts and short holds to fit the
  storyboard without fabricating interaction.
- Subtitles remain within the lower safe area and must not cover buttons, evidence, or owner
  fields.
