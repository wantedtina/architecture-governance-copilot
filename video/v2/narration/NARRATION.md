# Narration — V2 Human Voice

This script matches the human-voice revision. The user removed the closing feedback sentence from What we strengthened. All other approved script wording is retained.

## 00:00–00:10 — Architecture Governance Copilot

Hello, we're Two Tokens One Brain. Let me show you how Architecture Governance Copilot helps teams prepare and follow up on architecture reviews.

## 00:10–00:28 — The problem: fragmented governance work

Today, a project team writes its Solution Intent in Confluence, tracks the review in Azure Boards, and discusses the design in Teams.

Afterwards, someone has to bring the decisions, evidence and action owners back together. That's the work we're trying to make easier.

## 00:28–00:44 — Two activities, explicit human checkpoints

Our app helps with drafting and review, but Confluence remains the source of truth for the Solution Intent.

We only produce drafts and suggested changes. The app never edits Confluence. Users decide what to keep and make those changes themselves.

## 00:44–01:07 — System architecture

Both project teams and Domain Architects use the app, with different permissions and responsibilities.

The interface sits in Service Bench. SKE hosts the backend and database, with adapters for Confluence, AI Factory and Azure DevOps.

Teams transcripts are imported manually. Logs, traces and metrics go to COP.

## 01:07–01:31 — 1. Prepare and confirm an SI draft

Let's start with the project team. I open the project context, which brings together the template, repository revision and governance details.

I save the supporting evidence, confirm the package, and generate a Solution Intent draft.

I review and confirm that draft here. I would then make any changes I want in Confluence myself. The governance review is a separate step.

## 01:31–01:50 — 2. Select and confirm review inputs

For the review, I select the authoritative Solution Intent, import the meeting transcript, and load the review details.

I check and confirm these inputs before running the analysis. The app then puts together a proposal, with evidence for us to inspect.

## 01:50–02:21 — 3. Exercise human judgment

This is where I review what the app has proposed. The transcript says Riley will document the retry controls. I'm changing that action's owner to Taylor Kim.

Notice that Riley's original words stay visible, alongside my change.

I'm also leaving the retention finding out of this record. That doesn't mean the issue is resolved or approved.

The outcome is still Changes Requested. I confirm my reviewed record before generating the outputs.

## 02:21–02:42 — 4. Follow evidence into the outputs

The change summary shows what I edited and left out. Let's follow that retry action: here's Riley's original quote, then Taylor as the owner I confirmed, followed by the minutes and work-item preview.

We can check how the final action came from the original discussion, and see where I changed it.

## 02:42–03:05 — 5. Deliver through explicit controls

Next, I'll deliver the work item. I preview the request and check the owner, due date, parent reference and supporting evidence.

The summary and JSON show the same request. Once I'm happy with it, I confirm and create the work item.

The app reads it back to check the result. The receipt is visible here, and this action can't simply be submitted again.

## 03:05–03:22 — 6. Protect against stale outputs

Now let's see what happens if I change the transcript. I add some new context, and the previous outputs become invalid.

I need to run the analysis and review again before using new outputs. The work item I already delivered is still recorded.

## 03:22–03:29 — What we strengthened

We've made edits easier to see, evidence easier to follow, and delivery easier to check.

## 03:29–03:39 — Two Tokens One Brain

That's our demo. We want teams to spend less time piecing reviews together, while keeping people in control. Thank you for watching.
