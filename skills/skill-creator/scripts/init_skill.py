"""skill-creator: deterministic initializer.

Thin wrapper around the repository CLI (keeps skill bundles small).
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
    #   python3 skills/skill-creator/scripts/init_skill.py <skill-name> [--description "..."]
    if len(sys.argv) < 2:
        print('Usage: python3 skills/skill-creator/scripts/init_skill.py <skill-name> [--description "..."]')
        return 2
    _add_src_to_path()
    name = sys.argv[1]
    extra = sys.argv[2:]
    cmd = [sys.executable, "-m", "skill_creator.cli", "init", name] + extra
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
