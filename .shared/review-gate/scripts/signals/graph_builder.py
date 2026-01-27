"""Build impacted dependency subgraph for TypeScript projects."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class DependencyNode:
    """Represents a module in the dependency graph."""
    path: str
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    layer: Optional[str] = None
    is_changed: bool = False


@dataclass
class DependencyGraph:
    """Dependency graph for the codebase."""
    nodes: Dict[str, DependencyNode]
    cycles: List[List[str]]
    impacted_nodes: Set[str]


class GraphBuilder:
    """Builds dependency graph from TypeScript/JavaScript imports."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.src_path = repo_path / "src"
    
    def build_impacted_subgraph(self, changed_files: List[str]) -> DependencyGraph:
        """Build subgraph of modules impacted by changed files."""
        all_nodes = self._scan_all_modules()
        
        # Mark changed files
        for file_path in changed_files:
            normalized = self._normalize_path(file_path)
            if normalized in all_nodes:
                all_nodes[normalized].is_changed = True
        
        # Find impacted nodes (transitive closure)
        impacted = self._find_impacted_nodes(all_nodes, changed_files)
        
        # Detect cycles
        cycles = self._detect_cycles(all_nodes)
        
        return DependencyGraph(
            nodes=all_nodes,
            cycles=cycles,
            impacted_nodes=impacted,
        )
    
    def _scan_all_modules(self) -> Dict[str, DependencyNode]:
        """Scan all TypeScript/JavaScript modules."""
        nodes = {}
        
        if not self.src_path.exists():
            return nodes
        
        for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            for file_path in self.src_path.rglob(ext):
                if "node_modules" in file_path.parts or ".test." in file_path.name:
                    continue
                
                normalized = self._normalize_path(str(file_path.relative_to(self.repo_path)))
                imports = self._extract_imports(file_path)
                
                node = DependencyNode(path=normalized, imports=imports)
                nodes[normalized] = node
        
        # Build reverse edges
        for node in nodes.values():
            for imp in node.imports:
                if imp in nodes:
                    nodes[imp].imported_by.append(node.path)
        
        return nodes
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return []
        
        imports = []
        
        # Match ES6 imports: import ... from "..."
        for match in re.finditer(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content):
            import_path = match.group(1)
            resolved = self._resolve_import(file_path, import_path)
            if resolved:
                imports.append(resolved)
        
        # Match require: require("...")
        for match in re.finditer(r'require\(["\']([^"\']+)["\']\)', content):
            import_path = match.group(1)
            resolved = self._resolve_import(file_path, import_path)
            if resolved:
                imports.append(resolved)
        
        return imports
    
    def _resolve_import(self, from_file: Path, import_path: str) -> Optional[str]:
        """Resolve import path to actual file."""
        # Skip external packages
        if not import_path.startswith(".") and not import_path.startswith("@/"):
            return None
        
        # Handle path aliases (@/)
        if import_path.startswith("@/"):
            import_path = import_path[2:]
            base = self.src_path
        else:
            base = from_file.parent
        
        # Try different extensions
        for ext in ["", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js", "/index.jsx"]:
            candidate = (base / import_path).with_suffix("") if not ext.startswith("/") else base / import_path
            if ext.startswith("/"):
                candidate = base / import_path / ext[1:]
            else:
                candidate = candidate.with_suffix(ext)
            
            if candidate.exists():
                try:
                    rel_path = candidate.relative_to(self.repo_path)
                    return self._normalize_path(str(rel_path))
                except ValueError:
                    continue
        
        return None
    
    def _normalize_path(self, path: str) -> str:
        """Normalize file path."""
        return path.replace("\\", "/")
    
    def _find_impacted_nodes(self, nodes: Dict[str, DependencyNode], changed_files: List[str]) -> Set[str]:
        """Find all nodes impacted by changed files (BFS)."""
        impacted = set()
        queue = []
        
        for file_path in changed_files:
            normalized = self._normalize_path(file_path)
            if normalized in nodes:
                queue.append(normalized)
                impacted.add(normalized)
        
        while queue:
            current = queue.pop(0)
            node = nodes.get(current)
            if not node:
                continue
            
            for dependent in node.imported_by:
                if dependent not in impacted:
                    impacted.add(dependent)
                    queue.append(dependent)
        
        return impacted
    
    def _detect_cycles(self, nodes: Dict[str, DependencyNode]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = []
        
        def dfs(node_path: str) -> bool:
            if node_path in rec_stack:
                cycle_start = rec_stack.index(node_path)
                cycles.append(rec_stack[cycle_start:] + [node_path])
                return True
            
            if node_path in visited:
                return False
            
            visited.add(node_path)
            rec_stack.append(node_path)
            
            node = nodes.get(node_path)
            if node:
                for imp in node.imports:
                    if imp in nodes:
                        dfs(imp)
            
            rec_stack.pop()
            return False
        
        for node_path in nodes:
            if node_path not in visited:
                dfs(node_path)
        
        return cycles
