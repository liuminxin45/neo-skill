from __future__ import annotations

from typing import Dict, Any


def dump_frontmatter(fields: Dict[str, Any]) -> str:
    """Dump a minimal YAML frontmatter block.

    Notes:
    - We intentionally keep this implementation small and dependency-free.
    - Values are rendered as single-line scalars (quoted when needed).
    """
    lines = ["---"]
    for k, v in fields.items():
        if v is None:
            continue
        s = str(v)
        # Quote if it contains colon, newline, or leading/trailing whitespace
        if any(ch in s for ch in [":", "\n"]) or s != s.strip():
            s = s.replace("\\", "\\\\").replace('"', '\\"')
            s = f"\"{s}\""
        lines.append(f"{k}: {s}")
    lines.append("---")
    return "\n".join(lines) + "\n"
