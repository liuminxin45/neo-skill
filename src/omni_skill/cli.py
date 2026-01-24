from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set

from skill_creator.cli import cmd_generate

STATE_FILE = ".neo-skill.json"

SUPPORTED_AIS = [
    "claude", "cursor", "windsurf", "antigravity", "copilot",
    "kiro", "codex", "qoder", "roocode", "gemini", "trae", "opencode", "continue",
]

AI_COPY_RULES: Dict[str, Dict] = {
    "claude": {
        "sync_pairs": [(".claude/skills", ".claude/skills")],
        "base_dirs": [".claude"],
    },
    "windsurf": {
        "sync_pairs": [(".windsurf/workflows", ".windsurf/workflows")],
        "base_dirs": [".windsurf"],
    },
    "cursor": {
        "sync_pairs": [(".cursor/commands", ".cursor/commands")],
        "base_dirs": [".cursor"],
    },
    "copilot": {
        "sync_pairs": [(".github/skills", ".github/skills")],
        "base_dirs": [".github"],
    },
    "antigravity": {
        "sync_pairs": [(".agent", ".agent"), (".shared", ".shared")],
        "base_dirs": [".agent", ".shared"],
    },
    "kiro": {
        "sync_pairs": [(".kiro", ".kiro")],
        "base_dirs": [".kiro"],
    },
    "codex": {
        "sync_pairs": [(".codex", ".codex")],
        "base_dirs": [".codex"],
    },
    "qoder": {
        "sync_pairs": [(".qoder", ".qoder")],
        "base_dirs": [".qoder"],
    },
    "roocode": {
        "sync_pairs": [(".roocode", ".roocode")],
        "base_dirs": [".roocode"],
    },
    "gemini": {
        "sync_pairs": [(".gemini", ".gemini")],
        "base_dirs": [".gemini"],
    },
    "trae": {
        "sync_pairs": [(".trae", ".trae")],
        "base_dirs": [".trae"],
    },
    "opencode": {
        "sync_pairs": [(".opencode", ".opencode")],
        "base_dirs": [".opencode"],
    },
    "continue": {
        "sync_pairs": [(".continue", ".continue")],
        "base_dirs": [".continue"],
    },
}


def _get_pkg_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _get_pkg_version() -> str:
    pkg_json = _get_pkg_root() / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            return str(data.get("version", "unknown")).strip() or "unknown"
        except Exception:
            pass
    return "unknown"


def _write_init_state(cwd: Path, selected_ais: List[str]) -> None:
    state_path = cwd / STATE_FILE
    payload = {"ais": selected_ais}
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _read_init_state(cwd: Path) -> Dict:
    state_path = cwd / STATE_FILE
    if not state_path.exists():
        return {"ok": False, "error": f"Missing {STATE_FILE}. Please run: omni-skill init --ai <target>"}
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        ais = [a.strip().lower() for a in data.get("ais", []) if a]
        resolved = _resolve_selected_ais(ais)
        if not resolved["ok"]:
            return resolved
        if not resolved["selected"]:
            return {"ok": False, "error": f"Invalid {STATE_FILE}: ais is empty. Please re-run init."}
        return {"ok": True, "selected": resolved["selected"]}
    except Exception:
        return {"ok": False, "error": f"Invalid {STATE_FILE}. Please delete it and re-run init."}


def _resolve_selected_ais(ai_values: List[str]) -> Dict:
    supported: Set[str] = set(SUPPORTED_AIS + ["all"])
    if not ai_values:
        return {"ok": True, "selected": []}
    for v in ai_values:
        if v not in supported:
            return {"ok": False, "error": f"Unknown --ai value: {v}"}
    if "all" in ai_values:
        return {"ok": True, "selected": list(SUPPORTED_AIS)}
    return {"ok": True, "selected": list(set(ai_values))}


