# Skill System Design

How to design a complete skill system using the search tool and reasoning rules.

## Design System Generation

Use the search tool to generate a comprehensive skill system:

```bash
python3 .shared/skill-creator/scripts/search.py "<keywords>" --skill-system -p "<project_name>"
```

This command:
1. Searches all domains (workflow, output, resource, trigger, validation)
2. Applies reasoning rules from `skill-reasoning.csv`
3. Returns complete design: pattern, output, resources, rules

## Design Components

### 1. Workflow Pattern

Choose based on task complexity:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Sequential | Linear tasks, clear dependencies | collect → generate → validate |
| Conditional | Multiple paths, feature flags | if new: create else: update |
| Gated | Quality-critical, multi-phase | step → gate → step → gate |
| Parallel | Independent subtasks | [search_a, search_b] → merge |
| Iterative | Refinement, feedback loops | draft → review → revise |

### 2. Output Pattern

Match output to task type:

| Task Type | Output Pattern | Template Location |
|-----------|---------------|-------------------|
| Review/Audit | Checklist | `references/checklist-template.md` |
| Generation | Code + Tree | inline or `scripts/` |
| Analysis | Report | `references/report-template.md` |
| Fix/Debug | Patch/Diff | inline |
| Transform | Structured data | `assets/` |

### 3. Resource Strategy

Apply progressive disclosure:

| Content Type | Location | When |
|--------------|----------|------|
| Rules/Guidelines | `references/` | Static knowledge AI reads |
| Data/Templates | `assets/` | Structured, searchable data |
| Deterministic ops | `scripts/` | Reproducible execution |
| Cross-skill shared | `.shared/` | Reusable across skills |
| Step-local only | `notes` field | Truly unique to one step |

### 4. Reasoning Rules

Common reasoning patterns from `skill-reasoning.csv`:

| Condition | Recommendation | Rationale |
|-----------|---------------|-----------|
| Deterministic output | Use scripts/ | Reproducible results |
| Large context (>2000 tokens) | Progressive disclosure | Split into references/ |
| Reusable rules | Shared data | Move to .shared/ |
| Multi-step workflow | Sequential with gates | Validation between phases |
| User input required | Collect step first | Ensure requirements met |
| Error-prone step | Add gate | Clear error messages |

## Master + Overrides Pattern

For complex skills, use hierarchical configuration:

### Master (skillspec.json)
- Contains all default rules
- Single source of truth
- All steps reference it

### Overrides (references/<context>.md)
- Context-specific deviations
- Override master for specific pages/steps
- Document why deviation is needed

### Lookup Order
1. Check `references/<context>.md` for specific context
2. Fall back to `skillspec.json` defaults
3. Fall back to `.shared/` common patterns

## Example Design Session

**Input**: "code review skill for TypeScript projects"

```bash
python3 .shared/skill-creator/scripts/search.py "code review typescript audit" --skill-system -p "ts-review"
```

**Output**:
```
╔════════════════════════════════════════════════════════════════╗
║  SKILL SYSTEM: ts-review                                       ║
╠════════════════════════════════════════════════════════════════╣
║  WORKFLOW: Gated Workflow                                      ║
║    Checkpoints that must pass before proceeding                ║
║  OUTPUT: Checklist Pattern                                     ║
║    Actionable items with status                                ║
║  RESOURCES: Reference Documents                                ║
╠════════════════════════════════════════════════════════════════╣
║  APPLICABLE RULES:                                             ║
║    • review_task: checklist_output                             ║
║    • multi_step_workflow: sequential_with_gates                ║
║    • large_context: progressive_disclosure                     ║
╚════════════════════════════════════════════════════════════════╝
```
