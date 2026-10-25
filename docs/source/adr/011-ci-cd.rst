ADR-011: CI/CD
==============

Status
------
Accepted. Superseded in part by :doc:`ADR-019 <019-release-on-push>`: releases start on every push.

Context
-------
Every change must be linted, tested and buildable before it is released, and
releases must not depend on one person's machine.

Decision
--------
CI/CD uses GitHub Actions. ``ci.yml`` runs on every push and
pull request: the pre-commit hooks, the test matrix and Redis, coverage uploaded
to Codecov, then a build of the sdist and wheel checked with ``twine check
--strict``. ``release.yml`` is started by hand, and releases and publishes in
one run: the whole of CI, semantic-release (:doc:`012-semantic-versioning`), a
build from the new tag attached to the GitHub release, a rehearsal upload to
TestPyPI that is installed back and checked, then PyPI, from ``main`` only.
Uploads use trusted publishing, with no stored token, and are enabled by the
repository variables ``PUBLISH_TO_TESTPYPI`` and ``PUBLISH_TO_PYPI``. Every
``make`` target has a CI counterpart.

Alternatives Considered
-----------------------
- Another CI platform.
- Release on every push to main, which makes a release of every merged fix before it can be reviewed together.
- Publish to PyPI by hand after the release, which lets a tagged release never reach PyPI.
- Publish with a PyPI API token stored as a secret, which can leak and must be rotated.

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
