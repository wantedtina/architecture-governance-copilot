# Targeted V2 proposal

Date: 14 September 2026
Status: Awaiting user approval. No V2 production authorized or started.

## Recommendation

Preserve V1's accepted story and visual direction. Prioritize alignment between narration, the visible evidence, and the actual action being demonstrated. Reuse the existing footage and editable SVGs where they work. Use new tools to improve a specific weakness, not to justify a complete rebuild.

## Confirmed constraints

These are user decisions and accepted V1 properties, not new creative suggestions:

- Audience: Accelerate 3.0 hackathon judges. Project: Architecture Governance Copilot. Team: Two Tokens One Brain.
- Chinese session communication. English narration, captions, graphics, files and deliverables.
- Title first, then problem, solution, architecture, full end-to-end demo, response to feedback and natural spoken close. Do not restore a pre-title Human Review cold open.
- Preserve the accepted opening and closing verbatim. Preserve navy/white, blue/green branding, logo proportions and credits. No new music or illustrative theme.
- Maximum video duration: four minutes. Retain 3:58 as the planning target, 1080p/30 fps, H.264/AAC, visible English subtitles and a separate SRT. Combined submission attachments stay below the screenshot-supplied 200 MB limit.
- Preserve the process snake: 1, 2, 3 across the top, down to 4, then left to 5 and 6. Keep Tool/Owner labels.
- Confluence is the SI source of truth. The app produces drafts and suggestions; users write and edit Confluence themselves. Draft confirmation and review-input confirmation remain separate.
- Project Team and Domain Architect have equal standing as users, with different responsibilities and permissions. Formal decisions remain with the Domain Architect.
- Preserve Service Bench, SKE, the database, adapters, enterprise-service topology and automatic SKE telemetry to COP with Grafana/Kibana. Teams transcripts are manually imported. Do not add a Teams API or a Production/Target/fake architecture title.
- Application commit stays 81835b9ced0c709f4003522557b6423bc4bdaa18. Capture remains the development Internal fake path. Do not modify application behavior, fixtures, the refinement register, dependencies or history for the video.
- Preserve the retry action, Riley Chen to Taylor Kim owner edit, due date 2026-09-18, High priority, parent SYN-204, excluded finding 3, Changes Requested outcome, and local delivery receipt 7001/revision 1. Preserve the exact transcript addition recorded in the handoff.
- Show original evidence, human edits and confirmation, minutes/work-item outputs, controlled delivery, and inputs changed/outputs invalidated. Completed delivery is not undone by invalidation.
- Preserve native notices. Do not add claims of accepted live integrations, actual deployed persistence/COP, verified enterprise identities, formal approval, or measured savings. The architecture describes the agreed system design.
- Keep the approved three form fields unchanged. Company access, SPOC, SharePoint, uploads and submission remain with the user. Human voice replacement remains pending.

## What was inspected

The handoff and tooling setup were read in full, along with AGENTS.md. Inspection covered the accepted script, timeline, audio timing and caption JSON, current SVG/PNG slides and architecture, historical architecture, source capture scripts, production render/voice scripts, source footage metadata and V1 frame/contact-sheet evidence. Frames at 131 and 190 seconds were freshly extracted from the accepted MP4 to confirm the observations rather than relying only on historical QA images.

This was visual/frame, source and timing inspection, not a claim of a new complete real-time human listening review.

Authoritative inputs:

- Handoff: `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/VIDEO_HANDOFF.md`
- Tooling history: `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/TOOLING_SETUP.md`
- V1: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/export/architecture-governance-copilot-v2.2-narrated.mp4`
- Script: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/export/NARRATION_V2.2.md`
- Timeline: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/export/edit-timeline.json`
- Slides: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/frames/`
- Architecture: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/export/system-architecture.svg`
- Raw footage: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2/clips/`
- Capture sources: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2/tools/`
- Render and speech sources: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/tools/`
- Backup: `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/V1_BACKUP_2026-09-14/`

The original application remains clean on `codex/final-stage-i2-review-summary` at the locked commit. The existing materials worktree remains on `codex/submission-2026-09-14-materials` at the same commit, with only untracked `docs/submission/`. No fetch or company access check was performed. Cached upstream status is unchanged; it is not fresh remote acceptance.

V1 SHA-256 remains `fe52d4bdf9cf42114a77d9646af4a27f2de2bc82108e845491cdc8f89282068a`. All 695 backup entries and protected production sources passed preservation checks.

