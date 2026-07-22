# Architecture Governance Copilot — Narration Script

Target: `03:42`. The script is aligned to the updated four-stage application flow.

## Timed script

### 00:00–00:12 — Opening

Architecture Governance Copilot is our Accelerate 3.0 proof of concept from Two Tokens One Brain.
It turns architecture work into an accountable, evidence-backed governance record.

### 00:12–00:36 — Current process

Product Owners and development teams prepare the Solution Intent using a required template. The
official document remains in Confluence, an Azure DevOps governance ticket tracks the review,
and a Domain Architect reviews it through Teams meetings and revision rounds. This proof of
concept uses synthetic local content representing those sources.

### 00:36–00:44 — Pain points

Those handoffs scatter decisions, risks, actions, and evidence. Teams then rebuild the
governance record manually.

### 00:44–00:52 — Proposed solution

The Copilot drafts the Solution Intent, structures its governance review, preserves evidence,
and keeps every confirmation under human control.

### 00:52–01:04 — Target system architecture

Target architecture deploys the front end in Service Bench and backend API in SKE. Controlled
adapters connect Confluence, Teams, AIF LLM, database, and Azure DevOps.

### 01:04–03:19 — Working proof of concept

The application opens at Draft Solution Intent, the first of four visible stages. Demo mode uses
synthetic data, local processing, and no external connections.

I load the SI template, selected source-code context, and supporting notes for a fictional
Digital Payment Notification Service. Generate SI Draft validates that context and creates an
editable draft. The screen makes clear that this is a drafting aid, not publication or approval.
I explicitly confirm the draft before it moves to Review Inputs.

The confirmed SI is preserved. I add the matching Teams-style transcript and review metadata,
then select Analyze Review. A separate Human Review page opens with a Changes Requested outcome.
The summary shows one decision, three findings, one risk, two actions, one open question, and two
missing-information items.

The decision accepts managed PostgreSQL as the system of record. Findings identify missing
traffic-failover behaviour, missing RTO and RPO values, and undefined production support
ownership. Database sizing is a release risk. Each item retains a source quote from the Solution
Intent, the transcript, or both.

This remains a proposal, not an approval. The reviewer can inspect evidence, edit fields, and
include or exclude items. I change the first action owner to the clearly synthetic value Taylor
Kim, then exclude the unresolved Redis question. Evidence stays read-only.

Only after that human review do I confirm the record and generate outputs. The completed package
preserves those choices: Taylor Kim appears in the review record and first Azure DevOps
work-item preview, while the Redis question is absent. The output is explicitly preview-only;
nothing was submitted to Azure DevOps.

### 03:19–03:35 — Business value and controls

This workflow reduces manual review administration, supports more consistent records, and
improves evidence traceability. Structured outputs can support future integration, but every
record remains human-reviewed and formal decision authority stays with the Domain Architect.

### 03:35–03:42 — Closing

Architecture Governance Copilot demonstrates a practical, human-controlled path from
architecture context to accountable action. Two Tokens One Brain.

## Script statistics

- Spoken word count: **446**
- Video duration: **03:42**
- Average pace: approximately **121 words per minute**
- Narrator: one consistent English voice

## Pronunciation notes

- `SI`: say “ess-eye”.
- `ADO`: say “A-D-O”.
- `RTO`: say “R-T-O”.
- `RPO`: say “R-P-O”.
- `PostgreSQL`: say “post-gres-Q-L”.
- `Confluence`: stress the first syllable.
- `Taylor Kim`: synthetic reviewer-approved owner used only in the demo.

## Clean TTS-ready version

Use the eight timed sections above in order, without reading their headings.
