# Large Task Governance Model

This document defines a generic model for governing large engineering tasks.
Use it when work is long-running, risky, cross-module, cross-repository,
stateful, migration-heavy, refactor-heavy, or dependent on staged closure.

## 1. Overall Positioning

The model treats a large-task skill as an entry router and governance layer, not
as a single oversized knowledge dump.

It splits complex work into two layers:

- Routing layer: decide which defined intent or task shape owns the request,
  then load only the smallest useful context.
- Execution layer: let the matching workflow handle domain-specific work such as
  migration, plugin debugging, integration validation, frontend updates, or
  memory maintenance.

The goal is to prevent large-task drift: avoid acting from stale memory, avoid
cross-domain edits without ownership, and avoid treating local build success as
full task completion.

## 2. Standard Landing Loop

Use this loop for long-running, risky, cross-module, cross-repository,
migration-heavy, refactor-heavy, integration-dependent, or staged-closure work:

```text
Audit current state
  -> Refresh plan
  -> Classify affected objects
  -> Implement in safe batches
  -> Verify gates
  -> Rescan residue
  -> Record progress and pitfalls
  -> Continue the next loop
until the explicit completion boundary is reached
```

The loop is designed to keep each step evidence-backed, bounded, recorded, and
recoverable.

## 3. Entry Routing

Before a large task starts, select exactly one primary route.

Routing constraints:

- Keep one machine-readable source of truth when the workspace has route definitions.
- Match exactly one primary route before acting.
- After matching, read only the route's first-read files unless the task proves more context is required.
- Read cross-reference material only when downstream or cross-intent effects are part of the task.
- If no defined intent matches, stop and ask whether to add a new intent.

## 4. Route Contract

Every large-task route should define:

- Use when: request shapes that belong to this route.
- Do not use when: nearby cases that should route elsewhere.
- First read: the minimum context to inspect before acting.
- Minimum evidence: required commands, files, diffs, logs, or user inputs.
- Output contract: what the final answer or artifact must contain.
- Stop conditions: when to pause and ask the user.
- Stale-reference handling: which source wins when references conflict.

## 5. Completion Boundaries

Do not use "code changed" or "build passed" as the whole definition of done.
Separate completion into layers:

- Partial progress: what has moved forward.
- Build-surface success: whether the immediate build or test surface passes.
- Source/workspace closure: whether source, generated files, configs, and residue are settled.
- Consumer closure: whether downstream callers, apps, plugins, services, or user workflows are verified or explicitly out of scope.
- Final completion: whether the user's explicit objective is fully achieved.

## 6. Classification First

Classify before editing. Classification should be task-specific rather than
directory-only.

Possible categories:

- Module, file, API, build surface, generated artifact, runtime descriptor, package, UI, test, or consumer.
- Schema/protocol, native export, frontend request shape, registration, packaging, or workflow surface.
- Visual-only, behavior-affecting, data-contract-affecting, destructive, or uncertain.
- Read-only, state-changing, or destructive.

## 7. Quality Gates

Select gates according to blast radius:

- Classification gate: object ownership and risk are known.
- Contract/API gate: public surfaces, generated artifacts, and callers have been inspected.
- Build/test gate: the narrowest meaningful validation has run.
- Residue scan gate: old symbols, paths, descriptors, wrappers, and references have been searched.
- Consumer gate: downstream integration has been verified or explicitly left open.

The final answer should state what changed, what was verified, what was not
verified, why checks were skipped, and whether any consumer-closure gap remains.

## 8. Records And Recovery

A large task should leave enough operational state to resume later:

- `PLAN.md`: current phase, roadmap, verification matrix, blockers.
- `LOG.md`: execution history, verification results, skipped checks.
- `PITFALLS.md`: failures, traps, repeatable fixes.
- `references/*.md`: longer topic material.

Write records where the project or user expects them. If permanent memory
writeback is blocked, include the recovery state in the final response.
