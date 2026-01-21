# ai-skill-creator (multi-assistant)

A deterministic **skill-creator** repository.

## What it does
- Uses a canonical `skills/<skill>/skillspec.json` (single source of truth)
- Generates wrappers for multiple assistants:
  - Claude: `.claude/skills/<skill>/SKILL.md` + `resources/`
  - Windsurf: `.windsurf/workflows/<skill>.md`
  - Cursor: `.cursor/commands/<skill>.md`
  - GitHub / VS Code Skills: `.github/skills/<skill>/SKILL.md` + resources
- Validates strict Claude metadata rules for generated `SKILL.md`
- Packages a Claude `.skill` (zip) with the correct root-folder layout

## Quickstart

### Recommended (short commands)
> If `omni-skill` is available as a CLI.

```bash
omni-skill init --cursor
omni-skill do --agent
```

### No-install fallback
```bash
python -m omni_skill.cli init --cursor
python -m omni_skill.cli do --agent
```

### Direct (skill-creator)
```bash
# From repo root
python -m skill_creator.cli generate skills/skill-creator/skillspec.json
python -m skill_creator.cli validate skills/skill-creator/skillspec.json
python -m skill_creator.cli package --target claude --skill skill-creator
```

Or use the convenience scripts:

```bash
python .shared/skill-creator/scripts/generate.py skills/skill-creator/skillspec.json
python .shared/skill-creator/scripts/validate.py skills/skill-creator/skillspec.json
python .shared/skill-creator/scripts/package.py --target claude --skill skill-creator
```

## Canonical vs generated files

### Canonical (edit these)
- `skills/<skill>/skillspec.json`
- `skills/<skill>/references/**`
- `skills/<skill>/scripts/**` (optional)
- `skills/<skill>/assets/**` (optional)

### Generated (do not hand-edit)
- `.windsurf/workflows/<skill>.md`
- `.windsurf/workflows/data/<skill>/**` (synced from `skills/<skill>/assets/windsurf-workflow-data`)
- `.claude/skills/<skill>/**`
- `.cursor/commands/<skill>.md`
- `.github/skills/<skill>/**`
