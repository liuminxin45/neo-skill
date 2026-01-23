#!/usr/bin/env python3
"""
Skill Packager - Package skills for distribution

Usage:
    python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>
    python3 .shared/skill-creator/scripts/package.py --target repo
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def package_claude_skill(skill_name: str, repo_root: Path, out_dir: Path) -> Path:
    """
    Package a Claude skill as .skill zip file.
    
    Claude .skill format:
    - Zip root must be the skill folder
    - Must contain SKILL.md with strict frontmatter
    - Resources in resources/ subfolder
    """
    skill_dir = repo_root / ".claude" / "skills" / skill_name
    
    if not skill_dir.exists():
        print(f"ERROR: Claude skill not found: {skill_dir}", file=sys.stderr)
        print("Run generate.py first to create Claude output", file=sys.stderr)
        sys.exit(1)
    
    # Validate before packaging
    validate_script = SCRIPT_DIR / "validate.py"
    spec_path = repo_root / "skills" / skill_name / "skillspec.json"
    
    if validate_script.exists() and spec_path.exists():
        result = subprocess.run(
            [sys.executable, str(validate_script), str(spec_path)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Validation failed:", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
    
    ensure_dir(out_dir)
    out_path = out_dir / f"{skill_name}.skill"
    
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in skill_dir.rglob("*"):
            if path.is_file():
                arcname = path.relative_to(skill_dir.parent)
                zf.write(path, arcname)
    
    return out_path


def package_repo_zip(repo_root: Path, out_dir: Path) -> Path:
    """Package entire repo as zip for easy sharing."""
    ensure_dir(out_dir)
    out_path = out_dir / f"{repo_root.name}.zip"
    
    # Use git archive if available
    try:
        result = subprocess.run(
            ["git", "archive", "--format=zip", "--output", str(out_path), "HEAD"],
            cwd=repo_root,
            capture_output=True
        )
        if result.returncode == 0:
            return out_path
    except FileNotFoundError:
        pass
    
    # Fallback: manual zip (respecting gitignore patterns)
    gitignore = repo_root / ".gitignore"
    ignore_patterns = set()
    if gitignore.exists():
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ignore_patterns.add(line.strip("/"))
    
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in repo_root.rglob("*"):
            if path.is_file():
                rel = path.relative_to(repo_root)
                
                # Skip common ignored patterns
                skip = False
                for part in rel.parts:
                    if part in ignore_patterns or part.startswith("."):
                        skip = True
                        break
                
                if not skip:
                    zf.write(path, rel)
    
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Package skills for distribution")
    parser.add_argument("--target", "-t", choices=["claude", "repo"], required=True,
                        help="Package target")
    parser.add_argument("--skill", "-s", help="Skill name (required for --target claude)")
    parser.add_argument("--repo-root", "-r", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--out-dir", "-o", help="Output directory (default: dist/)")
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir) if args.out_dir else repo_root / "dist"
    
    if args.target == "claude":
        if not args.skill:
            print("ERROR: --skill required for --target claude", file=sys.stderr)
            sys.exit(1)
        out_path = package_claude_skill(args.skill, repo_root, out_dir)
    else:
        out_path = package_repo_zip(repo_root, out_dir)
    
    print(f"Packaged: {out_path}")


if __name__ == "__main__":
    main()
