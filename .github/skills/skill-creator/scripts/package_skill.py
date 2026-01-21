"""skill-creator: deterministic packager.

Packages a Claude-ready .skill zip.

Usage:
  python3 skills/skill-creator/scripts/package_skill.py <skill-name>
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
    if len(sys.argv) != 2:
        print("Usage: python3 skills/skill-creator/scripts/package_skill.py <skill-name>")
        return 2
    _add_src_to_path()
    skill_name = sys.argv[1]
    cmd = [sys.executable, "-m", "skill_creator.cli", "package", "--target", "claude", "--skill", skill_name]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
