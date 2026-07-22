# Architecture Governance Copilot — Video Brief

## Audience

Accelerate 3.0 Hackathon judges and internal stakeholders who understand architecture governance
but may not know this prototype.

## Objective

Show one reliable, end-to-end workflow in less than four minutes: draft a Solution Intent from
synthetic context, confirm it, perform an evidence-backed governance review, and generate a
review record plus Azure DevOps work-item previews.

## Central message

> Architecture Governance Copilot converts Solution Intent content and architecture-review
> discussions into a structured, evidence-backed review, while preserving human review and
> Domain Architect accountability.

## Business problem

The Product Owner and development team prepare a Solution Intent using the organisation's
required template. The official SI is maintained in Confluence, an Azure DevOps governance
ticket tracks review, and a Domain Architect may conduct several Teams meetings and revision
rounds before formal approval. Decisions, findings, risks, actions, and evidence can be
distributed across those sources, creating repeated manual administration and inconsistent
records.

## Proposed solution

The PoC drafts an SI from a template, selected source-code context, and supporting notes. After
human confirmation, it combines the SI with a review transcript, proposes a structured
governance review with source evidence, allows a human to edit or exclude items, and generates a
standardized review record plus ADO work-item previews. Formal approval remains with the Domain
Architect.

## Input origins

### Solution Intent

The official SI remains a Confluence page. The PoC's fully synthetic Markdown file represents
content extracted and normalized from that page. Markdown is a lightweight internal
representation that preserves headings and readable structure; it is not a second official copy
for project teams to maintain. The PoC has no Confluence connector.

Intended future flow:

```text
Confluence SI Page
→ approved connector, API, or export
→ extraction and normalization
→ normalized SI content
```

### Review transcript

Architecture reviews take place in Microsoft Teams. When transcription is enabled and permitted
by meeting configuration and organisational policy, a transcript can contain speakers,
timestamps, and spoken content. Microsoft 365 Copilot may use a transcript for recap or analysis,
but it is not described as always creating one. The PoC uses fully synthetic plain text and has
no Teams connector.

Intended future flow:

```text
Teams architecture review with transcription enabled
→ approved connector or export
→ extraction and normalization
→ normalized review transcript
```

## Current implementation boundaries

- Synthetic data only.
- Fixture-backed `DeterministicDemoExtractor` behind the `GovernanceExtractor` interface.
- Reliable complete workflow for one frozen review scenario.
- No production enterprise LLM and no arbitrary-document analysis.
- No real Confluence, Teams, or Azure DevOps connection.
- No real ADO work-item creation.
- No database, authentication, RAG, agent framework, or production deployment.
- Not production ready.
- The application proposes and records; it does not replace or formally approve on behalf of the
  Domain Architect.

## Tone and format

Calm, precise, professional English. Use restrained blue and green accents, high contrast,
generous whitespace, concise callouts, clean cuts, and short fades. The real application is the
largest single segment. A provisional offline macOS TTS track may be used only for the review
draft and must be replaceable with approved human narration.

The opening and closing use the approved Standard Chartered lock-up for this internal video.
The technical frame shows a target deployment and integration architecture rather than a
business workflow. It places the AGC Front End in Service Bench and the AGC Backend API in SKE,
with adapters for Confluence, Teams, AIF LLM endpoints, a database, ADO, and enterprise controls.
The frame explicitly distinguishes this target state from the locally running deterministic PoC.

## Target duration

`03:42` total, with an absolute ceiling of `03:55`.

## Prohibited claims

Do not claim measured time, accuracy, quality, defect, or cost improvement; production
readiness; arbitrary-document support; automatic SI remediation or approval; live Confluence,
Teams, or ADO integration; real work-item creation; formal governance authority; or replacement
of the Domain Architect.
