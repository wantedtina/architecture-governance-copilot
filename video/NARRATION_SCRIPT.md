# Architecture Governance Copilot — Narration Script

Target: `03:50` video, approximately 125–135 spoken words per minute during narration. The word
count below covers the spoken script once; the clean version repeats the same text for recording.

## Timed script

### 00:00–00:12 — Opening

Architecture Governance Copilot is our Accelerate 3.0 proof of concept from Two Tokens One Brain.
It turns architecture review discussion into an accountable, evidence-backed record.

### 00:12–00:38 — Governance process and input origins

Product Owners and development teams prepare the Solution Intent using the required template. The
official SI remains in Confluence, with an ADO governance ticket for review tracking. A Domain
Architect reviews it through Teams meetings and revision rounds until formal approval. Here,
synthetic Confluence content is normalized into Markdown, while synthetic text represents a Teams
review transcript produced only when transcription is enabled.

### 00:38–00:58 — Pain points

That process creates repeated administration. Decisions, findings, risks, and actions can be
spread across the SI, meeting discussion, notes, and ADO. Teams manually rebuild the governance
record and tracked work, increasing the risk that evidence, ownership, or requested changes are
missed or recorded inconsistently.

### 00:58–01:10 — Proposed solution

The Copilot structures both normalized inputs, preserves evidence, and pauses for human review
before producing a standardized record and mock ADO actions. It never approves automatically.

### 01:10–03:05 — Working PoC

The application begins with clear synthetic-data and human-accountability notices. I load the
bundled review package: version 1.2 of a fictional Digital Payment Notification Service SI,
review metadata, and a timestamped transcript.

Analyze Review validates both sources and opens a separate Human Review page. The outcome is
Changes Requested. The summary shows one decision, three findings, one risk, two actions, one
open question, and two missing-information items.

The decision accepts managed PostgreSQL as the system of record. Findings identify missing
traffic-failover behaviour, missing RTO and RPO values, and undefined production support
ownership. Database sizing is a release risk. Every item retains a source quote from the SI, the
transcript, or both.

This is a proposal, not an approval. The reviewer can inspect evidence, edit fields, and include
or exclude items. I change the first action owner to the clearly synthetic value Taylor Kim,
then exclude the unresolved Redis question. Evidence stays read-only.

Only now do I confirm the reviewed record and generate outputs. The application preserves those
choices: Taylor Kim appears in the review record and first mock work item, while the Redis
question is absent. Two mock Azure DevOps actions are prepared, and the screen confirms that no
real work item was created.

### 03:05–03:27 — Business value and controls

This workflow reduces manual review administration, supports more consistent records, helps
reduce the risk of missed findings and actions, and improves evidence traceability. Structured
outputs can support future integration, but every record is reviewed before generation, and
formal decision authority remains with the Domain Architect.

### 03:27–03:43 — Architecture and future direction

The extractor interface uses a deterministic demo implementation for reliable offline use. It
does not analyze arbitrary documents or use a production enterprise LLM. A future approved
provider could connect Confluence, Teams, and Azure DevOps; none exists today.

### 03:43–03:50 — Closing

Architecture Governance Copilot shows one practical, human-controlled path from architecture
discussion to accountable action. Two Tokens One Brain.

## Script statistics

- Spoken word count: **462**
- Video duration: **03:50**
- Narrated pace: approximately **130 words per narrated minute**, allowing short visual pauses
- Narrator: one consistent English voice

## Pronunciation notes

- `SI`: say “ess-eye”.
- `ADO`: say “A-D-O”.
- `RTO`: say “R-T-O”.
- `RPO`: say “R-P-O”.
- `PostgreSQL`: say “post-gres-Q-L”.
- `Confluence`: stress the first syllable.
- `Taylor Kim`: clearly synthetic reviewer-approved owner used only in the demo.

## Clean TTS-ready version

Architecture Governance Copilot is our Accelerate 3.0 proof of concept from Two Tokens One Brain.
It turns architecture review discussion into an accountable, evidence-backed record.

Product Owners and development teams prepare the Solution Intent using the required template. The
official SI remains in Confluence, with an ADO governance ticket for review tracking. A Domain
Architect reviews it through Teams meetings and revision rounds until formal approval. Here,
synthetic Confluence content is normalized into Markdown, while synthetic text represents a Teams
review transcript produced only when transcription is enabled.

That process creates repeated administration. Decisions, findings, risks, and actions can be
spread across the SI, meeting discussion, notes, and ADO. Teams manually rebuild the governance
record and tracked work, increasing the risk that evidence, ownership, or requested changes are
missed or recorded inconsistently.

The Copilot structures both normalized inputs, preserves evidence, and pauses for human review
before producing a standardized record and mock ADO actions. It never approves automatically.

The application begins with clear synthetic-data and human-accountability notices. I load the
bundled review package: version 1.2 of a fictional Digital Payment Notification Service SI,
review metadata, and a timestamped transcript.

Analyze Review validates both sources and opens a separate Human Review page. The outcome is
Changes Requested. The summary shows one decision, three findings, one risk, two actions, one
open question, and two missing-information items.

The decision accepts managed PostgreSQL as the system of record. Findings identify missing
traffic-failover behaviour, missing RTO and RPO values, and undefined production support
ownership. Database sizing is a release risk. Every item retains a source quote from the SI, the
transcript, or both.

This is a proposal, not an approval. The reviewer can inspect evidence, edit fields, and include
or exclude items. I change the first action owner to the clearly synthetic value Taylor Kim,
then exclude the unresolved Redis question. Evidence stays read-only.

Only now do I confirm the reviewed record and generate outputs. The application preserves those
choices: Taylor Kim appears in the review record and first mock work item, while the Redis
question is absent. Two mock Azure DevOps actions are prepared, and the screen confirms that no
real work item was created.

This workflow reduces manual review administration, supports more consistent records, helps
reduce the risk of missed findings and actions, and improves evidence traceability. Structured
outputs can support future integration, but every record is reviewed before generation, and
formal decision authority remains with the Domain Architect.

The extractor interface uses a deterministic demo implementation for reliable offline use. It
does not analyze arbitrary documents or use a production enterprise LLM. A future approved
provider could connect Confluence, Teams, and Azure DevOps; none exists today.

Architecture Governance Copilot shows one practical, human-controlled path from architecture
discussion to accountable action. Two Tokens One Brain.
