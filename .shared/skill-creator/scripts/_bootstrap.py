from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    # .../.shared/skill-creator/scripts/_bootstrap.py -> repo root is 4 levels up
    return Path(__file__).resolve().parents[3]


def add_src_to_path() -> None:
    rr = repo_root()
    src = rr / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