## Capability verification

| Component | Verified now | Limits and implications |
| --- | --- | --- |
| Build Web Data Visualization 0.1.21 | Account installed/enabled. Router available. UML/software architecture and node-link layout specialists read successfully. V1 SVG parsed and required labels found. | The specialist instructions are available; this is not a separate rendering engine. Browser SVG export was not verified because local HTTP access timed out. Use the existing SVG source and fixed accepted layout; no new graph engine is needed by default. |
| Presentations 26.904.11930, Artifact Tool 2.8.59 | A neutral, one-text-box test exported to PPTX and PNG. The PNG was visually inspected and native editable text was verified inside the PPTX. | This verifies basic export/rendering, not conversion of the full V1 design or PowerPoint UI fidelity. No V2 slide was created. |
| Playwright CLI 0.1.19, Playwright 1.63.0-alpha-2026-08-31, Chrome 152 | Neutral about:blank page, real button click, action annotation, screenshot and a 1.72-second WebM recording passed. WebM decoding passed. | The test output defaulted to 800x450/25 fps. Production capture resolution must be explicitly set and verified; 1080p capture is not proven. A local HTTP test server timed out in Chrome and curl; file navigation was blocked. Real app capture is not yet verified in this session. |
| Remotion plugin 1.0.7 | Account installed/enabled, 12 skills discoverable. Router, rendering, captions and SRT import instructions read. Skill frontmatter version 4.0.506 is separate from plugin package version. | Remotion SDK, renderer, CLI and captions modules were not found in the checked bundled and designated production module roots. No SDK API, Studio or render test ran. Installing a skill is not rendering readiness. |
| Existing FFmpeg 7.1 | V1 frame extraction and neutral WebM decoding passed. V1 is 238 seconds, 1920x1080, 30 fps. | FFmpeg remains the established fallback. This turn did not re-render V1 or V2. |

V1 captions have 48 cues, no overlap, and a shortest cue of approximately 2.39 seconds. The observed issues are scene/cue alignment and attention placement, not a demonstrated global subtitle reading-speed failure. The source footage is 1600x900/25 fps; V1's delivery format is 1920x1080/30 fps. Avoid aggressive digital zoom on those source clips.

The CLI's built-in action annotation exposed a technical locator string in the neutral recording. It is unsuitable for judges without adjustment. Preserve V1's human-readable click labels and yellow pointer treatment instead of inserting raw automation callouts.

The older CLI plugin copies remain intact. The current catalog exposes the desktop bundles, with no duplicate entries observed. No plugins, dependencies or settings were installed, removed or upgraded in this turn.

No model or reasoning-setting switch was requested or performed. Exact active model/effort and the historical session's exact values are not exposed by the available runtime metadata, so equivalence cannot be independently certified. Do not silently select a different model later.

## Proposed changes, not yet approved

