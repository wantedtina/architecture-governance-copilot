# Historical presentation archive

Document role: `HISTORICAL_MATERIALS_INDEX`. Updated 14 September 2026.

This directory contains nine PowerPoint iterations from the earlier video-production work. They are retained for traceability. No deck here matches all the later revisions in the video explicitly accepted and named **V1** by the user. The accepted **V2** final submission has its own corresponding PowerPoint deck.

Names such as `Final`, `Updated`, and `Revised` describe historical iterations. They do not identify the 14 September final submission. The table below records content differences, not a verified chronological order or a one-to-one mapping to historical video exports.

## Deck inventory

All filenames below begin with `Architecture_Governance_Copilot_Video_Deck` and end with `.pptx`. The complete files are present in the original project directory `/Users/wantedtina/Repos/architecture-governance-copilot/video/presentation/`. A fresh checkout or another worktree may contain only the tracked subset.

| Filename suffix | Slides | Distinguishing content |
| --- | --- | --- |
| No suffix | 5 | Original review-focused proposal and an implemented-versus-future provider diagram |
| `_Updated` | 5 | Adds SI drafting to the proposal while retaining the implemented-versus-future provider diagram |
| `_Final` | 5 | Uses a local application architecture with Streamlit, application services, deterministic providers, models and outputs |
| `_System_Architecture` | 5 | Replaces the architecture page with an image-based proposed deployment view |
| `_Revised` | 5 | Retains the same high-level slide text as `_System_Architecture`; text inspection alone does not establish all visual differences |
| `_Enterprise_SI` | 6 | Adds a synthetic SI context page covering document control, architecture evidence and governance |
| `_Project_Context` | 5 | Uses a Project Context Package as the drafting input and retains the image-based deployment view |
| `_AI_Factory` | 5 | Architecture text names AI Factory, a database and enterprise APIs, including a Teams API |
| `_Connected_Architecture` | 5 | Expands integration adapters and separates Azure Repos and Azure Boards; still describes Teams API retrieval and publishing a confirmed record to Confluence |

Inventory evidence: slide count and text extracted read-only from all nine local PPTX packages. This was not a full PowerPoint rendering or visual equivalence test. Similar text does not prove identical layout, images or notes. Earlier naming and file timestamps alone do not establish which video used each deck.

## Differences from the accepted V1 direction

The later accepted V1 uses revised slide artwork rather than a fully synchronized deck in this directory. Its process and solution pages were revised, including the continuous process flow and the explicit Confluence source-of-truth boundary. Its architecture shows manual Teams transcript intake, read-only Confluence access, separate peer user boxes for Project Team and Domain Architect, and COP observability.

For example, `_Connected_Architecture` still says `Teams API` / `Retrieve permitted review transcript` and `Confluence API` / `Retrieve SI content · publish confirmed record`. These descriptions predate the accepted manual-import and user-edited-Confluence decisions. Retain them as historical evidence, not current product or integration claims.

## Related files

- `system-architecture.dot`: historical architecture diagram source in this directory.
- `Architecture_Governance_Copilot_Video_Deck_Connected_Architecture.pptx.inspect.ndjson`: historical inspection output, not a submission deliverable.
- Earlier narration, video outputs and production scripts remain elsewhere under `video/`. A precise deck-to-video mapping has not been verified for every iteration.

## Find the accepted versions

- [All video versions](../versions/README.md).
- [V1 accepted base](../versions/v1/README.md): its actual slide artwork, architecture, narration and captions.
- [V2 final submission](../versions/v2/README.md): the accepted human-voice video, matching six-slide PPTX and architecture PDF.
- [Production and archive index](../../docs/VIDEO_PRODUCTION.md): exact external source and final-file paths.

Keep this directory at its existing path so older scripts and documentation retain their references. Preserve all existing files. Store new revisions in their own version workspace; do not add a new final deck here or overwrite a historical deck. This index does not move files, change application behavior, or authorize rerendering historical material.
