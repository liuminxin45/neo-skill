from __future__ import annotations

from ..spec.model import SkillSpec


def render_windsurf_workflow_md(spec: SkillSpec) -> str:
    # Windsurf workflows often use a small YAML header; keep it minimal.
    header = "---\n" + f"description: {spec.description}\n" + "auto_execution_mode: 3\n---\n"
    lines = [header, f"# {spec.name}", ""]

    is_skill_creator = spec.name == "skill-creator"
    if is_skill_creator:
        lines.append("Role: skill generator.")
        lines.append("")
        lines.append("Non-negotiable:")
        lines.append("- Follow the canonical SkillSpec at skills/<skill>/skillspec.json")
        lines.append("- Generate Claude/Windsurf/Cursor/GitHub Skills outputs")
        lines.append("- Run validation before packaging")
        lines.append("")
    else:
        lines.append("Role: workflow executor.")
        lines.append("")

    if spec.triggers:
        lines.append("## Triggers")
        for t in spec.triggers:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("## Workflow")
    lines.append(f"Mode: `{spec.workflow_type}`")
    lines.append("")
    for i, step in enumerate(spec.steps, start=1):
        lines.append(f"### Step {i} — {step.title}")
        if step.notes:
            notes = step.notes
            notes = notes.replace("`references/", f"`skills/{spec.name}/references/")
            lines.append(notes)
        if step.commands:
            lines.append("```bash")
            lines.extend(step.commands)
            lines.append("```")
        lines.append("")

    if is_skill_creator:
        lines.append("## Deterministic tools")
        lines.append("```bash")
        lines.append("# Generate outputs for all targets")
        lines.append("python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json")
        lines.append("# Validate outputs")
        lines.append("python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json")
        lines.append("# Package Claude .skill")
        lines.append("python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>")
        lines.append("```")

    return "\n".join(lines)
