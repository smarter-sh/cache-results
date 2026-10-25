ADR-005: Django Startup: Cache Only Once Apps Are Ready
=======================================================

Status
------
Accepted

Context
-------
Decorators run when their module is imported, which often happens while Django
is still starting. Touching ``django.core.cache`` then can leave it on an
unexpected backend, such as a local-memory cache that silently persists
nothing, and a decorated function can be called before the cache exists.

Decision
--------
The package initializes Django's cache lazily: it imports ``django.core.cache``
only inside functions, never at module level, and reads or writes the cache
only once Django's apps are ready (``cache_ready()``, which is ``apps.ready``).
A decorated function called earlier runs uncached, and ``invalidate()`` does
nothing.

Alternatives Considered
-----------------------
- Raise an error before apps are ready, which breaks code that runs during startup.
- Import the cache at module level, and document that the package must be imported late.

Consequences
------------
- **Positive:**

  - Importing or calling a decorated function is safe at any point of startup.
  - A project can't accidentally initialize its cache before its settings.

- **Negative:**

  - Calls during startup are never cached.
  - Every call checks ``apps.ready`` first.

Related ADRs
------------
- `Smarter ADR-018: Caching <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/018-caching.rst>`__
