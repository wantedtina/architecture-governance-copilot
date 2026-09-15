# Video handoff for future revisions

Document role: `CURRENT_VIDEO_REQUIREMENTS`. Updated 15 September 2026. This records confirmed decisions and accepted properties; it does not authorize producing V3. New explicit user instructions supersede this record. Historical preparation-only notices describe their original checkpoints, not current task authority.

## Read first

Read repository `AGENTS.md`, this file, `TOOLING_SETUP.md`, then `v2/README.md`, `v2/CHANGES.md`, `v2/narration/NARRATION.md` and the V2 deliverables before proposing changes. Inspect current application Git state and maintained product documentation separately. A production plan or architecture drawing is not evidence that an integration works.

## Explicit user decisions

- Audience: Accelerate 3.0 hackathon judges. Introduce the complete project, followed by the complete end-to-end demonstration.
- Communicate in Chinese; all deliverables, narration and captions are English. Maximum video duration is four minutes. The supplied organizer screenshot specified 200 MB combined attachments; it was not a live portal check.
- Keep title first, followed by problem, solution, architecture, full demo, improvements and closing. Human Review is central, but never restore the rejected pre-title demo cold open.
- Use natural first-person speech to judges, especially opening and close. Keep English captions, cursor halo and click-target highlighting.
- Preserve branding and the accepted cover/closing artwork. Project Team and Domain Architect have equal visual standing and different responsibilities; no Primary users or extra Human reviewers hierarchy.
- Keep the process snake: 1–3 across the top, down to 4 at bottom right, then left through 5 and 6. Tool/Owner labels clarify the second dimension.
- Confluence remains the SI source of truth. The app produces drafts and suggestions; users decide and make edits in Confluence themselves. No app writes to Confluence.
- Keep SI drafting separate from governance review. Teams transcripts are imported manually; no Teams/Graph API connection is included.
- Architecture title is System Architecture / Architecture Governance Copilot, without Production/Target/fake labels. Include Service Bench, SKE, adapters, database, read-only Confluence, AIF, Azure Repos/Boards, and COP with automatic SKE telemetry and Grafana/Kibana.
- The assistant handles production; the user records the provided narration. The final V2 uses the user's twelve recordings. The sentence “That's our response to the feedback.” was deliberately omitted and must remain absent unless the user changes that decision.
- Company-internal integration, access, SPOC and submission are handled by the user. Uploads, submission and contacting others need explicit authorization. The prior GitHub Release upload was specifically authorized; this is not blanket future authorization.
- Final submission files are the video, matching PPTX and architecture PDF. The three approved form fields are preserved in V2 production history. Do not invent benefit numbers.

## Accepted baseline properties

These were accepted in the artifacts, not all individually dictated: 1080p/30 fps H.264/AAC, navy/white with restrained blue/green accents, Arial-style typography, no background music, preserved team credit strings `Two Tokens One Brain`, `Zhang1, Yang — Team Lead`, `Wang, Ted — Team Member`. V1 is 238 seconds with 48 caption cues; final V2 is 219 seconds with 47 cues. Do not silently change these properties during a small revision.

## Demo and application truth

Both accepted videos reference application commit `81835b9ced0c709f4003522557b6423bc4bdaa18`. Capture used development Internal fake for the full workflow including Work Item Delivery. The footage is real application interaction with synthetic local transport; it does not prove live enterprise publication.

Preserve the reviewed demonstration: action `Document retry and backoff controls`; owner Riley Chen changed to Taylor Kim while the original quote remains visible; due 2026-09-18, High priority, parent SYN-204; finding 3 `Routing-record retention lacks approval` excluded; outcome Changes Requested. Follow source evidence to confirmed record, minutes and work-item preview. Delivery includes request inspection, confirmation, Create, GET read-back and receipt 7001 revision 1. Changing the transcript invalidates prior outputs and requires new review, while completed delivery history stays recorded. Transcript addition: `Additional context for manual review: support ownership still requires confirmation.`

Demonstrated capabilities include deterministic drafting, strict models and evidence validation, editable human review, confirmation, output generation, local simulated delivery controls and stale-output invalidation. No claim of general semantic AI drafting, enterprise identity verification, formal approval, live AIF/Confluence/ADO acceptance, deployed DB/authentication, working SKE-to-COP telemetry, measured ROI or production scalability is established. Persistence and enterprise services in the diagram are agreed system design. Do not dwell on fake terminology in narration or erase native app notices.

## Rejected approaches

Disconnected UI-only tours, a demo clip before the cover, stiff slogan-like opening/closing, disconnected process rows, user-role hierarchy, a fake-only architecture, Production wording in the architecture title and Teams API ingestion were rejected or superseded. Explain any reason to revisit them and obtain user approval first.

## Starting V3

1. Read and inspect the accepted V2 files, then gather only the new requirements and unresolved specifics. Preserve accepted content that does not need change.
2. Verify application revision, available tools and dependencies. Record exact model/reasoning settings only if exposed; their historical equivalence is not independently known.
3. Create a separate `video/v3/` with the same five material folders, `README.md` and `CHANGES.md`. Record the parent V2 manifest and distinguish proposed changes from user-approved changes.
4. Copy required inputs into the V3 production workspace. Resolve historical absolute paths and output destinations before executing any script. Use isolated dependencies, never the application environment for video tools.
5. Confirm the final application commit, demo path and concrete values with the user before new app recording. Do not modify application behavior to make footage work; report defects to the application workstream.
6. Verify picture, audio, captions, deck/diagram correspondence, duration, total size and hashes. Preserve V1/V2 accepted files. Record user acceptance and any remaining verification limits.

This reorganization verifies copied bytes and source locations only. It does not certify a portable, freshly rerendered production environment. Historical commands, including non-idempotent scripts, are preserved for reference rather than immediate execution.
