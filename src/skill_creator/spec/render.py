from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from ..util.fs import ensure_dir, copytree, copyfile
from .model import SkillSpec
from ..targets.claude import render_claude_skill_md
from ..targets.windsurf import render_windsurf_workflow_md
from ..targets.cursor import render_cursor_command_md
from ..targets.github_skills import render_github_skill_md

# Primary target is Windsurf; others are backward compat
PRIMARY_TARGET = "windsurf"
BACKWARD_COMPAT_TARGETS = ["claude", "cursor", "github"]
ALL_TARGETS = [PRIMARY_TARGET] + BACKWARD_COMPAT_TARGETS


def generate_target(repo_root: Path, spec: SkillSpec, spec_dir: Path, target: str) -> Path:
    """Generate output for a specific target. Returns output path."""
    refs_dir = spec_dir / "references"
    scripts_dir = spec_dir / "scripts"
    assets_dir = spec_dir / "assets"
    skill_readme = spec_dir / "readme.txt"

    if target == "windsurf":
        # PRIMARY: Windsurf workflow
        out_path = repo_root / ".windsurf" / "workflows" / f"{spec.name}.md"
        ensure_dir(out_path.parent)
        out_path.write_text(render_windsurf_workflow_md(spec), encoding="utf-8")
        
        # Windsurf workflow data (optional)
        windsurf_data_src = assets_dir / "windsurf-workflow-data"
        if windsurf_data_src.exists():
            windsurf_data_dst = repo_root / ".windsurf" / "workflows" / "data" / spec.name
            copytree(windsurf_data_src, windsurf_data_dst)
        return out_path

    elif target == "claude":
        # BACKWARD COMPAT: Claude SKILL.md
        claude_dir = repo_root / ".claude" / "skills" / spec.name
        ensure_dir(claude_dir)
        out_path = claude_dir / "SKILL.md"
        out_path.write_text(render_claude_skill_md(spec), encoding="utf-8")
        if skill_readme.exists():
            copyfile(skill_readme, claude_dir / "readme.txt")
        claude_res = claude_dir / "resources"
        copytree(refs_dir, claude_res / "references")
        copytree(scripts_dir, claude_res / "scripts")
        copytree(assets_dir, claude_res / "assets")
        return out_path

    elif target == "cursor":
        # BACKWARD COMPAT: Cursor command
        out_path = repo_root / ".cursor" / "commands" / f"{spec.name}.md"
        ensure_dir(out_path.parent)
        out_path.write_text(render_cursor_command_md(spec), encoding="utf-8")
        return out_path

    elif target == "github":
        # BACKWARD COMPAT: GitHub Skills
        gh_dir = repo_root / ".github" / "skills" / spec.name
        ensure_dir(gh_dir)
        out_path = gh_dir / "SKILL.md"
        out_path.write_text(render_github_skill_md(spec), encoding="utf-8")
        if skill_readme.exists():
            copyfile(skill_readme, gh_dir / "readme.txt")
        copytree(refs_dir, gh_dir / "references")
        copytree(scripts_dir, gh_dir / "scripts")
        copytree(assets_dir, gh_dir / "assets")
        return out_path

    else:
        raise ValueError(f"Unknown target: {target}")


def generate_windsurf(repo_root: Path, spec_path: Path) -> SkillSpec:
    """Generate Windsurf output only (primary target)."""
    spec = SkillSpec.from_path(spec_path)
    spec_dir = spec_path.parent
    generate_target(repo_root, spec, spec_dir, "windsurf")
    return spec


def generate_all(repo_root: Path, spec_path: Path, targets: Optional[List[str]] = None) -> SkillSpec:
    """
    Generate outputs for specified targets.
    
    Args:
        repo_root: Repository root path
        spec_path: Path to skillspec.json
        targets: List of targets to generate. Default: all targets.
    
    Returns:
        Loaded SkillSpec
    """
    repo_root = repo_root.resolve()
    spec_path = spec_path.resolve()
    spec = SkillSpec.from_path(spec_path)
    spec_dir = spec_path.parent

    if targets is None:
        targets = ALL_TARGETS

    for target in targets:
        generate_target(repo_root, spec, spec_dir, target)

    return spec
