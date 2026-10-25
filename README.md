<span align="center">

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![tests](https://github.com/billwallis/git-plugins/actions/workflows/tests.yaml/badge.svg)](https://github.com/billwallis/git-plugins/actions/workflows/tests.yaml)
[![coverage](https://raw.githubusercontent.com/billwallis/git-plugins/refs/heads/main/coverage.svg)](https://smarie.github.io/python-genbadge/)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/billwallis/git-plugins/main.svg)](https://results.pre-commit.ci/latest/github/billwallis/git-plugins/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/billwallis/git-plugins)](https://shields.io/badges/git-hub-last-commit)

</span>

---

# Git plugins

Plugins for Git.

## Usage

Install the project and expose the scripts to your `PATH`.

For example, with [pipx](https://pipx.pypa.io/stable/):

```shell
pipx install git+https://github.com/billwallis/git-plugins
```

## Contributing

Install the dependencies:

```shell
pip install --editable . --group dev --group test
pre-commit install --install-hooks
```
