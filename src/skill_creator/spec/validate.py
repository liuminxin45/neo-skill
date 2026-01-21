from __future__ import annotations

from pathlib import Path
from typing import List

from .model import SkillSpec


def validate_spec(spec_path: Path) -> List[str]:
    spec = SkillSpec.from_path(spec_path)
    return spec.validate_basic()


def assert_spec_valid(spec_path: Path) -> None:
    errors = validate_spec(spec_path)
    if errors:
        joined = "\n- " + "\n- ".join(errors)
        raise SystemExit(f"Spec validation failed:{joined}\n")
