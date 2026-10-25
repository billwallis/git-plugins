import textwrap

import pytest

from git_plugins import _git
from git_plugins.wrapup import main

# TODO: Instead of mocking, can we do operations in a totally new git directory?


def test__wrapup__can_switch_delete_fetch_and_pull(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_status",
        lambda: textwrap.dedent(
            """\
            On branch feature-branch
            nothing to commit, working tree clean
            """
        ),
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )
    monkeypatch.setattr(
        _git,
        "switch_branch",
        lambda b, **_: (
            "git switch main",
            "Switched to branch '{b}'",
            "Your branch is up to date with 'origin/{b}'.",
        ),
    )
    monkeypatch.setattr(
        _git,
        "delete_branch",
        lambda b, **_: (
            f"git branch --delete {b} --force",
            f"Deleted branch {b} (was abcd123).",
        ),
    )
    monkeypatch.setattr(
        _git,
        "fetch",
        lambda **_: ("git fetch --prune",),
    )
    monkeypatch.setattr(
        _git,
        "pull",
        lambda **_: (
            "git pull",
            "Updating abcd123..xyz6789",
            "Fast-forward",
            " foo/bar.baz | 3 +++",
            " 1 file changed, 3 insertions(+)",
        ),
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == textwrap.dedent(
        """\
        git switch main
        Switched to branch '{b}'
        Your branch is up to date with 'origin/{b}'.
        git branch --delete feature-branch --force
        Deleted branch feature-branch (was abcd123).
        git fetch --prune
        git pull
        Updating abcd123..xyz6789
        Fast-forward
         foo/bar.baz | 3 +++
         1 file changed, 3 insertions(+)
        """
    )


def test__wrapup__errors_when_repository_is_dirty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_status",
        lambda: textwrap.dedent(
            """\
            On branch feature-branch
            Changes not staged for commit:
              (use "git add <file>..." to update what will be committed)
              (use "git restore <file>..." to discard changes in working directory)
                    modified:   foo/bar.baz

            no changes added to commit (use "git add" and/or "git commit -a")
            """
        ),
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == textwrap.dedent(
        """\
        \x1b[0;31m\x1b[1merror: git repository is dirty\x1b[0m
        \x1b[0;31mrun with `--allow-dirty` to continue anyway\x1b[0m
        """
    )


def test__wrapup__errors_when_on_default_branch(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_status",
        lambda: textwrap.dedent(
            """\
            On branch main
            nothing to commit, working tree clean
            """
        ),
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "main",
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == textwrap.dedent(
        """\
        \x1b[0;31m\x1b[1merror: not on feature branch\x1b[0m
        """
    )
