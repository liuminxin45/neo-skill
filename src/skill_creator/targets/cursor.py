from __future__ import annotations

from ..spec.model import SkillSpec
from .common import _render_prerequisites


def render_cursor_command_md(spec: SkillSpec) -> str:
    # Cursor's command palette prompts are typically Markdown instructions.
    lines = [f"# {spec.name}", "", spec.description, ""]
    
    # Prerequisites (三方库信息)
    prerequisites = _render_prerequisites(spec, include_python_check=False)
    if prerequisites:
        lines.append(prerequisites)
    
    if spec.triggers:
        lines.append("## When to use")
        lines.extend([f"- {t}" for t in spec.triggers])
        lines.append("")
    lines.append("## Command")
    lines.append("Run these deterministic steps in the repository:")
    lines.append("```bash")
    if spec.name == "skill-creator":
        lines.append("python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json")
        lines.append("python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json")
        lines.append("python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>")
    else:
        lines.append("omni-skill init --cursor")
        lines.append("omni-skill do --agent")
    lines.append("```")
    lines.append("")
    lines.append("## Workflow")
    lines.append(f"Mode: `{spec.workflow_type}`")
    lines.append("")
    for i, step in enumerate(spec.steps, start=1):
        lines.append(f"### {i}. {step.title}")
        if step.commands:
            lines.append("```bash")
            lines.extend(step.commands)
            lines.append("```")
    return "\n".join(lines)