| Priority / area | Observed V1 problem or limitation | Proposed treatment and tool | Expected improvement and preservation rule |
| --- | --- | --- | --- |
| High: Human Review footage | At 2:11, the caption/narration refers to Riley's original words while the quote body is below the visible frame. It appears in an adjacent shot. | Re-time the existing human-review source first. Keep the owner edit visible, then hold the actual quote while it is discussed. Use an event-based edit list with FFmpeg or, once verified, Remotion sequences. Use Playwright for a pickup only if the existing source cannot provide a readable shot. | The judge sees the evidence at the moment it is referenced. Preserve actual UI state, Riley/Taylor values, finding exclusion and explicit confirmation. |
| High: Delivery footage | At 3:10, the receipt is already visible while the spoken sentence still covers confirmation and creation. | Align request inspection, Confirm, Create and GET-verified receipt to separate spoken beats. Reuse delivery footage before considering a pickup. | Makes the control sequence easier to follow without changing the demonstrated behavior or claiming live ADO publication. |
| Medium: Architecture diagram | The dense full diagram stays static for 23 seconds. Small supporting labels and the adapter/ADO connector junction require visual searching during narration. | Retain the current architecture-map SVG and fixed node order. Apply the visualization UML/layout guidance to spacing and connector routing only. In the video, use restrained sequential emphasis on the region being discussed, returning to the complete diagram. Keep the static SVG/PNG/PDF complete. | Faster orientation with the same system design. Do not change diagram family, topology, roles, manual Teams path, read-only Confluence or DB/COP semantics. No decorative animation or automatic full relayout. |
| Medium: Process and solution slides | The accepted flow and Confluence statement are already clear, but several text regions appear simultaneously while narration discusses only one. There is no current editable PPTX matching V1. | Retain wording and layout. Optionally emphasize the current step/lane without hiding the complete sequence. Preserve the Confluence boundary throughout its explanation. Presentations can supply a faithful editable deck if approved as a companion deliverable; it is not necessary to rebuild slides solely for the video. | Helps attention follow the narration. Keep the snake, Tool/Owner lines, colors and accepted title/closing assets. Editable PPTX is optional, not a new mandatory submission item. |
| Medium: Narration and captions | Several sections are slowed to 0.90x; the eight-second feedback section is accelerated to about 1.137x. Cue subdivision partly uses word-count proportions. | Keep accepted wording as the initial script, especially the opening and close. Improve pauses and cue boundaries before rewriting. Use the actual narration waveform for alignment and preserve sentence-based two-line captions. Use Remotion caption utilities only after SDK availability is verified; existing SRT/ASS remains the fallback. | More even pacing and tighter speech/picture alignment. No karaoke styling, new slogans or unsupported claims. Any necessary wording changes should be shown as an explicit small diff. |
| Medium: Final assembly | V1 rendering depends on absolute paths and previously encoded clips; cached static clips can survive source edits unless deliberately rebuilt. | In the separate V2 workspace, use one asset manifest and timeline with immutable V1 inputs. Prefer reusing raw source clips and a single final encode for changed sections. Remotion is useful only if frame-based timing/overlays reduce this maintenance problem; otherwise retain the FFmpeg pipeline. | More reproducible revisions and simpler human-voice replacement, with fewer avoidable re-encodes. No whole-video rewrite merely to demonstrate Remotion. |

Do not rebuild the cover, closing, approved form text, functioning drafting/review flow or branding. Do not generate decorative imagery, install draw.io, add a dashboard/3D scene, or create a mobile product. The deliverable remains the accepted 16:9 video; smaller-player readability is checked within that format.

## Production plan after approval

1. **Freeze scope and inputs.** Use this proposal as the approved change list. Retain the locked commit and concrete demo values. Verify V1 hashes again before any production write. Confirm changes to commit, route or values with the user before any new capture.
2. **Create a timing map from V1.** Map each key sentence to its source shot, click and visible result. Keep all 12 sections in order and retain the 238-second budget initially. Reallocate pauses locally before shortening approved narration or dropping content.
3. **Resolve only needed technical prerequisites.** For fresh capture, first resolve local HTTP reachability and verify capture dimensions on a neutral page. For Remotion, establish license suitability with the user before any acceptance/payment/account step, pin compatible packages in this external workspace, and run a neutral import/render test before relying on it. Do not use application dependencies for production tools.
4. **Make the targeted visual changes.** Preserve the accepted architecture and slide content. Adjust geometry and restrained focus treatment where it aids reading. Produce a matching editable PPTX only if included in the approval.
5. **Repair footage timing, then assess pickups.** Reuse existing clips for the two confirmed alignment problems and the evidence-to-output comparison. Only capture missing readable beats through the real unchanged app. Any discovered function defect goes back to the application workstream; do not patch the app for filming or fabricate state.
6. **Assemble a provisional narrated review cut.** Use the accepted English script and temporary narration. Keep human-readable click labels, pointer halo, native notices and reserved caption band. Review the complete story at normal playback speed and in a smaller player.
7. **Replace with the user's recording.** Fit picture and sentence-aligned captions to the real delivery. Avoid heavy voice time-stretching. Preserve the four-minute limit; propose a small script/timing adjustment for approval if natural speech cannot fit.
8. **Verify and package externally.** Check first frame/title, all required demo steps and values, evidence readability, confirmation-before-output/create, receipt verification, invalidation, no cut-off words, no caption overlap, 1080p/30 fps, duration <=240 seconds, full decode and attachment-size budget. Export MP4, SRT, architecture SVG/PNG/PDF, narration script and source/timing manifest. No upload or submission.

## Workspace and current stop point

Separate V2 workspace:
`/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2/`

Current contents are planning and isolated capability checks only. The neutral PPTX, PNG and 1.72-second browser recording are technical checks, not V2 deliverables. No application was launched or recorded, no V2 design or composition was created, and no application files or accepted V1 assets were modified. The owned test browser and HTTP server were closed.

User approval is required before the production plan starts, as explicitly requested in this turn.
