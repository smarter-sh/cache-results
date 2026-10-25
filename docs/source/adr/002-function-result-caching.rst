ADR-002: Function Result Caching in Django's Cache Framework
============================================================

Status
------
Accepted

Context
-------
Expensive work, such as a database query or a call to a third-party api, is
often repeated with the same arguments. Projects tend to hand-roll
``cache.get()`` and ``cache.set()`` around it, each with its own key format,
invalidation and handling of ``None``.

Decision
--------
The package offers one decorator, ``@cache_results``, that caches a function's
result by its arguments, in a cache of Django's cache framework, and gives the
function an ``invalidate()`` for the same arguments. ``None`` is cached like any
other result. It caches function results, not objects: there is no model or
queryset caching.

Alternatives Considered
-----------------------
- Object or queryset caching, such as django-cacheops or django-cachalot, which patch the ORM.
- An in-process cache such as ``functools.lru_cache``, which is neither shared between servers nor survives a restart.
- A cache client of its own, rather than Django's cache framework.

Consequences
------------
- **Positive:**

  - Works with every Django cache backend, and shares results across processes and servers with a shared cache such as Redis.
  - One key format and one way to invalidate, instead of one per call site.

- **Negative:**

  - Every call serializes and hashes its arguments and makes a round trip to the cache, so it doesn't suit cheap, short-lived results.
  - The caller decides what to cache and when to invalidate: nothing is invalidated automatically when data changes.

Related ADRs
------------
- `Smarter ADR-018: Caching <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/018-caching.rst>`__
- :doc:`ADR-003: Cache Keys <003-cache-keys>`
