import pathlib
import subprocess
import re
import warnings
from collections.abc import Iterable, Generator

from git_plugins import _colours as colours

# TODO: Bin this in favour of `get_default_branch_name`
DEFAULT_BRANCH_NAMES = ["main", "master"]


class GitError(Exception):
    pass


def _run_git_cmd(
    args: Iterable[str],
    git_dir: pathlib.Path | None = None,
    print_cmd: bool = False,
    check: bool = False,
) -> Generator[str]:
    cmds = ("git",) if git_dir is None else ("git", "-C", git_dir)
    if print_cmd:
        yield colours.colour(" ".join([*cmds, *args]), colours.BLUE + colours.BOLD)

    # https://stackoverflow.com/a/4417735
    popen = subprocess.Popen(
        args=(*cmds, *args),
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    if popen.stdout:
        for line in popen.stdout:
            yield line.rstrip("\n")
    if popen.stderr:
        for line in popen.stderr:
            yield line.rstrip("\n")

    popen.wait()
    if check and popen.returncode != 0:
        raise GitError("git returned a non-zero exit code")


def get_status() -> str:
    return "\n".join(_run_git_cmd(("status",)))


def get_current_branch_name() -> str:
    return next(_run_git_cmd(("branch", "--show-current")))


def get_default_branch_name() -> str:
    """
    Return the default branch for the current repository.
    """

    merge_bases = list(_run_git_cmd(("show-branch", "--merge-base")))
    assert len(merge_bases) == 1, f"expected 1 merge base, found {len(merge_bases)}: {merge_bases}"

    default_branch_names = list(_run_git_cmd(("name-rev", "--name-only", merge_bases[0])))
    assert len(merge_bases) == 1, f"expected 1 default branch name, found {len(default_branch_names)}: {default_branch_names}"

    default_branch_name = default_branch_names[0]
    if default_branch_name not in DEFAULT_BRANCH_NAMES:
        warnings.warn(  # pragma: no cover
            f"'{default_branch_name}' detected as default branch, which is not one of {DEFAULT_BRANCH_NAMES}",
            stacklevel=1,
        )

    return default_branch_name


def get_remote_url() -> str:
    origin_name = "origin"
    return "\n".join(
        _run_git_cmd(("remote", "get-url", origin_name))
    )


def get_commits_on_branch(base_branch: str) -> str:
    return "\n".join(
        _run_git_cmd(
            ("log", f"{base_branch}..HEAD", "--format=%s", "--reverse")
        )
    )

# TODO: Switch `stream` and `print_cmd` for some kind of "controller" param?
#       e.g.
#           do_thing(..., git.Controls(stream=True, print_cmd=False))

def fetch(
    prune: bool = True,
    stream: bool = True,
    print_cmd: bool = False,
) -> Generator[str] | str:
    args = ("fetch", )
    if prune:
        args = (*args, "--prune")
    cmd = _run_git_cmd(args, print_cmd=print_cmd)
    if stream:
        def wrapper():
            yield from cmd

        return wrapper()
    else:
        return "\n".join(cmd)

def pull(
    stream: bool = True,
    print_cmd: bool = False,
) -> Generator[str] | str:
    cmd = _run_git_cmd(("pull", ), print_cmd=print_cmd)
    if stream:
        def wrapper():
            yield from cmd

        return wrapper()
    else:
        return "\n".join(cmd)

def push(
    stream: bool = True,
    print_cmd: bool = False,
) -> Generator[str] | str:
    cmd = _run_git_cmd(("push", ), print_cmd=print_cmd)
    if stream:
        def wrapper():
            yield from cmd

        return wrapper()
    else:
        return "\n".join(cmd)


def switch_branch(
    target_branch: str,
    stream: bool = True,
    print_cmd: bool = False,
) -> Generator[str] | str:
    cmd = _run_git_cmd(("switch", target_branch), print_cmd=print_cmd)
    if stream:
        def wrapper():
            yield from cmd

        return wrapper()
    else:
        return "\n".join(cmd)


def delete_branch(
    target_branch: str,
    force: bool = False,
    stream: bool = True,
    print_cmd: bool = False,
) -> Generator[str] | str:
    args = ("branch", "--delete", target_branch)
    if force:
        args = (*args, "--force")
    cmd = _run_git_cmd(args, print_cmd=print_cmd)

    if stream:
        def wrapper():
            yield from cmd

        return wrapper()
    else:
        return "\n".join(cmd)


# TODO: Should this go here?
def ssh_to_http(ssh_url: str) -> str:
    ssh_pattern = r"git@([\w.]+):([\w-]+)/([\w-]+)"
    matches = re.compile(ssh_pattern).findall(ssh_url)
    if not matches:
        raise ValueError(
            f"Could not handle SSH remote with URL '{ssh_url}'. Expected URL with pattern '{ssh_pattern}'"
        )

    host, owner, repo = matches[0]
    return f"https://{host}/{owner}/{repo}"
