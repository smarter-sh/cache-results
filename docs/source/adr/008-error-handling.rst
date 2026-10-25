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
When a call's arguments can't be keyed, or the cache isn't ready, the function
runs uncached and the reason is logged; the caller sees only its own function's
result or exceptions. Exceptions that the function raises are never cached, so
a failure is retried on the next call. The package's own exceptions subclass
the built-in exception they refine, e.g. ``CacheKeyArgumentError`` is a
``TypeError``. Programming errors are raised at decoration time: decorating an
instance method raises ``TypeError``.

Alternatives Considered
-----------------------
- Raise on an argument that can't be keyed, which turns a performance problem into an outage.
- A package-wide exception hierarchy, which callers would have to learn for little benefit.

Consequences
------------
- **Positive:**

  - The decorator can't break a working function.
  - Code that catches ``TypeError`` also catches the package's errors.

- **Negative:**

  - A function that is silently uncached is only visible in the logs.

Related ADRs
------------
- `Smarter ADR-012: Error Handling <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/012-error-handling.rst>`__
- :doc:`ADR-003: Cache Keys <003-cache-keys>`
