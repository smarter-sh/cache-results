"""
Django's cache, imported only once Django is ready.

Importing ``django.core.cache`` while Django is still starting can leave it on
an unexpected backend, such as a local-memory cache that silently persists
nothing: sessions are lost, and cached results are recomputed in every
process. :data:`lazy_cache` has the api of ``django.core.cache.cache``, and
imports it only on first use, once Django's apps are ready.

.. code-block:: python

    from cache_results import lazy_cache as cache

    cache.set("my_key", "my_value", timeout=300)
    cache.get("my_key")  # "my_value"

On first use it also checks the cache: it writes and reads a test key, and
warns when the ``default`` cache is a local-memory or dummy backend, which is
usually a misconfiguration in production.
"""

import logging

from django.apps import apps

from .conf import cache_results_settings

logger = logging.getLogger(__name__)
LOGGER_PREFIX = f"{__name__}.LazyCache"

_DIAGNOSTIC_KEY = "cache_results.lazy_cache.diagnostic"

_DEFAULT_TIMEOUT = object()
"""The default of every ``timeout``: the cache's own timeout.

``None``, as in Django, means never expire.
"""

_NON_PERSISTENT_BACKENDS = (
    "django.core.cache.backends.locmem.LocMemCache",
    "django.core.cache.backends.dummy.DummyCache",
)
"""Backends that keep nothing across processes, which ``default`` falls back to when misconfigured."""


def _prefix(method: str) -> str:
    """
    Return the formatted start of a log message.

    :param method: The method that logs, e.g. ``cache``.
    :type method: str
    :return: The prefix.
    :rtype: str
    """
    return cache_results_settings.log_prefix(f"{LOGGER_PREFIX}.{method}()")


class LazyCache:
    """
    Django's default cache, imported on first use.

    Use the module's :data:`lazy_cache` instance. Every method passes its
    arguments to the method of the same name of ``django.core.cache.cache``.
    """

    def __init__(self) -> None:
        self._cache = None

    @property
    def ready(self) -> bool:
        """
        Whether the cache can be used yet: True once Django's apps are ready.

        Until then, :attr:`cache` returns ``None`` rather than initialize
        Django's cache prematurely, so callers that may run during startup
        check this first, as ``@cache_results`` does.

        :rtype: bool
        """
        return apps.ready

    @property
    def cache(self):
        """
        Import and return ``django.core.cache.cache``, checking it on first use.

        :return: The cache, or ``None`` before Django's apps are ready.
        :rtype: Optional[django.core.cache.backends.base.BaseCache]
        """
        if self._cache is not None:
            return self._cache
        if not apps.ready:
            logger.warning(
                "%s the cache was used before Django's apps are ready, which can leave it on the wrong backend.",
                _prefix("cache"),
            )
            return None
        # imported here: importing django.core.cache while Django is still starting
        # can leave the cache on the wrong backend.
        from django.core.cache import cache  # pylint: disable=import-outside-toplevel

        self._cache = cache
        self._check(cache)
        return cache

    def _check(self, cache) -> None:
        """
        Write and read a test key, and warn when the cache persists nothing.

        :param cache: The cache.
        :type cache: django.core.cache.backends.base.BaseCache
        """
        try:
            cache.set(_DIAGNOSTIC_KEY, "ready", timeout=5)
            if cache.get(_DIAGNOSTIC_KEY) == "ready":
                logger.debug("%s the cache is ready.", _prefix("cache"))
            else:
                logger.error("%s the cache did not return a test value that was just written.", _prefix("cache"))
        except Exception as e:  # pylint: disable=broad-except
            logger.error("%s the cache could not be read or written: %s", _prefix("cache"), e)

        backend = f"{type(cache).__module__}.{type(cache).__qualname__}"
        if backend in _NON_PERSISTENT_BACKENDS:
            logger.warning(
                "%s the default cache is %s, which persists nothing across processes.", _prefix("cache"), backend
            )

    def get(self, key, default=None, version=None):
        """Fetch a key, or ``default`` if it is not cached."""
        return self.cache.get(key, default, version=version)

    def set(self, key, value, timeout=_DEFAULT_TIMEOUT, version=None):
        """Set a value.

        Without ``timeout``, the cache's own timeout is used, and ``None`` never expires.
        """
        if timeout is _DEFAULT_TIMEOUT:
            return self.cache.set(key, value, version=version)
        return self.cache.set(key, value, timeout=timeout, version=version)

    def add(self, key, value, timeout=_DEFAULT_TIMEOUT, version=None) -> bool:
        """Set a value only if the key is not cached yet."""
        if timeout is _DEFAULT_TIMEOUT:
            return self.cache.add(key, value, version=version)
        return self.cache.add(key, value, timeout=timeout, version=version)

    def touch(self, key, timeout=_DEFAULT_TIMEOUT, version=None) -> bool:
        """Give a key a new timeout."""
        if timeout is _DEFAULT_TIMEOUT:
            return self.cache.touch(key, version=version)
        return self.cache.touch(key, timeout=timeout, version=version)

    def delete(self, key, version=None) -> bool:
        """Delete a key."""
        return self.cache.delete(key, version=version)

    def has_key(self, key, version=None) -> bool:
        """Whether a key is cached."""
        return self.cache.has_key(key, version=version)

    def incr(self, key, delta: int = 1, version=None) -> int:
        """Add ``delta`` to a cached number."""
        return self.cache.incr(key, delta, version=version)

    def decr(self, key, delta: int = 1, version=None) -> int:
        """Subtract ``delta`` from a cached number."""
        return self.cache.decr(key, delta, version=version)

    def get_many(self, keys, version=None) -> dict:
        """Fetch several keys, as a dict of those that are cached."""
        return self.cache.get_many(keys, version=version)

    def set_many(self, data: dict, timeout=_DEFAULT_TIMEOUT, version=None) -> list | None:
        """Set several values.

        Returns what the backend does: Django's own backends, the keys that could not be set.
        """
        if timeout is _DEFAULT_TIMEOUT:
            return self.cache.set_many(data, version=version)
        return self.cache.set_many(data, timeout=timeout, version=version)

    def delete_many(self, keys, version=None) -> None:
        """Delete several keys."""
        return self.cache.delete_many(keys, version=version)

    def incr_version(self, key, delta: int = 1, version=None) -> int:
        """Move a key to a higher version."""
        return self.cache.incr_version(key, delta, version=version)

    def decr_version(self, key, delta: int = 1, version=None) -> int:
        """Move a key to a lower version."""
        return self.cache.decr_version(key, delta, version=version)

    def clear(self) -> None:
        """Delete every key in the cache, not only those of this application."""
        return self.cache.clear()

    def close(self, **kwargs) -> None:
        """Close the connection to the cache."""
        return self.cache.close(**kwargs)


lazy_cache = LazyCache()
"""Django's default cache, imported on first use, with the api of ``django.core.cache.cache``."""


__all__ = ["LazyCache", "lazy_cache"]
