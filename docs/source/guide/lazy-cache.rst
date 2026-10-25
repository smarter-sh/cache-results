Lazy Cache
==========

For raw ``get()`` and ``set()``, use :data:`~cache_results.lazy.lazy_cache`
in place of ``django.core.cache.cache``:

.. code-block:: python

    from cache_results import lazy_cache as cache

    cache.set("my_key", "my_value", timeout=300)
    cache.get("my_key")  # "my_value"

It has the api of Django's cache, and the same timeouts: without ``timeout``
the cache's own ``TIMEOUT`` is used, ``None`` never expires, and ``0`` stores
nothing.

Why not import django.core.cache?
---------------------------------

Importing ``django.core.cache`` while Django is still starting, e.g. from a
module that a settings file or an app's ``models.py`` imports, can leave it on
an unexpected backend, such as a local-memory cache. Nothing fails: values are
stored, but only in that process, and are lost on every restart. Sessions
stored in the cache are lost, and cached results are recomputed by every
server.

``lazy_cache`` imports Django's cache only on first use. Before Django's apps
are ready, :attr:`~cache_results.lazy.LazyCache.cache` is ``None`` and a
warning is logged. Code that may run during startup checks
:attr:`~cache_results.lazy.LazyCache.ready` first, as ``@cache_results``
does.

Checks on first use
-------------------

On first use, ``lazy_cache`` writes and reads a test key, and logs an error if
the cache can't be read or written. It warns when the ``default`` cache is a
local-memory or dummy backend, which keep nothing across processes and are
usually a misconfiguration in production. Its messages go to the
``cache_results.lazy`` logger, formatted by ``LOG_PREFIX``.
