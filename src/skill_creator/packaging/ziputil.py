from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Optional


def zip_dir(src_dir: Path, out_path: Path, *, root_name: Optional[str] = None) -> None:
    """Zip a directory.

    If root_name is provided, the zip will contain entries under that root folder,
    regardless of the actual directory name.
    """
    src_dir = src_dir.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in src_dir.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(src_dir)
            if root_name:
                arcname = Path(root_name) / rel
            else:
                arcname = rel
            zf.write(p, arcname.as_posix())
