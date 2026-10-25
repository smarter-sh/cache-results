ADR-011: CI/CD
==============

Status
------
Accepted

Context
-------
Every change must be linted, tested and buildable before it is released, and
releases must not depend on one person's machine.

Decision
--------
CI/CD uses GitHub Actions. ``ci.yml`` runs on every push and
pull request: the pre-commit hooks, the test matrix and Redis, coverage uploaded
to Codecov, then a build of the sdist and wheel checked with ``twine check
--strict``. ``release.yml`` is started by hand: semantic-release
(:doc:`012-semantic-versioning`), a build from the new tag, and publication to
PyPI with trusted publishing, enabled by the repository variable
``PUBLISH_TO_PYPI``. Every ``make`` target has a CI counterpart.

Alternatives Considered
-----------------------
- Another CI platform.
- Release on every push to main, which makes a release of every merged fix before it can be reviewed together.

Consequences
------------
- **Positive:**

  - One platform for every smarter-sh repository.
  - PyPI is published to without a stored token.

- **Negative:**

  - Releases need someone to start them.

Related ADRs
------------
- `Smarter ADR-014: CI CD <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/014-ci-cd.rst>`__
- :doc:`ADR-012: Semantic Versioning <012-semantic-versioning>`
