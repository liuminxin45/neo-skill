from __future__ import annotations

import argparse
import os
from pathlib import Path

from skill_creator.cli import cmd_generate, cmd_validate


def _resolve_repo_root(repo_root_arg: str) -> Path:
    if repo_root_arg:
        return Path(repo_root_arg).resolve()
    return Path.cwd().resolve()


def _resolve_spec_path(repo_root: Path, args: argparse.Namespace) -> Path:
    if getattr(args, "spec", ""):
        return Path(args.spec).resolve()

    if getattr(args, "skill", ""):
        return (repo_root / "skills" / args.skill / "skillspec.json").resolve()

    cwd_spec = Path.cwd() / "skillspec.json"
    if cwd_spec.exists():
        return cwd_spec.resolve()

    env_spec = os.environ.get("OMNI_SKILL_SPEC", "").strip()
    if env_spec:
        return Path(env_spec).resolve()

    env_skill = os.environ.get("OMNI_SKILL", "").strip()
    if env_skill:
        return (repo_root / "skills" / env_skill / "skillspec.json").resolve()

    default = repo_root / "skills" / "coding-standards" / "skillspec.json"
    if default.exists():
        return default.resolve()

    specs = sorted((repo_root / "skills").glob("*/skillspec.json"))
    if len(specs) == 1:
        return specs[0].resolve()

    if specs:
        found = "\n- " + "\n- ".join(str(p.relative_to(repo_root)) for p in specs)
        raise SystemExit(
            "Multiple skillspec.json found; please pass --skill <name> or --spec <path>. Found:" + found
        )

    raise SystemExit("No skillspec.json found. Run from skills/<skill>/ or pass --spec/--skill.")


def _cmd_run(args: argparse.Namespace) -> int:
    repo_root = _resolve_repo_root(args.repo_root)
    spec_path = _resolve_spec_path(repo_root, args)

    cmd_generate(argparse.Namespace(repo_root=str(repo_root), spec=str(spec_path)))
    return cmd_validate(argparse.Namespace(repo_root=str(repo_root), spec=str(spec_path)))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="omni-skill",
        description="Short wrapper around skill-creator (generate + validate).",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Generate + validate (cursor-friendly wrapper)")
    p_init.add_argument("--cursor", action="store_true")
    p_init.add_argument("--repo-root", default=".")
    p_init.add_argument("--skill", default="")
    p_init.add_argument("--spec", default="")
    p_init.set_defaults(func=_cmd_run)

    p_do = sub.add_parser("do", help="Generate + validate (agent-friendly wrapper)")
    p_do.add_argument("--agent", action="store_true")
    p_do.add_argument("--repo-root", default=".")
    p_do.add_argument("--skill", default="")
    p_do.add_argument("--spec", default="")
    p_do.set_defaults(func=_cmd_run)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    rc = args.func(args)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
