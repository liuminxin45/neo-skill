from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, obj: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')


def copytree(src: Path, dst: Path, *, overwrite: bool = True) -> None:
    if not src.exists():
        return
    if dst.exists() and overwrite:
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copyfile(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
