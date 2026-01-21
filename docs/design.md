# Design (skill-creator)

## Goals
- Canonical SkillSpec drives generation of multiple AI-assistant formats.
- Strict validation for Claude SKILL.md metadata (frontmatter: name+description only).
- Progressive disclosure: keep SKILL.md concise; move details to `references/` and deterministic work to `scripts/`.
- Packaging: create Claude `.skill` zip where the zip root contains the skill folder.

## Repo layout
- `skills/<skill>/skillspec.json`: canonical spec (JSON, dependency-free)
- `.shared/skill-creator/`: shared data + scripts used by assistants
- `.claude/skills/<skill>/`: generated Claude skill (SKILL.md + resources/)
- `.windsurf/workflows/`: generated Windsurf workflows
- `.cursor/commands/`: generated Cursor commands
- `.github/skills/`: generated GitHub/VS Code skills
- `src/`: Python implementation
- `dist/`: build artifacts (.skill, .zip)

## Sources
- Agent Skills specification: https://agentskills.io/specification
- Anthropic skills repository: https://github.com/anthropics/skills
- UI UX Pro Max skill (multi-tool structure inspiration): https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
