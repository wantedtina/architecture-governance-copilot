# On-screen Text

## Frame 1 — Opening

```text
Architecture Governance Copilot
Two Tokens One Brain
Accelerate 3.0 Hackathon
Zhang1, Yang — Team Lead
Wang, Ted — Team Member
```

## Frame 2 — Current governance process

```text
Project Team
→ Solution Intent in Confluence
→ Domain Architecture Review in Teams
→ Findings and Requested Changes
→ SI Revision
→ Further Review
→ Approval by Domain Architect

ADO governance ticket · tracked actions · manual handoffs

Confluence content → normalized SI content
Teams transcript → normalized review transcript
```

## Frame 3 — Proposed solution

```text
Project Context Package
+
Review Transcript + Metadata
↓
Draft + Governance Review
↓
Human Review and Confirmation
↓
Review Record + ADO Item Previews

Evidence Traceability · Structured Findings and Actions · Human Accountability
No Automatic Approval
```

## Frame 4 — Target system architecture

```text
Domain Architect
→ Service Bench: AGC Front End
→ SKE: AGC Backend API → Provider & Integration Adapters

Adapters connect:
├── Confluence API
├── Approved Source Repository API
├── Teams API
├── AI Factory (AIF): approved enterprise LLM endpoints
└── Azure DevOps API

SKE governed state:
└── Database

Enterprise Controls: identity · secrets · audit · monitoring · data policy
Proposed deployment and integration view · Current PoC uses local deterministic providers.
```

## Frame 5 — Closing

```text
Architecture Governance Copilot
Two Tokens One Brain
Zhang1, Yang — Team Lead
Wang, Ted — Team Member

Traceable evidence. Human-controlled decisions.
```

## Application callouts

- `Synthetic Data`
- `Changes Requested`
- `Evidence Traceability`
- `Human Review`
- `Generated Review Record`
- `Azure DevOps Work Item Previews`
- `No Automatic Approval`

## Disclosures

- `Synthetic data · Deterministic demo extractor · No external connections`
- `Preview only · Nothing submitted to Azure DevOps`
- `Formal decision authority remains with the Domain Architect.`

## Subtitle treatment

Burned-in review-draft subtitles use white text on a 78%-opaque navy rounded rectangle, centered
inside the lower title-safe area. Maximum two lines where practical. Do not cover application
buttons, evidence text, the owner field, or the ADO warning.
