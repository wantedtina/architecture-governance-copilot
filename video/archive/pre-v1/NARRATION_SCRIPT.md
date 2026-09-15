# Architecture Governance Copilot — Narration Script

Target: `03:58`. The script emphasizes the AI-assisted workflow, its human controls, and the
distinction between the deterministic proof of concept and proposed production integrations.

## Timed script

### 00:00–00:11 — Opening

Architecture Governance Copilot is our Accelerate 3.0 proof of concept from Two Tokens One Brain.
It turns architecture work into an accountable, AI-assisted governance record.

### 00:11–00:30 — Current process

Product Owners and development teams prepare the Solution Intent in Confluence. An Azure DevOps
governance ticket tracks the review, and a Domain Architect reviews through Teams meetings and
revision rounds. This proof of concept uses synthetic local content representing those sources.

### 00:30–00:38 — Pain points

Those handoffs scatter decisions, risks, actions, and evidence. Teams then rebuild the governance
record manually.

### 00:38–00:52 — Proposed solution

AI accelerates two high-effort steps: synthesizing confirmed project context into a draft Solution
Intent, then interpreting the SI and review transcript into structured, evidence-linked governance
proposals. Humans retain control.

### 00:52–01:14 — Target system architecture

The front end runs in Service Bench; the backend and governed state run in SKE. Permission-aware
Confluence, Teams, and Azure DevOps connectors retrieve only user-selected sources. Azure Repos
supplies the branch, while Azure Boards supplies governance metadata. The backend builds a
human-confirmed context package, and only that approved scope reaches AI Factory, or AIF.

### 01:14–03:30 — Working proof of concept

The application opens at Project Context, the first of five visible stages. The fictional workspace
shows its ADO governance reference, SI template, repository branch, supporting documents, and
source-selection controls. In production, the permission-aware connectors retrieve only
user-confirmed sources. Here, deterministic synthetic fixtures keep the demonstration reliable and
offline.

I inspect each selected preview, refresh the context, and explicitly confirm the package before any
AI-assisted drafting. Generate SI Draft validates that confirmed context and creates an editable
proposal. The proposed SI appears first, while source details remain available beneath it. This is
a drafting aid, not publication or approval, so I confirm it before continuing.

The confirmed SI is preserved. I add the matching Teams-style transcript and review metadata, then
select Analyze Review. AI-assisted analysis proposes a structured governance record, and a separate
Human Review page opens with a Changes Requested outcome.

The summary covers a decision, findings, a risk, actions, an open question, and missing information.
It accepts managed PostgreSQL as the system of record while identifying unresolved failover,
resilience, support-ownership, and capacity evidence. Every proposal retains a source quote from the
Solution Intent, the transcript, or both.

The reviewer can inspect evidence, edit fields, and include or exclude items. I change the first
action owner to the clearly synthetic value Taylor Kim, then exclude the unresolved Redis question.
Evidence stays read-only.

That human checkpoint is essential: AI proposes structure and evidence links, but it does not decide
the review outcome, approve architecture, or publish records. The Domain Architect remains
accountable for the decision, while the project team remains accountable for completing actions and
evidence. The system makes those boundaries visible throughout the workflow.

Only after human review do I confirm the record and generate outputs. The completed package
preserves those choices in the review record and Azure DevOps work-item previews. Nothing was
submitted to Azure DevOps.

### 03:30–03:48 — Business value and controls

AI reduces first-pass drafting and review administration, while evidence grounding makes every
proposal easier to verify. Structured outputs support future integration, but every record remains
human-reviewed and formal decision authority stays with the Domain Architect.

### 03:48–03:58 — Closing

Architecture Governance Copilot demonstrates a practical, human-controlled path from governed
context, through AI assistance, to accountable action. Two Tokens One Brain.

## Pronunciation notes

- `SI`: say “ess-eye”.
- `ADO`: say “A-D-O”.
- `AIF`: say “A-I-F”; it stands for “AI Factory”.
- `SKE`: say “S-K-E”.
- `PostgreSQL`: say “post-gres-Q-L”.
- `Confluence`: stress the first syllable.
- `Taylor Kim`: synthetic reviewer-approved owner used only in the demo.

## Clean TTS-ready version

Use the eight timed sections above in order, without reading their headings.
