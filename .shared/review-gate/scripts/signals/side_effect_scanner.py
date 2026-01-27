"""Scan for side effects in domain/application layers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class SideEffectViolation:
    """A side effect found in a pure layer."""
    file_path: str
    line_number: int
    line_content: str
    side_effect_type: str
    severity: str


class SideEffectScanner:
    """Scans for side effects in layers that should be pure."""
    
    SIDE_EFFECT_PATTERNS = {
        "network": [r"\bfetch\s*\(", r"\baxios\.", r"\.get\s*\(", r"\.post\s*\("],
        "fs": [r"\bfs\.", r"\.readFile", r"\.writeFile"],
        "time": [r"\bDate\.now\s*\(", r"\bnew\s+Date\s*\(", r"\bsetTimeout\s*\("],
        "random": [r"\bMath\.random\s*\("],
        "console": [r"\bconsole\.(log|warn|error|info|debug)\s*\("],
        "dom": [r"\bdocument\.", r"\bwindow\.", r"\blocalStorage\."],
    }
    
    PURE_LAYERS = ["domain", "application"]
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def scan(self, file_path: str, layer: str) -> List[SideEffectViolation]:
        """Scan a file for side effects."""
        if layer not in self.PURE_LAYERS:
            return []
        
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return []
        
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception:
            return []
        
        violations = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            for effect_type, patterns in self.SIDE_EFFECT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        severity = "HIGH" if effect_type in ["network", "fs"] else "MEDIUM"
                        violations.append(SideEffectViolation(
                            file_path=file_path,
                            line_number=i,
                            line_content=line.strip(),
                            side_effect_type=effect_type,
                            severity=severity,
                        ))
                        break
        
        return violations
