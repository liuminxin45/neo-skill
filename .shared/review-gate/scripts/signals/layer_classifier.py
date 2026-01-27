"""Classify files into architectural layers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LayerInfo:
    """Information about a file's layer."""
    layer: str
    confidence: str  # HIGH, MEDIUM, LOW
    reason: str


class LayerClassifier:
    """Classifies files into architectural layers."""
    
    LAYERS = [
        "presentation",
        "application",
        "domain",
        "infra",
        "shared",
        "types",
        "tests",
    ]
    
    LAYER_PATTERNS = {
        "presentation": [
            "presentation/",
            "components/",
            "pages/",
            "views/",
            "ui/",
            "hooks/use",
        ],
        "application": [
            "application/",
            "services/",
            "use-cases/",
            "usecases/",
            "orchestration/",
        ],
        "domain": [
            "domain/",
            "models/",
            "entities/",
            "business/",
        ],
        "infra": [
            "infra/",
            "infrastructure/",
            "adapters/",
            "repositories/",
            "api/client",
            "api/fetch",
        ],
        "shared": [
            "shared/",
            "utils/",
            "helpers/",
            "common/",
            "lib/",
        ],
        "types": [
            "types/",
            ".d.ts",
            "interfaces/",
        ],
        "tests": [
            "tests/",
            "test/",
            "__tests__/",
            ".test.",
            ".spec.",
        ],
    }
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def classify(self, file_path: str) -> LayerInfo:
        """Classify a file into a layer."""
        normalized = file_path.replace("\\", "/").lower()
        
        # Check explicit layer patterns
        for layer, patterns in self.LAYER_PATTERNS.items():
            for pattern in patterns:
                if pattern in normalized:
                    return LayerInfo(
                        layer=layer,
                        confidence="HIGH",
                        reason=f"Path contains '{pattern}'",
                    )
        
        # Heuristic: check file content for clues
        content_layer = self._classify_by_content(file_path)
        if content_layer:
            return content_layer
        
        # Default to shared if uncertain
        return LayerInfo(
            layer="shared",
            confidence="LOW",
            reason="No clear layer indicators",
        )
    
    def classify_batch(self, file_paths: List[str]) -> Dict[str, LayerInfo]:
        """Classify multiple files."""
        return {path: self.classify(path) for path in file_paths}
    
    def _classify_by_content(self, file_path: str) -> Optional[LayerInfo]:
        """Classify by analyzing file content."""
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return None
        
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception:
            return None
        
        # React component indicators
        if any(pattern in content for pattern in ["export default function", "export const", "React.FC", "JSX.Element"]):
            if "useState" in content or "useEffect" in content or "onClick" in content:
                return LayerInfo(
                    layer="presentation",
                    confidence="MEDIUM",
                    reason="Contains React component patterns",
                )
        
        # Domain model indicators
        if any(pattern in content for pattern in ["class ", "interface ", "type "]):
            if not any(pattern in content for pattern in ["fetch(", "axios", "useState", "useEffect"]):
                return LayerInfo(
                    layer="domain",
                    confidence="MEDIUM",
                    reason="Contains type definitions without side effects",
                )
        
        # Infrastructure indicators
        if any(pattern in content for pattern in ["fetch(", "axios", "prisma", "db.", "api."]):
            return LayerInfo(
                layer="infra",
                confidence="MEDIUM",
                reason="Contains external I/O operations",
            )
        
        return None
    
    def get_layer_hierarchy(self) -> Dict[str, int]:
        """Get layer hierarchy (lower number = lower in stack)."""
        return {
            "domain": 1,
            "application": 2,
            "presentation": 3,
            "infra": 1,  # Same level as domain (dependency inversion)
            "shared": 0,
            "types": 0,
            "tests": 4,
        }
    
    def is_valid_dependency(self, from_layer: str, to_layer: str) -> bool:
        """Check if dependency direction is valid."""
        hierarchy = self.get_layer_hierarchy()
        
        # Shared and types can be imported by anyone
        if to_layer in ["shared", "types"]:
            return True
        
        # Tests can import anything
        if from_layer == "tests":
            return True
        
        # Infra can only import domain, shared, types
        if from_layer == "infra":
            return to_layer in ["domain", "shared", "types"]
        
        # Domain should not import presentation, application, or infra
        if from_layer == "domain":
            return to_layer in ["domain", "shared", "types"]
        
        # Application should not import presentation
        if from_layer == "application":
            return to_layer in ["domain", "application", "shared", "types", "infra"]
        
        # Presentation can import anything except tests
        if from_layer == "presentation":
            return to_layer != "tests"
        
        return True
