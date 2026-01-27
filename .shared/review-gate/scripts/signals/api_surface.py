"""Detect API surface and public exports changes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ExportInfo:
    """Information about an exported symbol."""
    name: str
    type: str  # function, class, const, type, interface
    is_default: bool
    file_path: str
    line_number: Optional[int] = None


@dataclass
class ApiSurface:
    """API surface of a module or package."""
    package_exports: Dict[str, List[str]]  # package.json exports
    index_exports: List[ExportInfo]  # index.ts exports
    deep_exports: List[ExportInfo]  # exports from deep files
    breaking_changes: List[str]


class ApiSurfaceAnalyzer:
    """Analyzes API surface and detects changes."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def analyze(self, changed_files: List[str]) -> ApiSurface:
        """Analyze API surface changes."""
        package_exports = self._analyze_package_json()
        index_exports = self._analyze_index_files(changed_files)
        deep_exports = self._analyze_deep_exports(changed_files)
        breaking_changes = self._detect_breaking_changes(changed_files)
        
        return ApiSurface(
            package_exports=package_exports,
            index_exports=index_exports,
            deep_exports=deep_exports,
            breaking_changes=breaking_changes,
        )
    
    def _analyze_package_json(self) -> Dict[str, List[str]]:
        """Analyze package.json exports field."""
        package_json = self.repo_path / "package.json"
        if not package_json.exists():
            return {}
        
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            exports = data.get("exports", {})
            
            if isinstance(exports, str):
                return {".": [exports]}
            elif isinstance(exports, dict):
                result = {}
                for key, value in exports.items():
                    if isinstance(value, str):
                        result[key] = [value]
                    elif isinstance(value, dict):
                        result[key] = list(value.values())
                return result
        except Exception:
            pass
        
        return {}
    
    def _analyze_index_files(self, changed_files: List[str]) -> List[ExportInfo]:
        """Analyze index.ts/index.js files."""
        exports = []
        
        for file_path in changed_files:
            if not file_path.endswith(("index.ts", "index.tsx", "index.js", "index.jsx")):
                continue
            
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue
            
            file_exports = self._extract_exports(full_path, file_path)
            exports.extend(file_exports)
        
        return exports
    
    def _analyze_deep_exports(self, changed_files: List[str]) -> List[ExportInfo]:
        """Analyze exports from non-index files."""
        exports = []
        
        for file_path in changed_files:
            if file_path.endswith(("index.ts", "index.tsx", "index.js", "index.jsx")):
                continue
            
            if not file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
                continue
            
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue
            
            file_exports = self._extract_exports(full_path, file_path)
            exports.extend(file_exports)
        
        return exports
    
    def _extract_exports(self, file_path: Path, rel_path: str) -> List[ExportInfo]:
        """Extract export statements from a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return []
        
        exports = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            # export default
            if re.match(r"^\s*export\s+default\s+", line):
                match = re.search(r"export\s+default\s+(function|class|const)?\s*(\w+)?", line)
                name = match.group(2) if match and match.group(2) else "default"
                export_type = match.group(1) if match and match.group(1) else "unknown"
                
                exports.append(ExportInfo(
                    name=name,
                    type=export_type,
                    is_default=True,
                    file_path=rel_path,
                    line_number=i,
                ))
            
            # export function/class/const
            match = re.match(r"^\s*export\s+(function|class|const|let|var|interface|type|enum)\s+(\w+)", line)
            if match:
                exports.append(ExportInfo(
                    name=match.group(2),
                    type=match.group(1),
                    is_default=False,
                    file_path=rel_path,
                    line_number=i,
                ))
            
            # export { ... }
            match = re.search(r"export\s*\{([^}]+)\}", line)
            if match:
                names = [n.strip().split(" as ")[0] for n in match.group(1).split(",")]
                for name in names:
                    if name:
                        exports.append(ExportInfo(
                            name=name.strip(),
                            type="unknown",
                            is_default=False,
                            file_path=rel_path,
                            line_number=i,
                        ))
        
        return exports
    
    def _detect_breaking_changes(self, changed_files: List[str]) -> List[str]:
        """Detect potential breaking changes."""
        breaking = []
        
        for file_path in changed_files:
            # Check if public API file
            if any(pattern in file_path for pattern in ["index.ts", "index.js", "/api/", "/public/"]):
                full_path = self.repo_path / file_path
                if not full_path.exists():
                    breaking.append(f"Public API file deleted: {file_path}")
                    continue
                
                # Check for removed exports (simplified - would need git diff)
                try:
                    content = full_path.read_text(encoding="utf-8")
                    if "// BREAKING:" in content or "// @deprecated" in content:
                        breaking.append(f"Breaking change marker in: {file_path}")
                except Exception:
                    pass
        
        return breaking
    
    def has_deep_index_files(self, changed_files: List[str]) -> List[str]:
        """Detect deep index.ts files that may cause coupling."""
        deep_indexes = []
        
        for file_path in changed_files:
            if file_path.endswith(("index.ts", "index.tsx", "index.js", "index.jsx")):
                depth = file_path.count("/")
                if depth > 2:  # More than src/module/index.ts
                    deep_indexes.append(file_path)
        
        return deep_indexes
    
    def detect_default_export_overuse(self, exports: List[ExportInfo]) -> List[ExportInfo]:
        """Detect files with default exports (should prefer named)."""
        return [e for e in exports if e.is_default and "page" not in e.file_path.lower()]
