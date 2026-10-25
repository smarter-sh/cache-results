ADR-012: Semantic Versioning
============================

Status
------
Accepted

Context
-------
Users decide whether an upgrade is safe from its version number, which must
therefore follow the changes, and the changelog must say what they were.

Decision
--------
Versions are semantic, and computed by semantic-release from the conventional
commit messages since the last tag: ``fix`` and ``perf`` make a patch release,
``feat`` a minor one, a ``BREAKING CHANGE:`` footer a major one.
``release.config.js`` writes the version into ``src/cache_results/__version__.py``,
which ``pyproject.toml`` reads, updates ``CHANGELOG.md``, commits both, tags
``v<version>``, and publishes a GitHub release. ``alpha`` and ``beta`` make
prereleases. Commit messages are checked by commitlint at commit time.

Alternatives Considered
-----------------------
- Bump versions by hand.
- Read the version from git tags at build time, which leaves the source without its version.

Consequences
------------
- **Positive:**

  - The version and changelog can't drift from the commits.
  - Contributors learn one convention, which commitlint checks before each commit.

- **Negative:**

  - A mislabeled commit type makes a wrong release, so types must be chosen carefully.

Related ADRs
------------
- `Smarter ADR-020: Semantic Versioning <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/020-semantic-versioning.rst>`__
- :doc:`ADR-009: Compatibility <009-compatibility>`
