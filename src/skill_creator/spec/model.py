from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..util.fs import read_json


def _as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _kebab_case_ok(name: str) -> bool:
    return bool(name) and all(c.islower() or c.isdigit() or c == '-' for c in name) and '--' not in name and not name.startswith('-') and not name.endswith('-')


@dataclass
class WorkflowStep:
    id: str
    title: str
    kind: str = "action"  # action|gate|branch
    commands: List[str] = field(default_factory=list)
    notes: str = ""

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "WorkflowStep":
        return WorkflowStep(
            id=str(d.get("id", "")).strip(),
            title=str(d.get("title", "")).strip(),
            kind=str(d.get("kind", "action")).strip(),
            commands=[str(c) for c in _as_list(d.get("commands"))],
            notes=str(d.get("notes", "")).strip(),
        )


@dataclass
class SkillSpec:
    version: int
    name: str
    description: str

    # Multi-assistant support
    assistants: List[str] = field(default_factory=lambda: ["claude", "windsurf", "cursor", "github-skills"])

    # Prompting
    questions: List[str] = field(default_factory=list)  # must be <= 10
    triggers: List[str] = field(default_factory=list)
    freedom_level: str = "low"  # low|medium|high

    # Workflow + assets
    workflow_type: str = "sequential"  # sequential|conditional
    steps: List[WorkflowStep] = field(default_factory=list)

    references: List[str] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)

    @staticmethod
    def from_path(path: Path) -> "SkillSpec":
        data = read_json(path)
        return SkillSpec.from_dict(data)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SkillSpec":
        steps = [WorkflowStep.from_dict(x) for x in _as_list(d.get("workflow", {}).get("steps"))]
        return SkillSpec(
            version=int(d.get("version", 1)),
            name=str(d.get("name", "")).strip(),
            description=str(d.get("description", "")).strip(),
            assistants=[str(x) for x in _as_list(d.get("assistants"))] or ["claude", "windsurf", "cursor", "github-skills"],
            questions=[str(x) for x in _as_list(d.get("questions"))],
            triggers=[str(x) for x in _as_list(d.get("triggers"))],
            freedom_level=str(d.get("freedom_level", "low")).strip(),
            workflow_type=str(d.get("workflow", {}).get("type", "sequential")).strip(),
            steps=steps,
            references=[str(x) for x in _as_list(d.get("references"))],
            scripts=[str(x) for x in _as_list(d.get("scripts"))],
            assets=[str(x) for x in _as_list(d.get("assets"))],
        )

    def validate_basic(self) -> List[str]:
        errors: List[str] = []
        if self.version != 1:
            errors.append(f"Unsupported spec version: {self.version}")
        if not _kebab_case_ok(self.name):
            errors.append("name must be kebab-case (lowercase letters, digits, hyphen)")
        if not self.description:
            errors.append("description is required")
        if len(self.questions) > 10:
            errors.append("questions must be <= 10")
        if self.freedom_level not in {"low", "medium", "high"}:
            errors.append("freedom_level must be one of: low, medium, high")
        if self.workflow_type not in {"sequential", "conditional"}:
            errors.append("workflow.type must be sequential or conditional")
        if not self.steps:
            errors.append("workflow.steps must not be empty")
        # minimal step validation
        for i, s in enumerate(self.steps):
            if not s.id:
                errors.append(f"workflow.steps[{i}].id is required")
            if not s.title:
                errors.append(f"workflow.steps[{i}].title is required")
        return errors
