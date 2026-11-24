ADR-008: Error Handling: Degrade to an Uncached Call
====================================================

Status
------
Accepted

Context
-------
A cache is an optimization. A caller that gets an exception from the caching
layer, rather than from its own function, has been made worse off by it.

Decision
--------
When a call's arguments can't be keyed, the cache isn't ready, or the cache
backend raises (e.g. django-redis's ``ConnectionInterrupted`` while Redis is
unreachable), the function runs uncached and the reason is logged; the caller
sees only its own function's result or exceptions. A backend error is logged as
a warning that names the exception's class, never its message, which can name
the cache's host. A read that fails skips the write too, and the per-key lock,
so that a call waits on at most one socket timeout. A failed write still
returns the computed result. A failed ``invalidate()`` is logged and returns:
the entry, if it survives the outage, can be served until its timeout. Exceptions that the function raises are never cached, so
a failure is retried on the next call. The package's own exceptions subclass
the built-in exception they refine, e.g. ``CacheKeyArgumentError`` is a
``TypeError``. Programming errors are raised at decoration time: decorating an
instance method raises ``TypeError``.

Alternatives Considered
-----------------------
- Raise on an argument that can't be keyed, which turns a performance problem into an outage.
- Let cache backend errors reach the caller, which turned every Redis outage into
  an outage of every function that reads through the cache, as it did for
  `Smarter <https://github.com/smarter-sh/smarter/issues/1052>`__.
- Set django-redis's ``IGNORE_EXCEPTIONS``, which works only for django-redis,
  and only for every cache alias that shares the option, e.g. sessions.
- A package-wide exception hierarchy, which callers would have to learn for little benefit.

Consequences
------------
- **Positive:**

  - The decorator can't break a working function.
  - Code that catches ``TypeError`` also catches the package's errors.

- **Negative:**

  - A function that is silently uncached is only visible in the logs.
  - During a cache outage every call runs uncached, so the functions' own load,
    e.g. on the database, rises until the cache is back.
  - A failed ``invalidate()`` doesn't raise, so a caller can't retry it.

Related ADRs
------------
- `Smarter ADR-012: Error Handling <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/012-error-handling.rst>`__
- :doc:`ADR-003: Cache Keys <003-cache-keys>`
