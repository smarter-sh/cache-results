ADR-004: Settings and Hooks: One Django Setting
===============================================

Status
------
Accepted

Context
-------
A package installed into any Django project has only Django's settings to
rely on, and must let each project adapt it: the cache to use, the default
timeout, how to log, which argument types are allowed.

Decision
--------
Everything is configured by one Django setting, ``CACHE_RESULTS``, a dict whose
entries are all optional: ``CACHE_ALIAS``, ``TIMEOUT``, ``KEY_PREFIX``,
``VERSION``, ``KEY_ENCODER``, ``LOGGING_ENABLED``, ``VERBOSE_LOGGING`` and
``LOG_PREFIX``. Callables and classes are given as dotted paths or as objects.
The setting is read on every call, through ``cache_results_settings``, so
``override_settings`` works. Behavior that a project wants to change is a hook,
not a dependency.

Alternatives Considered
-----------------------
- Several top-level settings (``CACHE_RESULTS_TIMEOUT``, ...), which crowd a project's settings.
- A Pydantic settings model, which would add a dependency.
- Reading the setting once at import, which breaks ``override_settings`` and can run before settings are configured.

Consequences
------------
- **Positive:**

  - One place to read, one place to document, and every entry has a default.
  - A project's feature flags, log formatting or extra argument types plug in as hooks, without becoming dependencies.

- **Negative:**

  - Reading the setting on every call costs a dict lookup per call.
  - Hooks given as dotted paths fail only when first used, not at startup.

Related ADRs
------------
- `Smarter ADR-007: Settings <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/007-settings.rst>`__
- :doc:`ADR-001: A Standalone Package <001-standalone-package>`
