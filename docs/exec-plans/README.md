# Bounded execution plans

Document status: `PROCESS_CONVENTION`

This directory stores one living execution plan per explicitly approved implementation batch. This
README defines structure and recovery rules only; it never authorizes work and never identifies the
active batch. The active-plan pointer exists only in
`docs/POST_BASELINE_REFINEMENT_PLAN.md` to avoid two documents claiming the same scope.

## Creation gate and naming

Create an execution plan only after the user approves a coherent group of `Accepted` or `Ready`
refinement items for implementation. Use a stable name such as:

```text
POST_BASELINE_REFINEMENT_BATCH_01.md
```

Do not create speculative plans for merely `Collected` items. Do not run two active plans that
define overlapping implementation scope.

## Required structure

Every execution plan must include:

1. document status, included refinement IDs, approval boundary, and baseline revision;
2. scope and explicit non-goals;
3. dependencies and unresolved blockers;
4. affected components and files;
5. implementation steps;
6. acceptance criteria;
7. required automated tests and browser verification;
8. state invalidation, compatibility, and migration implications where relevant;
9. a continuously updated progress checklist;
10. decisions and important discoveries;
11. actual verification evidence;
12. remaining limitations and deferred work; and
13. a final completion record.

Use English in execution plans and all repository deliverables. Record commands and results
accurately; planned verification is not verification evidence.

## Living-plan rules

- Update the plan as implementation progresses so a new session can recover without relying on
  conversation history.
- Keep requirement intent in the refinement register and implementation detail in the execution
  plan. Link by refinement ID instead of duplicating the full requirement.
- Reflect material discoveries and approved scope decisions in both places only at their proper
  level: lifecycle/intent in the register, execution consequences in the active plan.
- Update progress only after inspecting the Git working tree and actual results.
- When verification succeeds, mark the execution plan `COMPLETED_VERIFIED`, update the linked
  refinement items to `Verified`, clear the active-plan pointer, and retain the plan for historical
  evidence. Do not delete it.
- When work stops without verification, record the exact blocker or remaining work. Do not mark the
  plan complete merely because a session ends.

## Recovery protocol

A fresh Codex session working on an approved batch should read, in order:

1. current explicit user direction and `AGENTS.md`;
2. `docs/POST_BASELINE_REFINEMENT_PLAN.md` to identify accepted intent and the sole active-plan
   pointer;
3. the referenced active execution plan, if any;
4. Git status, recent history, current code, tests, and relevant maintained product documentation;
5. completed plans and baseline evidence only when historical rationale or comparison is needed.

If the register names no active execution plan, no post-baseline implementation batch is active.
