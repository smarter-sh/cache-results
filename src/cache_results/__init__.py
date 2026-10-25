"""
A Django decorator that caches a function's results by its arguments.

.. code-block:: python

    from cache_results import cache_results

    @cache_results(timeout=600)
    def get_book(book_id: int) -> dict:
        return Book.objects.values().get(pk=book_id)

    get_book(42)             # computed and cached
    get_book(42)             # served from the cache
    get_book.invalidate(42)  # clears that entry

See :func:`cache_results.decorators.cache_results` for how it works, and
:mod:`cache_results.conf` for the ``CACHE_RESULTS`` setting.
:data:`lazy_cache` is Django's cache, imported only once Django is ready
(:mod:`cache_results.lazy_cache`). :func:`cache_results.colors.log_prefix` is a
``LOG_PREFIX`` hook that colors log messages by event.
"""

from .__version__ import __version__
from .decorators import cache_results
from .keys import CacheKeyArgumentError, CacheKeyEncoder
from .lazy_cache import LazyCache, lazy_cache

__all__ = ["CacheKeyArgumentError", "CacheKeyEncoder", "LazyCache", "__version__", "cache_results", "lazy_cache"]
