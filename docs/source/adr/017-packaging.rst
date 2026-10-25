ADR-017: Packaging
==================

Status
------
Accepted

Context
-------
The package must build reproducibly into an sdist and a wheel for PyPI, with
its version, license and metadata in one place.

Decision
--------
Metadata lives in ``pyproject.toml`` (PEP 621), built by hatchling, with the
code in a ``src/`` layout (``src/cache_results/``) so that tests run against the
installed package rather than the working directory. The package is licensed
under MIT, a permissive license, so that any project can use it.

Alternatives Considered
-----------------------
- A ``setup.py`` that parses ``__version__.py``, an older, imperative style.
- A copyleft license such as AGPL-3.0, which many companies won't use in a library.

Consequences
------------
- **Positive:**

  - Standard, declarative packaging that any modern tool understands.
  - Anyone can use the package, including in closed-source projects.

- **Negative:**

  - Contributions are under MIT, so they can be used in closed-source projects too.

Related ADRs
------------
- :doc:`ADR-001: A Standalone Package <001-standalone-package>`
- :doc:`ADR-013: Dependency Management <013-dependency-management>`
