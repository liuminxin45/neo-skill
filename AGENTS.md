# Repository Instructions

This repository publishes a small public Codex skill pack.

## Scope

- Keep public skills under `skills/neo-*`.
- Maintain only the three public skills unless the user explicitly asks to add another:
  - `neo-task-governance`
  - `neo-cpp-refactor`
  - `neo-mail-assistant`
- Do not add private project memory, raw mailbox exports, local runtime output, or generated reports to the public skill surface.

## Skill Rules

- `SKILL.md` frontmatter must contain only `name` and `description`.
- The frontmatter `name` must match the folder name.
- Use `references/` for optional detailed guidance and keep the main `SKILL.md` concise.
- Use `scripts/` only for reusable deterministic helpers.
- Keep `agents/openai.yaml` aligned with the skill name and default trigger prompt.

## Validation

Run this before publishing:

```powershell
.\tools\validate-skills.ps1
```
