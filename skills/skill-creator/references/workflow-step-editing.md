# Workflow Step Editing Protocol

Use this protocol when the task is to update an existing skill (not create a new one) by modifying `workflow.steps` in `skills/<skill>/skillspec.json`.

## Inputs (must collect)

- **Target**: which existing skill to update (`<skill>`)
- **Current spec**: contents of `skills/<skill>/skillspec.json`
- **New requirements**: the user's new needs (can be bullets, examples, constraints)
- **Constraints**: hard limits (tools allowed, compatibility, fail-fast gates, etc.)
- **Knowledge base structure**: what should live in `references/` (rules/specs/templates) vs `assets/` (data/templates) vs `scripts/` (deterministic execution)

## Output contract (must produce)

- **Change summary**
  - Added steps
  - Removed steps
  - Merged steps
  - Step edits (notes/commands/kind/title)
  - Rationale for each structural change
  - Knowledge base edits (references/assets/scripts)
- **Final `workflow.steps`** (as JSON array)
- **Notes on rerunning generation**

## Step mapping procedure

1. **Normalize requirements**
   - Rewrite the user's needs into atomic requirements (one intent per line).
   - Tag each as one of:
     - `action` (do something)
     - `gate` (must block on failure)
     - `branch` (conditional/decision)

2. **Extract current step intents**
   - For each existing step, summarize:
     - Primary intent
     - Inputs it needs
     - Outputs it produces
     - Whether it is `action` / `gate`

3. **Classify each atomic requirement**
   - Try to place it into exactly one existing step.
   - If it fits multiple steps, choose the one with the strongest ownership and add a short note explaining why.
   - If it fits none, mark as `needs_new_step`.

4. **Design new steps (only when needed)**
   - Create a new step if:
     - It introduces a new phase (new inputs, new outputs), or
     - It would overload an existing step's intent.
   - Step `id` rules:
     - kebab-case
     - stable, intent-based (avoid renaming unless necessary)
   - Step `notes` rules:
     - Prefer **index-style notes**: keep `workflow.steps[*].notes` short and point to canonical knowledge in `references/` or `assets/`.
     - Put detailed rule text, denylist/allowlist, and examples into `references/*.md` (or `assets/*` when it is structured data).
     - Only keep step-local details in `notes` when they are truly unique and cannot be shared.

5. **Delete or merge steps (allowed but strict)**
   - **Merge** only if two steps have overlapping intent and their separation no longer provides clarity or gating value.
   - **Delete** only if:
     - It is fully subsumed by other steps, and
     - It does not represent a required gate, and
     - You provide an explicit mapping showing where its responsibilities went.

## Safety checks (must pass)

- **No lost requirements**: every atomic requirement must be mapped to a final step.
- **Gate preservation**: if an existing step is a `gate`, do not delete it unless its check is preserved elsewhere.
- **Command contract**: any step that relies on deterministic scripts must keep commands copy-pastable.
- **Minimal disruption**: prefer editing `notes/commands` over renaming/reordering steps.
- **Knowledge-base first**: if a step becomes long or rule-heavy, move the details into `references/` or `assets/` and keep the step as an index.

## Final output template

### Change summary

- Added steps:
- Removed steps:
- Merged steps:
- Edited steps:
- Rationale:

### Final workflow.steps (JSON)

```json
[
  {
    "id": "<id>",
    "title": "<title>",
    "kind": "action",
    "commands": [],
    "notes": "<notes>"
  }
]
```

### Regeneration

Regenerate multi-assistant outputs after updating the spec:

```bash
omni-skill init --skill <skill>
```
