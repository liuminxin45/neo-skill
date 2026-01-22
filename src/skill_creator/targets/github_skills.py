from __future__ import annotations

from ..spec.model import SkillSpec
from ..util.frontmatter import dump_frontmatter
from .common import _render_steps, _render_resources, _render_footer


def render_github_skill_md(spec: SkillSpec) -> str:
    # GitHub/Agent Skills can support additional metadata; keep it conservative.
    fm = dump_frontmatter(
        {
            "name": spec.name,
            "description": spec.description,
            "compatibility": "Multi-assistant (Claude/Windsurf/Cursor/GitHub Skills)",
            "metadata": "Generated from canonical skillspec.json",
        }
    )

    body = []
    body.append("# " + spec.name)
    body.append("")
    body.append("## Overview")
    body.append(spec.description)
    body.append("")
    if spec.triggers:
        body.append("## Triggers")
        for t in spec.triggers:
            body.append(f"- {t}")
        body.append("")
    body.append("## Workflow")
    body.append(f"*Mode:* `{spec.workflow_type}`")
    body.append("")
    body.append(_render_steps(spec.steps))
    body.append("")
    body.append(_render_resources(spec))
    body.append("## Output contract")
    body.append("- Deterministic artifacts (files, zips, reports) whenever possible")
    body.append("- Machine-readable output available when scripts support `--json`")
    body.append(_render_footer())
    return fm + "\n".join(body)
