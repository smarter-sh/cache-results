ADR-016: Code Quality
=====================

Status
------
Accepted

Context
-------
Consistent style and early detection of mistakes make a small codebase easy to
review, and the same tools should run on every machine and in CI.

Decision
--------
Code quality is managed with pre-commit, configured in
``.pre-commit-config.yaml``: black, isort, autoflake, flake8, bandit,
pyupgrade, pydocstringformatter, codespell, Prettier, the standard
pre-commit-hooks, and commitlint for commit messages. ``make init`` installs the
hooks, ``make lint`` runs them on every file, and CI's ``lint`` job runs them
too. flake8 runs all of its checks.
**Don't disable rules indiscriminately with comment directives.**

Alternatives Considered
-----------------------
- Rely on review for style.
- Ruff, which would replace several hooks with one tool, but with rules that differ from theirs.

Consequences
------------
- **Positive:**

  - One standard, enforced before each commit and again in CI.

- **Negative:**

  - Contributors must install the hooks, and the hooks' versions must be updated.

Related ADRs
------------
- `Smarter ADR-028: Code Quality <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/028-code-quality.rst>`__
