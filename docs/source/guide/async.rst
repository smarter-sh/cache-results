Async, Concurrency and Startup
==============================

async functions
---------------

Decorate an ``async def`` function as you would any other. Its result is
cached, not its coroutine:

.. code-block:: python

    @cache_results(timeout=300)
    async def get_forecast(city: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(FORECAST_URL, params={"city": city})
            return response.json()


    forecast = await get_forecast("Lisbon")

The cache is read and written without blocking the event loop. If your cache
backend implements Django's ``aget()`` and ``aset()`` itself, they are used.
Otherwise, the ordinary ``get()`` and ``set()`` run in a worker thread. Django's
default ``aget()`` and ``aset()`` aren't used, because they run every call on
one shared thread. django-redis has no async methods of its own, so with Redis
the worker threads are used.

``invalidate()`` is synchronous for async functions too. From async code, call
it through :func:`asgiref.sync.sync_to_async`.

Concurrent misses
-----------------

When several threads of one process call a function with the same arguments
while the result isn't cached, the first one computes it, and the others wait
for it and read it from the cache, instead of all computing it.

This doesn't extend to other processes or servers, which compute the result
independently, or to async callers, which don't wait.

A function that calls itself with the same arguments doesn't deadlock: the lock
is re-entrant.

During startup
--------------

Decorators are applied when their module is imported, which often happens
while Django is still starting. Touching Django's cache framework that early
can leave it on the wrong backend, so cache-results imports
``django.core.cache`` lazily, and uses the cache only once Django's apps are
ready. A decorated function called before then simply runs uncached.
