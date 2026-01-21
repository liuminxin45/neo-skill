from __future__ import annotations

from pathlib import Path

from ..util.fs import ensure_dir, copytree, copyfile
from .model import SkillSpec
from ..targets.claude import render_claude_skill_md
from ..targets.windsurf import render_windsurf_workflow_md
from ..targets.cursor import render_cursor_command_md
from ..targets.github_skills import render_github_skill_md


def generate_all(repo_root: Path, spec_path: Path) -> SkillSpec:
    repo_root = repo_root.resolve()
    spec_path = spec_path.resolve()
    spec = SkillSpec.from_path(spec_path)

    # Canonical skill sources
    canonical_skill_dir = spec_path.parent
    refs_dir = canonical_skill_dir / "references"
    scripts_dir = canonical_skill_dir / "scripts"
    assets_dir = canonical_skill_dir / "assets"
    skill_readme = canonical_skill_dir / "readme.txt"

    # Claude
    claude_dir = repo_root / ".claude" / "skills" / spec.name
    ensure_dir(claude_dir)
    (claude_dir / "SKILL.md").write_text(render_claude_skill_md(spec), encoding='utf-8')
    if skill_readme.exists():
        copyfile(skill_readme, claude_dir / "readme.txt")
    claude_res = claude_dir / "resources"
    if skill_readme.exists():
        copyfile(skill_readme, claude_res / "readme.txt")
    copytree(refs_dir, claude_res / "references")
    copytree(scripts_dir, claude_res / "scripts")
    copytree(assets_dir, claude_res / "assets")

    # Windsurf workflow
    windsurf_path = repo_root / ".windsurf" / "workflows" / f"{spec.name}.md"
    ensure_dir(windsurf_path.parent)
    windsurf_path.write_text(render_windsurf_workflow_md(spec), encoding='utf-8')

    # Windsurf workflow data (optional)
    windsurf_data_src = assets_dir / "windsurf-workflow-data"
    windsurf_data_dst = repo_root / ".windsurf" / "workflows" / "data" / spec.name
    copytree(windsurf_data_src, windsurf_data_dst)

    # Cursor
    cursor_path = repo_root / ".cursor" / "commands" / f"{spec.name}.md"
    ensure_dir(cursor_path.parent)
    cursor_path.write_text(render_cursor_command_md(spec), encoding='utf-8')

    # GitHub / VS Code Skills
    gh_dir = repo_root / ".github" / "skills" / spec.name
    ensure_dir(gh_dir)
    (gh_dir / "SKILL.md").write_text(render_github_skill_md(spec), encoding='utf-8')
    if skill_readme.exists():
        copyfile(skill_readme, gh_dir / "readme.txt")
    copytree(refs_dir, gh_dir / "references")
    copytree(scripts_dir, gh_dir / "scripts")
    copytree(assets_dir, gh_dir / "assets")

    return spec
