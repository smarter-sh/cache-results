ADR-020: Lazy Cache and Colored Log Prefixes
============================================

Status
------
Accepted

Context
-------
Smarter, where the package began, kept three more things beside the
decorator: ``lazy_cache``, a wrapper that imports Django's cache only once
Django is ready; a ``LOG_PREFIX`` hook that colors log messages by event; and
two hooks that need other libraries, a ``KEY_ENCODER`` that accepts Pydantic
models and a ``LOGGING_ENABLED`` that reads a django-waffle switch. Any Django
project that caches needs the first two. The last two need Pydantic and
django-waffle.

Decision
--------
The package provides :data:`~cache_results.lazy.lazy_cache` and
:func:`cache_results.colors.log_prefix`, which depend only on Django.
Hooks that need another library stay in the project that uses that library,
and are named by the project's ``CACHE_RESULTS`` setting, as Smarter's
``smarter/lib/cache/hooks.py`` is. The package has no optional extras for
them.

``lazy_cache`` keeps Django's api exactly, timeouts included: without
``timeout`` the cache's own is used, and ``None`` never expires. On first use
it checks the cache, and warns about a local-memory or dummy ``default``
cache rather than require a particular backend.

Alternatives Considered
-----------------------
- Optional extras (``cache-results[pydantic]``, ``cache-results[waffle]``) with
  hooks for each library: every extra is another library to support and test,
  and how a project reads its feature flags is its own business.
- Leaving ``lazy_cache`` in each project: every Django project that caches
  needs the same protection against importing the cache too early.

Consequences
------------
- **Positive:**

  - A project gets the decorator, a safe way to use Django's cache directly,
    and colored logs, from one package with no new dependencies.
  - The line between the package and a project is simple: anything that needs
    another library is the project's hook.

- **Negative:**

  - A project that uses Pydantic arguments or a feature flag writes a few lines
    of its own hooks.

Related ADRs
------------
- :doc:`ADR-001: A Standalone Package <001-standalone-package>`
- :doc:`ADR-004: Settings and Hooks <004-settings-and-hooks>`
- :doc:`ADR-005: Django Startup <005-django-startup>`
- :doc:`ADR-007: Logging <007-logging>`
