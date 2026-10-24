from git_plugins import main


def test__main__happy_path():
    assert main.main() == 0
