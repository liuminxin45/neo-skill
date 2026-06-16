---
name: neo-task-governance
description: >
  Govern large, risky, long-running engineering work with explicit routing,
  scope definition, classification, staged planning, verification gates,
  residue scans, progress records, and stop conditions.
---

# Large Task Governance

Use this skill to make large work controllable before making changes. The core
model is: route, scope, classify, plan, implement, verify, rescan, record, and
continue or stop.

For the full model document, read `references/large-task-model.md` when the user
asks for the model, asks to adapt it, or the task is long-running enough that a
complete governance checklist would prevent mistakes.

## Operating Rules

1. Route the request to one primary task shape before acting.
2. Define the completion boundary before implementation.
3. Load the smallest context that proves the route and scope.
4. Classify touched objects by role and risk before editing.
5. Refresh or create a master plan for multi-step work.
6. Use the largest safe batch that remains reviewable and verifiable.
7. Verify with the narrowest meaningful gates, then rescan for residue.
8. Record progress, skipped checks, blockers, and repeatable pitfalls.
9. Continue until the explicit completion boundary is reached, unless a stop
   condition requires user confirmation.

## Route And Scope

Choose exactly one primary route for the current task. If the project has its
own route registry, task plan, issue list, or memory files, use those as the
route source. If it does not, create an ad-hoc route for the current task in
working notes rather than inventing a permanent taxonomy.

For each route, establish:

- Use when: what request shape belongs here.
- Do not use when: nearby work that belongs elsewhere.
- First read: the minimum files, docs, logs, diffs, configs, or tests to inspect.
- Minimum evidence: what must be checked before output or edits.
- Output contract: what final response or artifact must include.
- Stop conditions: when to pause instead of guessing.
- Stale-reference handling: which source wins when evidence conflicts.

## Classification

Classify by behavior and contract, not just directory location. Pick categories
that match the domain, such as contract/API, implementation, packaging,
generated artifact, UI, test, config, runtime descriptor, migration residue, or
consumer surface.

Do not edit public contracts, delete legacy shells, or retire behavior until
consumers and replacement behavior are understood.

## Planning

For substantial work, keep a master plan that includes:

- Current phase and next milestone.
- Roadmap and batch boundaries.
- Inventory of affected files, modules, APIs, assets, or consumers.
- Retained capabilities and intentional removals.
- Public surfaces and compatibility concerns.
- Verification matrix.
- Blockers and stop-condition decisions.

## Verification Gates

Use gates appropriate to the blast radius:

- Classification gate: touched objects and risk categories are known.
- Contract/API gate: public surfaces, generated artifacts, and callers are checked.
- Build/test gate: the narrowest meaningful build, unit, integration, smoke, or visual check has run.
- Residue gate: old names, paths, wrappers, descriptors, or dead references are searched.
- Consumer gate: downstream app, plugin, service, or workflow impact is checked or explicitly left open.

In the final response, name verification that ran and checks skipped with
reasons. Never imply a consumer gate passed when it was not executed.

## Stop Conditions

Pause and ask the user before continuing when the task reaches:

- Public API or persistent data contract changes.
- Unknown consumers or cross-repository ownership conflicts.
- Product retirement, deletion, or compatibility removal decisions.
- Destructive cleanup or irreversible state changes.
- Hardware-affecting or shared-runtime operations.
- Ambiguous design input, product ownership, or API scope.
- Blocked memory/writeback rules where permanent notes would be misleading.

## Records

Prefer project-local or user-approved notes when the task spans turns. Keep
records concise and operational:

- `PLAN.md`: phase, roadmap, blockers, verification matrix.
- `LOG.md`: executed batches, results, skipped checks.
- `PITFALLS.md`: repeatable traps and fixes.
- Cross-reference notes: downstream or cross-intent effects.

If no persistent notes are appropriate, summarize the same information in the
final response so the next run can recover the state.
