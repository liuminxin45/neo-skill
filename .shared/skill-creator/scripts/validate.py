#!/usr/bin/env python3
"""
Skill Validator - Validate skillspec.json and generated outputs

Usage:
    python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
    python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json --strict
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
REPO_ROOT = SCRIPT_DIR.parent.parent.parent


def load_validation_rules() -> List[Dict[str, str]]:
    """Load validation rules from CSV."""
    rules_path = DATA_DIR / "validation-rules.csv"
    if not rules_path.exists():
        return []
    with rules_path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_kebab_case(name: str) -> bool:
    """Check if name is valid kebab-case."""
    return bool(re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name))


def validate_spec(spec: Dict[str, Any], spec_path: Path) -> List[Tuple[str, str, str]]:
    """
    Validate skillspec.json structure and content.
    Returns list of (severity, rule_id, message) tuples.
    """
    errors: List[Tuple[str, str, str]] = []
    
    # name validation
    name = spec.get("name", "")
    if not name:
        errors.append(("error", "name_required", "name is required"))
    elif not validate_kebab_case(name):
        errors.append(("error", "name_kebab", f"name '{name}' is not valid kebab-case"))
    
    # description validation
    desc = spec.get("description", "")
    if not desc:
        errors.append(("error", "description_required", "description is required"))
    elif len(desc) < 20:
        errors.append(("warning", "description_short", "description is very short (<20 chars)"))
    
    # questions validation
    questions = spec.get("questions", [])
    if len(questions) > 10:
        errors.append(("error", "questions_max_10", f"questions must be <= 10 (got {len(questions)})"))
    
    # triggers validation
    triggers = spec.get("triggers", [])
    if len(triggers) < 3:
        errors.append(("warning", "triggers_min_3", f"recommend at least 3 triggers (got {len(triggers)})"))
    
    # workflow validation
    workflow = spec.get("workflow", {})
    if not workflow:
        errors.append(("error", "workflow_required", "workflow is required"))
    else:
        workflow_type = workflow.get("type", "")
        if workflow_type not in ("sequential", "conditional"):
            errors.append(("error", "workflow_type_invalid", f"workflow.type must be sequential or conditional"))
        
        steps = workflow.get("steps", [])
        if not steps:
            errors.append(("error", "steps_not_empty", "workflow.steps must not be empty"))
        else:
            for i, step in enumerate(steps):
                if not step.get("id"):
                    errors.append(("error", "step_id_required", f"step[{i}].id is required"))
                if not step.get("title"):
                    errors.append(("error", "step_title_required", f"step[{i}].title is required"))
                
                notes = step.get("notes", "")
                if len(notes) > 500:
                    errors.append(("warning", "notes_max_length", 
                                   f"step[{i}].notes is long ({len(notes)} chars) - consider using references/"))
    
    # freedom_level validation
    freedom = spec.get("freedom_level", "low")
    if freedom not in ("low", "medium", "high"):
        errors.append(("error", "freedom_level_invalid", "freedom_level must be low, medium, or high"))
    
    return errors


def validate_claude_output(skill_name: str, repo_root: Path) -> List[Tuple[str, str, str]]:
    """Validate Claude SKILL.md strict frontmatter."""
    errors: List[Tuple[str, str, str]] = []
    
    skill_md = repo_root / ".claude" / "skills" / skill_name / "SKILL.md"
    if not skill_md.exists():
        return errors  # Not generated yet, skip
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Check frontmatter
    if not content.startswith("---\n"):
        errors.append(("error", "claude_frontmatter_missing", "Claude SKILL.md missing YAML frontmatter"))
        return errors
    
    try:
        end_idx = content.index("\n---\n", 4)
        frontmatter = content[4:end_idx]
    except ValueError:
        errors.append(("error", "claude_frontmatter_unterminated", "Claude SKILL.md frontmatter not closed"))
        return errors
    
    # Parse frontmatter keys
    keys = set()
    for line in frontmatter.splitlines():
        if ":" in line:
            key = line.split(":")[0].strip()
            if key:
                keys.add(key)
    
    allowed_keys = {"name", "description"}
    extra_keys = keys - allowed_keys
    if extra_keys:
        errors.append(("error", "claude_frontmatter_strict", 
                       f"Claude frontmatter has extra keys (strict mode): {extra_keys}"))
    
    return errors


def validate_banned_files(skill_name: str, repo_root: Path) -> List[Tuple[str, str, str]]:
    """Check for banned files in skill bundles."""
    errors: List[Tuple[str, str, str]] = []
    
    banned = {"README.md", "CHANGELOG.md", "INSTALL.md", "LICENSE", "LICENSE.md"}
    
    for target_dir in [
        repo_root / ".claude" / "skills" / skill_name,
        repo_root / ".github" / "skills" / skill_name,
    ]:
        if not target_dir.exists():
            continue
        
        for path in target_dir.rglob("*"):
            if path.is_file() and path.name in banned:
                errors.append(("error", "no_banned_files", f"Banned file in skill bundle: {path}"))
    
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate skillspec.json and outputs")
    parser.add_argument("spec", help="Path to skillspec.json")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--repo-root", "-r", default=str(REPO_ROOT), help="Repository root")
    
    args = parser.parse_args()
    
    spec_path = Path(args.spec).resolve()
    repo_root = Path(args.repo_root).resolve()
    
    if not spec_path.exists():
        print(f"ERROR: Spec not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    skill_name = spec.get("name", "")
    
    all_errors: List[Tuple[str, str, str]] = []
    
    # Validate spec
    all_errors.extend(validate_spec(spec, spec_path))
    
    # Validate outputs
    all_errors.extend(validate_claude_output(skill_name, repo_root))
    all_errors.extend(validate_banned_files(skill_name, repo_root))
    
    # Report
    has_errors = False
    has_warnings = False
    
    for severity, rule_id, message in all_errors:
        prefix = "ERROR" if severity == "error" else "WARN"
        print(f"[{prefix}] {rule_id}: {message}")
        
        if severity == "error":
            has_errors = True
        else:
            has_warnings = True
    
    if not all_errors:
        print("✓ Validation passed")
        sys.exit(0)
    
    if has_errors or (args.strict and has_warnings):
        sys.exit(1)
    
    print("✓ Validation passed with warnings")
    sys.exit(0)


if __name__ == "__main__":
    main()