def _sync_dir_replace(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        dest_path = dest / entry.name
        if dest_path.exists():
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()
        if entry.is_dir():
            shutil.copytree(entry, dest_path)
        else:
            shutil.copy2(entry, dest_path)


def _build_sync_pairs(effective_ais: List[str]) -> List[tuple]:
    pairs = [
        ("skills", "skills"),
        (".shared/skill-creator", ".shared/skill-creator"),
    ]
    for ai in effective_ais:
        rules = AI_COPY_RULES.get(ai)
        if rules:
            pairs.extend(rules["sync_pairs"])
    return pairs


def _perform_sync(pkg_root: Path, cwd: Path, sync_pairs: List[tuple]) -> None:
    for src_rel, dest_rel in sync_pairs:
        src = pkg_root / src_rel
        dest = cwd / dest_rel
        if src.resolve() == dest.resolve():
            print(f"  Skipping {dest_rel} (source equals destination)")
            continue
        if not src.exists():
            print(f"  Skipping {dest_rel} (not found in package)")
            continue
        print(f"  Syncing {dest_rel} (replace items)")
        _sync_dir_replace(src, dest)


def _write_version_files(cwd: Path, effective_ais: List[str], version: str) -> None:
    for ai in effective_ais:
        rules = AI_COPY_RULES.get(ai)
        if not rules:
            continue
        for base_dir in rules["base_dirs"]:
            dir_path = cwd / base_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            (dir_path / "VERSION").write_text(f"{version}\n", encoding="utf-8")


def _generate_outputs_best_effort(pkg_root: Path, cwd: Path) -> None:
    skills_dir = cwd / "skills"
    if not skills_dir.exists():
        return
    specs = sorted(skills_dir.glob("*/skillspec.json"))
    if not specs:
        return
    print("\nGenerating skill outputs from skillspec.json ...")
    for spec_path in specs:
        try:
            ns = argparse.Namespace(repo_root=str(cwd), spec=str(spec_path), all=True)
            cmd_generate(ns)
        except SystemExit as e:
            rel = spec_path.relative_to(cwd) if spec_path.is_relative_to(cwd) else spec_path
            print(f"  Skipping generator for {rel} (exit {e.code})")


def _install_skills_from_dir(skills_dir: Path, cwd: Path) -> int:
    """
    Install skills from a directory (either from npm package or local path).
    Generates outputs for all AI targets.
    """
    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        return 1
    
    specs = sorted(skills_dir.glob("*/skillspec.json"))
    if not specs:
        print(f"No skillspec.json found in: {skills_dir}")
        return 1
    
    print(f"\nInstalling {len(specs)} skill(s) from {skills_dir} ...")
    for spec_path in specs:
        skill_name = spec_path.parent.name
        print(f"  Installing skill: {skill_name}")
        
        # Copy skill to cwd/skills if not already there
        dest_skill_dir = cwd / "skills" / skill_name
        if spec_path.parent.resolve() != dest_skill_dir.resolve():
            dest_skill_dir.parent.mkdir(parents=True, exist_ok=True)
            if dest_skill_dir.exists():
                import shutil
                shutil.rmtree(dest_skill_dir)
            shutil.copytree(spec_path.parent, dest_skill_dir)
            print(f"    Copied to: {dest_skill_dir}")
        
        # Generate outputs for all targets
        try:
            ns = argparse.Namespace(repo_root=str(cwd), spec=str(cwd / "skills" / skill_name / "skillspec.json"), all=True)
            cmd_generate(ns)
            print(f"    Generated outputs for all targets")
        except SystemExit as e:
            print(f"    Warning: Generator failed (exit {e.code})")
    
    return 0


def _handle_init(selected_ais: List[str], mode: str) -> int:
    pkg_root = _get_pkg_root()
    cwd = Path.cwd().resolve()
    version = _get_pkg_version()
    effective_ais = selected_ais if selected_ais else list(SUPPORTED_AIS)

    sync_pairs = _build_sync_pairs(effective_ais)
    print("Initializing skills in:", cwd)
    _perform_sync(pkg_root, cwd, sync_pairs)
    
    # Install all skills from npm package
    pkg_skills_dir = pkg_root / "skills"
    if pkg_skills_dir.exists():
        _install_skills_from_dir(pkg_skills_dir, cwd)
    
    _write_version_files(cwd, effective_ais, version)
    print("\nDone! neo-skill initialized.")

    if mode == "init":
        _write_init_state(cwd, selected_ais)

    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    ai_values = [a.strip().lower() for a in (args.ai or []) if a]
    resolved = _resolve_selected_ais(ai_values)
    if not resolved["ok"]:
        raise SystemExit(resolved["error"])
    if not resolved["selected"]:
        _print_init_help()
        return 1
    return _handle_init(resolved["selected"], "init")


def _cmd_install(args: argparse.Namespace) -> int:
    """
    Install skill(s) from a local directory.
    Usage: omni-skill install <path-to-skill-or-skills-dir>
    """
    cwd = Path.cwd().resolve()
    skill_path = Path(args.path).resolve()
    
    if not skill_path.exists():
        raise SystemExit(f"Path not found: {skill_path}")
    
    # Check if it's a single skill directory (contains skillspec.json)
    if (skill_path / "skillspec.json").exists():
        # Single skill
        temp_skills_dir = skill_path.parent
        return _install_skills_from_dir(temp_skills_dir, cwd)
    
    # Check if it's a skills directory (contains subdirs with skillspec.json)
    elif skill_path.is_dir():
        return _install_skills_from_dir(skill_path, cwd)
    
    else:
        raise SystemExit(f"Invalid path: {skill_path}. Must be a skill directory or skills directory.")


def _cmd_update(args: argparse.Namespace) -> int:
    """
    Update npm package and re-initialize skills.
    """
    import subprocess
    
    cwd = Path.cwd().resolve()
    state = _read_init_state(cwd)
    if not state["ok"]:
        raise SystemExit(state["error"])
    
    print("Updating neo-skill npm package...")
    result = subprocess.run(
        ["npm", "install", "neo-skill@latest"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Warning: npm install failed: {result.stderr}")
        print("Continuing with re-initialization...")
    else:
        print("Package updated successfully.")
    
    print("\nRe-initializing skills...")
    return _handle_init(state["selected"], "update")


def _print_init_help() -> None:
    supported = "|".join(SUPPORTED_AIS + ["all"])
    print("Usage: omni-skill init --ai <target>")
    print(f"  <target>: {supported}")
    print("Examples:")
    print("  omni-skill init --ai claude")
    print("  omni-skill init --ai cursor")
    print("  omni-skill init --ai windsurf")
    print("  omni-skill init --ai all")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="omni-skill",
        description="Multi-assistant skill initializer and generator.",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize skills for target AI assistants")
    p_init.add_argument("--ai", action="append", help="Target AI (can be repeated)")
    p_init.set_defaults(func=_cmd_init)

    p_install = sub.add_parser("install", help="Install skill(s) from a local directory")
    p_install.add_argument("path", help="Path to skill directory or skills directory")
    p_install.set_defaults(func=_cmd_install)

    p_update = sub.add_parser("update", help="Update npm package and re-initialize skills")
    p_update.set_defaults(func=_cmd_update)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    rc = args.func(args)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
