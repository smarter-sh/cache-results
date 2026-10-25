Changelog
=========

Releases are made by `semantic-release <https://semantic-release.gitbook.io/>`__
from the project's conventional commit messages, which also write
``CHANGELOG.md``. Each release's notes are on its
`GitHub release page <https://github.com/smarter-sh/cache-results/releases>`__.

Versions follow `semantic versioning <https://semver.org/>`__:

- a **patch** release (0.1.1) fixes bugs,
- a **minor** release (0.2.0) adds features, and keeps working code working,
- a **major** release (1.0.0) can break code, or change the format of cache
  keys, which makes every existing cached result a miss once.

See :doc:`../adr/009-compatibility` and :doc:`../adr/012-semantic-versioning`.
