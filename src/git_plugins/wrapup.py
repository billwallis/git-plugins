import argparse
import sys
from collections.abc import Sequence

from git_plugins import (
    _colours as colours,
    _git as git,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-dirty",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    args = parser.parse_args(argv)

    status = git.get_status()
    if (not args.allow_dirty) and "nothing to commit, working tree clean" not in status:
        print(colours.colour("error: git repository is dirty", colours.RED + colours.BOLD), file=sys.stderr)
        print(colours.colour("run with `--allow-dirty` to continue anyway", colours.RED), file=sys.stderr)
        return 1

    branch_name = git.get_current_branch_name()
    if branch_name in git.DEFAULT_BRANCH_NAMES:
        print(colours.colour("error: not on feature branch", colours.RED + colours.BOLD), file=sys.stderr)
        return 1

    for line in git.switch_branch("main", print_cmd=True):
        print(line)

    for line in git.delete_branch(branch_name, force=True, print_cmd=True):
        print(line)

    for line in git.fetch(prune=True, print_cmd=True):
        print(line)

    for line in git.pull(print_cmd=True):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
