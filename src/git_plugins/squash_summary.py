import argparse
from collections.abc import Sequence

from git_plugins import (
    _git as git,
)


def main(argv: Sequence[str] | None = None) -> int:
    """
    Produce a summary message for a branch's squash merge.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    args = parser.parse_args(argv)

    commits = git.get_commits_on_branch(args.base)
    for commit in commits.splitlines():
        print(f"- {commit}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
