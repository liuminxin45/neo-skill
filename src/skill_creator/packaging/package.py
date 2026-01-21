from __future__ import annotations

from pathlib import Path

from ..util.fs import copytree, ensure_dir
from .ziputil import zip_dir


def package_claude_skill(repo_root: Path, skill_name: str, out_dir: Path) -> Path:
    """Create a .skill zip for Claude.

    Layout (zip root contains folder <skill_name>/):
      <skill_name>/SKILL.md
      <skill_name>/resources/*
    """
    claude_skill_dir = repo_root / ".claude" / "skills" / skill_name
    if not claude_skill_dir.exists():
        raise FileNotFoundError(f"Claude skill dir not found: {claude_skill_dir}")

    ensure_dir(out_dir)
    out_path = out_dir / f"{skill_name}.skill"
    zip_dir(claude_skill_dir, out_path, root_name=skill_name)
    return out_path


def package_repo_zip(repo_root: Path, out_path: Path) -> Path:
    """Zip the entire repo for distribution (IDE-friendly)."""
    repo_root = repo_root.resolve()
    zip_dir(repo_root, out_path, root_name=repo_root.name)
    return out_path
