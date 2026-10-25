ADR-006: Async Functions and Concurrent Misses
==============================================

Status
------
Accepted

Context
-------
A decorated ``async`` function returns a coroutine: what must be cached is
the result it produces, not the coroutine. Django's ``BaseCache.aget()`` and
``aset()`` are ``sync_to_async(..., thread_sensitive=True)``, which queues every
call on one thread, and django-redis has no native async methods. Separately,
several threads that miss the same key at once would all compute it.

Decision
--------
Coroutine functions get an async wrapper that awaits the function and caches
its result. It uses a backend's own ``aget()``/``aset()`` only when the backend
overrides Django's, and otherwise runs ``get()``/``set()`` in the thread pool
(``thread_sensitive=False``). Logging hooks, which may query a database, run
through ``sync_to_async``. In synchronous code, threads of one process that miss
the same key wait on a per-key re-entrant lock, held in a
``WeakValueDictionary``, and check the cache again before computing.

Alternatives Considered
-----------------------
- Django's default async methods, which serialize all async cache traffic.
- Lock striping, a fixed set of locks, rejected because nested cached calls on different keys could deadlock.
- A distributed lock in the cache, which needs backend support and adds a round trip to every miss.

Consequences
------------
- **Positive:**

  - Async functions are cached without blocking the event loop or queueing behind other synchronous work.
  - A burst of identical misses in one process computes the result once.

- **Negative:**

  - Processes don't wait for each other, and async callers don't wait at all.
  - Thread-pool cache calls rely on the backend being thread-safe, as Django's built-in backends and django-redis are.

Related ADRs
------------
- :doc:`ADR-005: Django Startup <005-django-startup>`
