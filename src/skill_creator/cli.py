from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .spec.validate import assert_spec_valid, validate_spec
from .spec.render import generate_all
from .packaging.package import package_claude_skill, package_repo_zip
from .util.fs import ensure_dir, write_json

DEFAULT_QUESTIONS: List[str] = [
    "这个 skill 的一句话目标是什么（动词开头）？",
    "用户会用哪些触发语句/关键词来表述这个需求（至少 5 条）？",
    "期望输出是什么形态（报告/代码/补丁/命令/文件树/清单）？",
    "硬约束有哪些（例如不可改变行为/不可联网/必须跑测试等）？",
    "允许使用的工具边界是什么（shell/git/python/读写文件/网络等）？",
    "需要哪些输入（repo/commit/diff/config/logs 等），从哪里来？",
    "工作流要拆成哪些关键步骤/分支？关键 gate 是什么？",
    "常见失败/边界情况有哪些？希望如何处理（停止/回退/提示）？",
    "哪些内容应放到 references 或 scripts 以降低上下文占用？",
    "需要适配哪些 AI Assistant（Claude/Windsurf/Cursor/GitHub Skills 等）？",
]


def cmd_init(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    skill_name = args.name.strip()
    skill_dir = repo_root / "skills" / skill_name
    ensure_dir(skill_dir / "references")
    ensure_dir(skill_dir / "scripts")
    ensure_dir(skill_dir / "assets")

    spec_path = skill_dir / "skillspec.json"
    if spec_path.exists() and not args.force:
        raise SystemExit(f"Spec already exists: {spec_path} (use --force to overwrite)")

    spec = {
        "version": 1,
        "name": skill_name,
        "description": args.description.strip() if args.description else f"<TODO: describe when to use {skill_name}>",
        "assistants": ["claude", "windsurf", "cursor", "github-skills"],
        "questions": DEFAULT_QUESTIONS,
        "triggers": [
            f"Create a new skill named {skill_name}",
            f"Update the {skill_name} skill",
            f"Generate SKILL.md for {skill_name}",
            f"Package {skill_name} as a Claude .skill zip",
            f"Validate the {skill_name} skill",
        ],
        "freedom_level": "low",
        "workflow": {
            "type": "sequential",
            "steps": [
                {
                    "id": "collect",
                    "title": "Collect requirements (<=10 questions)",
                    "kind": "action",
                    "commands": [],
                    "notes": "Ask only what is missing. Never exceed 10 questions total.",
                },
                {
                    "id": "plan",
                    "title": "Plan resources (SKILL.md vs references vs scripts)",
                    "kind": "action",
                    "commands": [],
                    "notes": "Enforce progressive disclosure: keep SKILL.md concise; move details into references/.",
                },
                {
                    "id": "generate",
                    "title": "Generate multi-assistant outputs",
                    "kind": "action",
                    "commands": [
                        f"skill-creator generate skills/{skill_name}/skillspec.json",
                    ],
                    "notes": "Produce Claude/Windsurf/Cursor/GitHub Skills wrappers.",
                },
                {
                    "id": "validate",
                    "title": "Validate the spec + outputs",
                    "kind": "gate",
                    "commands": [
                        f"skill-creator validate skills/{skill_name}/skillspec.json",
                    ],
                    "notes": "Fail fast on metadata violations or banned files.",
                },
                {
                    "id": "package",
                    "title": "Package for Claude (.skill)",
                    "kind": "action",
                    "commands": [
                        f"skill-creator package --target claude --skill {skill_name}",
                    ],
                    "notes": "Zip root must be the skill folder (not flat files).",
                },
            ],
        },
        "references": [
            "references/output-patterns.md",
            "references/workflows.md",
        ],
        "scripts": [
            "scripts/init_skill.py",
            "scripts/validate_skill.py",
            "scripts/package_skill.py",
        ],
        "assets": [],
    }

    # Seed references from shared templates if present
    shared_data = repo_root / ".shared" / "skill-creator" / "data"
    if (shared_data / "output-patterns.md").exists():
        (skill_dir / "references" / "output-patterns.md").write_text(
            (shared_data / "output-patterns.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    if (shared_data / "workflows.md").exists():
        (skill_dir / "references" / "workflows.md").write_text(
            (shared_data / "workflows.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    # Minimal script placeholders (deterministic tools often live here)
    (skill_dir / "scripts" / "init_skill.py").write_text(
        """# Placeholder: generated skill-specific initializer\n""",
        encoding="utf-8",
    )
    (skill_dir / "scripts" / "validate_skill.py").write_text(
        """# Placeholder: generated skill-specific validator\n""",
        encoding="utf-8",
    )
    (skill_dir / "scripts" / "package_skill.py").write_text(
        """# Placeholder: generated skill-specific packager\n""",
        encoding="utf-8",
    )

    write_json(spec_path, spec)
    print(str(spec_path))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    spec_path = Path(args.spec).resolve()
    assert_spec_valid(spec_path)
    spec = generate_all(repo_root, spec_path)
    print(f"Generated outputs for: {spec.name}")
    return 0


def _validate_claude_frontmatter(skill_md: Path) -> List[str]:
    # Strict: frontmatter must contain only name + description.
    txt = skill_md.read_text(encoding="utf-8")
    if not txt.startswith("---\n"):
        return [f"Missing YAML frontmatter: {skill_md}"]
    try:
        end = txt.index("\n---\n", 4)
    except ValueError:
        return [f"Unterminated YAML frontmatter: {skill_md}"]
    fm = txt[4:end].strip().splitlines()
    keys = []
    for line in fm:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        keys.append(line.split(":", 1)[0].strip())
    missing = [k for k in ["name", "description"] if k not in keys]
    extra = [k for k in keys if k not in {"name", "description"}]
    errs = []
    if missing:
        errs.append(f"Frontmatter missing keys {missing}: {skill_md}")
    if extra:
        errs.append(f"Frontmatter has extra keys {extra} (Claude strict mode): {skill_md}")
    return errs


def cmd_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    spec_path = Path(args.spec).resolve()

    errors = validate_spec(spec_path)
    if errors:
        raise SystemExit("Spec validation failed:\n- " + "\n- ".join(errors))

    # Validate generated outputs if present
    spec_name = Path(args.spec).resolve().parent.name
    claude_skill_md = repo_root / ".claude" / "skills" / spec_name / "SKILL.md"
    if claude_skill_md.exists():
        fm_errors = _validate_claude_frontmatter(claude_skill_md)
        if fm_errors:
            raise SystemExit("Claude SKILL.md validation failed:\n- " + "\n- ".join(fm_errors))

    # Ban noisy docs inside target skill folders (keep only execution-relevant files)
    banned = {"README.md", "CHANGELOG.md", "INSTALL.md"}
    for target_root in [repo_root / ".claude" / "skills" / spec_name, repo_root / ".github" / "skills" / spec_name]:
        if not target_root.exists():
            continue
        for p in target_root.rglob("*"):
            if p.is_file() and p.name in banned:
                raise SystemExit(f"Banned file inside skill bundle: {p}")

    print("OK")
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    out_dir = repo_root / "dist"
    ensure_dir(out_dir)

    if args.target == "claude":
        # Validate before packaging
        cmd_validate(
            argparse.Namespace(
                repo_root=str(repo_root),
                spec=str(repo_root / "skills" / args.skill / "skillspec.json"),
            )
        )
        out = package_claude_skill(repo_root, args.skill, out_dir)
        print(str(out))
        return 0

    if args.target == "repo":
        out = package_repo_zip(repo_root, out_dir / f"{repo_root.name}.zip")
        print(str(out))
        return 0

    raise SystemExit(f"Unknown target: {args.target}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skill-creator",
        description="Canonical SkillSpec -> multi-assistant skill outputs",
    )
    p.add_argument("--repo-root", default=".", help="Repo root (default: current directory)")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a new skill directory under skills/")
    p_init.add_argument("name", help="Skill name (kebab-case)")
    p_init.add_argument("--description", default="", help="Short description (should include trigger conditions)")
    p_init.add_argument("--force", action="store_true", help="Overwrite if already exists")
    p_init.set_defaults(func=cmd_init)

    p_gen = sub.add_parser("generate", help="Generate multi-assistant outputs from skillspec.json")
    p_gen.add_argument("spec", help="Path to skillspec.json")
    p_gen.set_defaults(func=cmd_generate)

    p_val = sub.add_parser("validate", help="Validate spec and generated outputs")
    p_val.add_argument("spec", help="Path to skillspec.json")
    p_val.set_defaults(func=cmd_validate)

    p_pkg = sub.add_parser("package", help="Package outputs")
    p_pkg.add_argument("--target", choices=["claude", "repo"], required=True)
    p_pkg.add_argument("--skill", default="", help="Skill name (required for --target claude)")
    p_pkg.set_defaults(func=cmd_package)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    rc = args.func(args)
    raise SystemExit(rc)
