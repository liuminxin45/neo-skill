"""Persist manager for layered review-system files."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class PersistManager:
    """Manages persisting override rules to review-system."""
    
    def __init__(self, review_system_dir: Path):
        self.review_system_dir = review_system_dir
    
    def persist_path_override(self, path: str, overrides: dict) -> Path:
        """Persist path-specific overrides."""
        paths_dir = self.review_system_dir / "paths"
        paths_dir.mkdir(parents=True, exist_ok=True)
        
        filename = path.replace("/", "_").replace("\\", "_") + ".md"
        file_path = paths_dir / filename
        
        content = self._format_override_file(f"Path: {path}", overrides)
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def persist_package_override(self, package: str, overrides: dict) -> Path:
        """Persist package-specific overrides."""
        packages_dir = self.review_system_dir / "packages"
        packages_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = packages_dir / f"{package}.md"
        
        content = self._format_override_file(f"Package: {package}", overrides)
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def persist_stack_override(self, stack: str, overrides: dict) -> Path:
        """Persist stack-specific overrides."""
        stacks_dir = self.review_system_dir / "stacks"
        stacks_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = stacks_dir / f"{stack}.md"
        
        content = self._format_override_file(f"Stack: {stack}", overrides)
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def _format_override_file(self, title: str, overrides: dict) -> str:
        """Format override file content."""
        lines = [
            f"# Review Gate Overrides: {title}",
            "",
            "Override rules for specific checks in this scope.",
            "",
        ]
        
        for check_id, check_overrides in overrides.items():
            lines.extend([
                f"## {check_id}",
                "",
            ])
            
            for key, value in check_overrides.items():
                lines.append(f"**{key.capitalize()}**: {value}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def load_override(self, level: str, name: str) -> Optional[dict]:
        """Load existing override file."""
        if level == "path":
            file_path = self.review_system_dir / "paths" / f"{name.replace('/', '_')}.md"
        elif level == "package":
            file_path = self.review_system_dir / "packages" / f"{name}.md"
        elif level == "stack":
            file_path = self.review_system_dir / "stacks" / f"{name}.md"
        else:
            return None
        
        if not file_path.exists():
            return None
        
        return self._parse_override_file(file_path)
    
    def _parse_override_file(self, file_path: Path) -> dict:
        """Parse override file."""
        overrides = {}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            current_check = None
            
            for line in content.split("\n"):
                if line.startswith("## "):
                    current_check = line.strip("# ").strip()
                    overrides[current_check] = {}
                elif current_check and line.startswith("**") and "**:" in line:
                    match = line.split("**:")
                    if len(match) == 2:
                        key = match[0].strip("*").strip().lower()
                        value = match[1].strip()
                        overrides[current_check][key] = value
        except Exception:
            pass
        
        return overrides
