# Pre-Delivery Checklist

Verify these items before delivering a skill.

## Spec Quality

- [ ] **name** is kebab-case (lowercase, hyphens only)
- [ ] **description** clearly states when to use (>20 chars)
- [ ] **questions** are ≤10 and prioritized
- [ ] **triggers** include ≥5 example phrases
- [ ] **freedom_level** matches task type (low=deterministic, high=heuristic)

## Workflow Quality

- [ ] All steps have unique `id` (kebab-case)
- [ ] All steps have descriptive `title`
- [ ] Gate steps (`kind: gate`) have clear pass/fail criteria
- [ ] Step `notes` are concise (<200 chars) and use index-style references
- [ ] Commands are copy-pastable and use `<placeholders>` consistently

## Resource Organization

- [ ] `references/` contains only static rules/guidelines
- [ ] `scripts/` contains only deterministic, executable code
- [ ] `assets/` contains only structured data (CSV/JSON)
- [ ] No duplicate content across resources
- [ ] `.shared/` used for cross-skill reusable content

## Generated Outputs

Run validation:
```bash
python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
```

- [ ] Windsurf workflow generated at `.windsurf/workflows/<name>.md`
- [ ] Claude SKILL.md has strict frontmatter (name + description only)
- [ ] No banned files in skill bundles (README.md, CHANGELOG.md, etc.)
- [ ] Resources copied correctly for Claude/GitHub targets

## Trigger Coverage

- [ ] Covers main action verb ("create", "review", "fix", etc.)
- [ ] Covers Chinese equivalents if applicable
- [ ] Covers common variations/synonyms
- [ ] Covers context keywords (technology, domain)
- [ ] Test: would a new user's phrasing match at least one trigger?

## Common Issues to Avoid

| Issue | Check |
|-------|-------|
| Notes too long | Move details to `references/` |
| Hardcoded paths | Use `<placeholders>` |
| Missing gates | Add validation after risky steps |
| Unclear output | Specify exact format in step notes |
| Duplicate triggers | Consolidate similar phrases |

## Final Sign-off

```markdown
## Delivery Confirmation

- Skill: <name>
- Version: 1
- Primary target: windsurf
- Backward compat: claude, cursor, github
- Validation: ✓ passed
- Package: dist/<name>.skill (if Claude target)
```
