from __future__ import annotations

import sys

from _bootstrap import add_src_to_path, repo_root


def main(argv: list[str]) -> int:
    add_src_to_path()
    from skill_creator.cli import cmd_package  # type: ignore
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["claude", "repo"], required=True)
    parser.add_argument("--skill", default="")
    ns = parser.parse_args(argv[1:])

    args = argparse.Namespace(repo_root=str(repo_root()), target=ns.target, skill=ns.skill)
    return cmd_package(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
