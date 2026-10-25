import textwrap
import webbrowser
from collections.abc import Sequence

import pytest

from git_plugins import _git
from git_plugins.pull_request import main

# TODO: Instead of mocking, can we do operations in a totally new git directory?


def test__pull_request__can_raise_a_pull_request_on_github__with_http_remote(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "https://github.com/owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )
    monkeypatch.setattr(
        webbrowser,
        "open",
        lambda _: None,
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == "\x1b[0;32mOpening PR at: https://github.com/owner/repository/pull/new/feature-branch\x1b[0m\n"


def test__pull_request__can_raise_a_pull_request_on_github__with_ssh_remote(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )
    monkeypatch.setattr(
        webbrowser,
        "open",
        lambda _: None,
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == "\x1b[0;32mOpening PR at: https://github.com/owner/repository/pull/new/feature-branch\x1b[0m\n"


def test__pull_request__errors_when_ssh_url_is_unknown(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:/owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == "\x1b[0;31merror: Could not handle SSH remote with URL 'git@github.com:/owner/repository'. Expected URL with pattern 'git@([\\w.]+):([\\w-]+)/([\\w-]+)'\x1b[0m\n"


def test__pull_request__can_raise_a_pull_request_on_github__with_push(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )
    monkeypatch.setattr(
        _git,
        "push",
        lambda **_: (
            "Enumerating objects: 3, done.",
            "Counting objects: 100% (3/3), done.",
            "Delta compression using up to 10 threads",
            "Compressing objects: 100% (2/2), done.",
            "Writing objects: 100% (2/2), 462 bytes | 462.00 KiB/s, done.",
            "Total 2 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0)",
            "remote: Resolving deltas: 100% (1/1), completed with 1 local object.",
            "remote:",
            "remote: Create a pull request for 'feature-branch' on GitHub by visiting:",
            "remote:      https://github.com/owner/repository/pull/new/feature-branch",
            "remote:",
            "To github.com:repository/scratch.git",
            " * [new branch]      feature-branch -> feature-branch",
            "branch 'feature-branch' set up to track 'origin/feature-branch'.",
        ),
    )
    monkeypatch.setattr(
        webbrowser,
        "open",
        lambda _: None,
    )

    rc = main(["--push"])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == textwrap.dedent(
        """\
        Enumerating objects: 3, done.
        Counting objects: 100% (3/3), done.
        Delta compression using up to 10 threads
        Compressing objects: 100% (2/2), done.
        Writing objects: 100% (2/2), 462 bytes | 462.00 KiB/s, done.
        Total 2 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0)
        remote: Resolving deltas: 100% (1/1), completed with 1 local object.
        remote:
        remote: Create a pull request for 'feature-branch' on GitHub by visiting:
        remote:      https://github.com/owner/repository/pull/new/feature-branch
        remote:
        To github.com:repository/scratch.git
         * [new branch]      feature-branch -> feature-branch
        branch 'feature-branch' set up to track 'origin/feature-branch'.
        \x1b[0;32mOpening PR at: https://github.com/owner/repository/pull/new/feature-branch\x1b[0m
        """
    )


def test__pull_request__errors_when_attempting_to_push_default_branch(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "main",
    )

    rc = main(["--push"])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == "\x1b[0;31merror: pushes to the default branch are prohibited\x1b[0m\n"


def test__pull_request__can_raise_a_pull_request_on_github__with_custom_parameters(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )
    monkeypatch.setattr(
        _git,
        "get_default_branch_name",
        lambda: "main",
    )
    monkeypatch.setattr(
        webbrowser,
        "open",
        lambda _: None,
    )

    rc = main(
        [
            *("--title", "This is a title"),
            *("--template", "custom.md"),
            *("--tags", "tag1", "tag2", "tag3"),
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == "\x1b[0;32mOpening PR at: https://github.com/owner/repository/compare/main...feature-branch?quick_pull=1&title=This+is+a+title&template=custom.md&tags=tag1,tag2,tag3\x1b[0m\n"


@pytest.mark.parametrize(
    "args",
    [
        ["bad-first-arg"],
        ["--unsupported", "separator", "--", "unreachable"],
    ],
)
def test__pull_request__errors_when_unknown_args_cannot_be_parsed(
    monkeypatch: pytest.MonkeyPatch,
    args: Sequence[str],
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@github.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )

    # TODO: This should be a CLI error, not an exception
    with pytest.raises(ValueError):
        main(args)


def test__pull_request__errors_with_unknown_remote(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_remote_url",
        lambda: "git@unsupported.com:owner/repository",
    )
    monkeypatch.setattr(
        _git,
        "get_current_branch_name",
        lambda: "feature-branch",
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == "error: remote code forge not supported: https://unsupported.com/owner/repository\n"
