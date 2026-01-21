"""skill-creator: deterministic validator.

Validates:
- SkillSpec schema (kebab-case name, <=10 questions, workflow exists)
- Generated Claude SKILL.md strict frontmatter (only name/description)
- Banned files inside skill bundles (README/CHANGELOG/etc)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    # Usage:
    #   python3 skills/skill-creator/scripts/validate_skill.py skills/<skill>/skillspec.json
    if len(sys.argv) != 2:
        print("Usage: python3 skills/skill-creator/scripts/validate_skill.py skills/<skill>/skillspec.json")
        return 2
    _add_src_to_path()
    cmd = [sys.executable, "-m", "skill_creator.cli", "validate", sys.argv[1]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
