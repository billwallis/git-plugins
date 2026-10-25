"""
Raise pull requests.
"""

import argparse
import sys
import urllib.parse
import warnings
import webbrowser
from collections.abc import Sequence
from typing import Any

from git_plugins import (
    _colours as colours,
    _git as git,
)


def _github_pull_request_url(host_url: str, branch_name: str) -> str:
    return f"{host_url}/pull/new/{branch_name}"


def _github_pull_request_url_with_params(
    host_url: str,
    branch_name: str,
    parameters: dict[str, str],
) -> str:
    """
    https://docs.github.com/en/pull-requests/reference/using-query-parameters-to-create-a-pull-request
    """
    # This isn't the "preferred" route since we have to guess the base
    # branch name, but that's required for the URL to support params

    def _parse(value: Any) -> Any:
        if isinstance(value, list):
            return ",".join(value)
        else:
            return value

    params = urllib.parse.urlencode(
        {"quick_pull": 1} | {k: _parse(v) for k, v in parameters.items()},
        safe=",",
    )

    # Assume we always want to merge back to the base branch, not any
    # intermediate branches (e.g. `main` -> `foo` -> `bar` would merge `bar`
    # into `main`)
    base_branch = git.get_default_branch_name()
    if base_branch not in git.DEFAULT_BRANCH_NAMES:
        warnings.warn(  # pragma: no cover
            f"'{base_branch}' detected as default branch, which is not one of {git.DEFAULT_BRANCH_NAMES}",
            stacklevel=1,
        )

    return f"{host_url}/compare/{base_branch}...{branch_name}?{params}"


def _parse_values(key: str, values: list) -> tuple[str, Any]:
    if len(values) == 0:
        # if key.startswith("no-"):
        #     return key[3:], False
        # else:
        #     return key, True
        raise NotImplementedError("flags are not implemented yet")  # pragma: no cover
    elif len(values) == 1:
        return key, values[0]
    else:
        return key, values


def collect_unknown_args(args: list[str]) -> dict[str, str]:
    assert args, f"somehow received empty list of unknown args!"
    if not args[0].startswith("--"):
        raise ValueError(f"could not parse unknown args: first argument must be a flag, not a value")

    key, values = None, []
    result = dict()
    for item in args:
        if item == "--":
            raise ValueError("'--' is unsupported")
        if item.startswith("--"):
            if key is not None:
                assert isinstance(key, str)
                k, v = _parse_values(key, values)
                result[k] = v

            key = item[2:]
            values = []
        else:
            assert key is not None
            values.append(item)

    assert key is not None
    k, v = _parse_values(key, values)
    result[k] = v

    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--push",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    args, unknown_args = parser.parse_known_args(argv)

    remote_url = git.get_remote_url()
    if remote_url.startswith("git@"):
        try:
            http_url = git.ssh_to_http(remote_url)
        except ValueError as err:
            print(colours.colour(f"error: {err}", colours.RED), file=sys.stderr)
            return 1
    else:
        http_url = remote_url

    branch_name = git.get_current_branch_name()
    if http_url.startswith("https://github.com"):
        if unknown_args:
            pull_request_url = _github_pull_request_url_with_params(
                http_url,
                branch_name,
                parameters=collect_unknown_args(unknown_args),
            )
        else:
            pull_request_url = _github_pull_request_url(http_url, branch_name)
    else:
        print(f"error: remote code forge not supported: {http_url}", file=sys.stderr)
        return 1

    if args.push:
        if branch_name in git.DEFAULT_BRANCH_NAMES:
            # not gonna bother implementing something like `--force` -- if the
            # branch needs to be pushed, just use `git push` directly
            print(colours.colour(f"error: pushes to the default branch are prohibited", colours.RED), file=sys.stderr)
            return 1

        for line in git.push(print_cmd=True):
            print(line)

    print(colours.colour(f"Opening PR at: {pull_request_url}", colours.GREEN))
    webbrowser.open(pull_request_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
