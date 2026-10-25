ADR-001: A Standalone Package That Depends Only on Django
=========================================================

Status
------
Accepted

Context
-------
``@cache_results`` is useful to any Django project. Every dependency it adds
becomes a dependency of each project that installs it, and behavior specific to
one project can't be part of it.

Decision
--------
cache-results is a standalone package, published to PyPI as ``cache-results``
with the import name ``cache_results``. Its only dependencies are Django and
asgiref. Behavior that a project needs to change is a hook that the project
configures (:doc:`004-settings-and-hooks`).

Alternatives Considered
-----------------------
- Keep the decorator inside one application, and let other projects copy it.
- Depend on a settings, logging or feature-flag library, which every user would then have to install.

Consequences
------------
- **Positive:**

  - Any Django project can use it, alongside its own dependencies.
  - The package is small enough to understand, test and document on its own.

- **Negative:**

  - Project-specific behavior has to go through hooks, which is more work than importing it.

Related ADRs
------------
- `Smarter ADR-018: Caching <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/018-caching.rst>`__
- :doc:`ADR-004: Settings and Hooks <004-settings-and-hooks>`
