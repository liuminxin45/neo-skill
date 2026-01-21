from __future__ import annotations

import sys

from _bootstrap import add_src_to_path, repo_root


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json")
        return 2
    spec_path = argv[1]
    add_src_to_path()
    from skill_creator.cli import cmd_validate  # type: ignore
    import argparse
    args = argparse.Namespace(repo_root=str(repo_root()), spec=spec_path)
    return cmd_validate(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
