ADR-022: A Cache of Its Own
===========================

Status
------
Accepted

Context
-------
The decorator stored results in a cache of the project's ``CACHES`` setting,
named by ``CACHE_ALIAS``, and ``lazy_cache`` checked the ``default`` cache on
first use by writing and reading a test key.

Smarter runs untrusted code, Extensions, in workers whose Redis user may read
only a few keys and write none of the project's cache, so that the code can't
read the platform's sessions or plant a crafted value, which Django would
unpickle, where the web servers read. In those workers every cached function
ran uncached, logging a warning on each call, and the first use of
``lazy_cache`` logged an error: the cache's user was restricted on purpose, and
the decorator had no way to use a connection of its own.

Decision
--------
``CACHE_RESULTS["CACHE"]`` gives the package a cache of its own, configured
like an entry of ``CACHES``: its own ``BACKEND``, its own ``LOCATION``, with
its own credentials, its own ``KEY_PREFIX``. When it is set, results go there,
and ``CACHE_ALIAS`` is not used. The package builds the backend itself
(:mod:`cache_results.backend`), as Django's ``CACHES`` handler does: from the
configuration, once per thread, and again when the setting changes.

The test key moves to the cache of cached results: the first time a process
uses it, the package writes and reads a key there, and logs an error if it
can't, since every cached function would then run uncached. ``lazy_cache``
writes nothing on first use: it is the project's cache, which a process may be
allowed only to read. It still warns about a local-memory or dummy backend.

Unset, ``CACHE`` changes nothing: the same cache, the same keys, so no cached
result is lost on upgrade.

Alternatives Considered
-----------------------
- An entry in the project's ``CACHES`` for the decorator: it works, but every
  project would build the package's cache in its own settings, which is the
  package's business.
- Widening the restricted Redis user to the project's cache: the process would
  then reach keys that other processes read, which the restriction exists to
  prevent.
- Turning the test key off where it fails: it would hide that cached functions
  run uncached.

Consequences
------------
- **Positive:**

  - A process can cache results with a connection of its own, as restricted
    as it should be, while its project's caches stay as they are.
  - The first-use check tests the cache that the decorator actually writes.

- **Negative:**

  - A process that sets ``CACHE`` shares cached results only with processes
    that set the same: results cached there aren't seen by the others.
  - The first use of the cache in a process makes one synchronous write and
    read, also when an ``async`` function is the first to use it.

Related ADRs
------------
- :doc:`ADR-004: Settings and Hooks <004-settings-and-hooks>`
- :doc:`ADR-005: Django Startup <005-django-startup>`
- :doc:`ADR-008: Error Handling <008-error-handling>`
- :doc:`ADR-020: Lazy Cache and Colored Log Prefixes <020-lazy-cache-and-colors>`
