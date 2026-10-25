import textwrap

import pytest

from git_plugins import _git
from git_plugins.squash_summary import main

# TODO: Instead of mocking, can we do operations in a totally new git directory?

def test__squash_summary__commits_can_be_combined_into_a_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
):
    monkeypatch.setattr(
        _git,
        "get_commits_on_branch",
        lambda _: textwrap.dedent(
            """\
            feat: first commit
            fix: second commit
            docs: third commit
            """
        ),
    )

    rc = main([])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out == textwrap.dedent(
        """\
        - feat: first commit
        - fix: second commit
        - docs: third commit
        """
    )
