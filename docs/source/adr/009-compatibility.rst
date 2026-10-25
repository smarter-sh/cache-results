ADR-009: Compatibility: Cached Entries Outlive Releases
=======================================================

Status
------
Accepted

Context
-------
Cached results live in shared caches such as Redis, often for hours, while
applications are upgraded under them. If a new release built different keys, or
stored ``None`` differently, every existing entry would be missed or misread at
once, and a fleet upgraded gradually would run two formats side by side.

Decision
--------
The key format (``make_key()``, ``normalize()``, and what the encoder produces
for each type it knows) and the stored value of ``None``
(``CACHE_NONE_SENTINEL``) are part of the public interface. Changing either is a
breaking change, released as a new major version with a ``BREAKING CHANGE:``
note, and tests pin both. Supported versions are Django 4.2 and newer, on
Python 3.10 and newer. Dropping a version is also a breaking change.

Alternatives Considered
-----------------------
- Treat keys as an internal detail, and let each release change them.
- Version keys automatically with the package's version, which abandons every entry on every release.

Consequences
------------
- **Positive:**

  - Upgrading the package doesn't empty anyone's cache.
  - Users can tell from the version number when it will.

- **Negative:**

  - Improving the key format waits for a major release.
  - ``KEY_PREFIX`` and ``VERSION`` are the tools for a project that wants to abandon its entries on purpose.

Related ADRs
------------
- :doc:`ADR-003: Cache Keys <003-cache-keys>`
- :doc:`ADR-012: Semantic Versioning <012-semantic-versioning>`
