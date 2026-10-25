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
"""

from .__version__ import __version__
from .decorators import cache_results
from .keys import CacheKeyArgumentError, CacheKeyEncoder

__all__ = ["CacheKeyArgumentError", "CacheKeyEncoder", "__version__", "cache_results"]
