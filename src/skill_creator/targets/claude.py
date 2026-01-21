from __future__ import annotations

from ..spec.model import SkillSpec
from ..util.frontmatter import dump_frontmatter
from .common import _render_steps, _render_resources, _render_footer


def render_claude_skill_md(spec: SkillSpec) -> str:
    # Strict metadata: only name + description.
    fm = dump_frontmatter({"name": spec.name, "description": spec.description})

    body = []
    body.append("# " + spec.name)
    body.append("")
    body.append("## What this skill does")
    body.append(spec.description)
    body.append("")

    if spec.triggers:
        body.append("## When to use (examples of user requests)")
        for t in spec.triggers:
            body.append(f"- {t}")
        body.append("")

    body.append("## Degrees of freedom")
    body.append(
        f"This skill is designed for **{spec.freedom_level}** freedom (high=heuristic, low=deterministic scripts)."
    )
    body.append("")

    if spec.questions:
        body.append("## Requirement collection (at most 10 questions)")
        body.append("Ask only what is missing. Never exceed 10 questions total.")
        for i, q in enumerate(spec.questions, start=1):
            body.append(f"{i}. {q}")
        body.append("")

    body.append("## Workflow")
    body.append(f"*Mode:* `{spec.workflow_type}`")
    body.append("")
    body.append(_render_steps(spec.steps))
    body.append("")

    body.append(_render_resources(spec))
    body.append("## Output contract")
    body.append("When invoked, produce:")
    body.append("A) A proposed directory tree")
    body.append("B) SKILL.md / workflow entry file(s)")
    body.append("C) Any scripts/references/assets")
    body.append("D) A validation checklist with pass/fail")

    body.append(_render_footer())
    return fm + "\n".join(body)
