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

On first use it warns when the ``default`` cache is a local-memory or dummy
backend, which is usually a misconfiguration in production. It writes nothing
to check it: the project's cache may be one that this process may only read.
The cache of cached results is checked instead, where ``@cache_results`` uses
it (:mod:`cache_results.backend`).
"""

import enum
import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from django.apps import apps
from django.core.exceptions import AppRegistryNotReady

from .conf import cache_results_settings

if TYPE_CHECKING:
    # only for annotations: importing django.core.cache at runtime, before Django is
    # ready, can leave its caches on the wrong backend.
    from django.core.cache.backends.base import BaseCache

logger = logging.getLogger(__name__)
LOGGER_PREFIX = f"{__name__}.LazyCache"


class _DefaultTimeout(enum.Enum):
    """
    The marker of a ``timeout`` that wasn't given, so that the cache's own is used.

    A one-member enum rather than a bare ``object()``: an ``is`` test narrows it
    away, so type checkers see the ``float | None`` that Django's methods take.
    """

    CACHE_DEFAULT = "cache default"


_DEFAULT_TIMEOUT = _DefaultTimeout.CACHE_DEFAULT
"""The default of every ``timeout``: the cache's own timeout.

``None``, as in Django, means never expire.
"""

Timeout = float | None | _DefaultTimeout
"""A ``timeout`` argument: seconds, ``None`` to never expire, or the cache's own when not given."""

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
    arguments to the method of the same name of ``django.core.cache.cache``,
    and raises ``AppRegistryNotReady`` if it is called before Django's apps are
    ready.
    """

    def __init__(self) -> None:
        self._cache: BaseCache | None = None

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
    def cache(self) -> "BaseCache | None":
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

    def _ready_cache(self) -> "BaseCache":
        """
        Return :attr:`cache`, for a method that uses it.

        :return: The cache.
        :rtype: django.core.cache.backends.base.BaseCache
        :raises AppRegistryNotReady: If Django's apps aren't ready yet, so that there is no cache to use.
        """
        cache = self.cache
        if cache is None:
            raise AppRegistryNotReady("lazy_cache was used before Django's apps are ready.")
        return cache

    def _check(self, cache: "BaseCache") -> None:
        """
        Warn when the cache persists nothing.

        :param cache: The cache.
        :type cache: django.core.cache.backends.base.BaseCache
        """
        backend = f"{type(cache).__module__}.{type(cache).__qualname__}"
        if backend in _NON_PERSISTENT_BACKENDS:
            logger.warning(
                "%s the default cache is %s, which persists nothing across processes.", _prefix("cache"), backend
            )

    # the cached values are whatever the project stores: Any, as in Django's own cache api.
    def get(self, key: str, default: Any = None, version: int | None = None) -> Any:
        """Fetch a key, or ``default`` if it is not cached."""
        cache = self._ready_cache()
        return cache.get(key, default, version=version)

    def set(self, key: str, value: Any, timeout: Timeout = _DEFAULT_TIMEOUT, version: int | None = None) -> None:
        """Set a value.

        Without ``timeout``, the cache's own timeout is used, and ``None`` never expires.
        """
        cache = self._ready_cache()
        if timeout is _DEFAULT_TIMEOUT:
            cache.set(key, value, version=version)
        else:
            cache.set(key, value, timeout=timeout, version=version)

    def add(self, key: str, value: Any, timeout: Timeout = _DEFAULT_TIMEOUT, version: int | None = None) -> bool:
        """Set a value only if the key is not cached yet."""
        cache = self._ready_cache()
        if timeout is _DEFAULT_TIMEOUT:
            return cache.add(key, value, version=version)
        return cache.add(key, value, timeout=timeout, version=version)

    def touch(self, key: str, timeout: Timeout = _DEFAULT_TIMEOUT, version: int | None = None) -> bool:
        """Give a key a new timeout."""
        cache = self._ready_cache()
        if timeout is _DEFAULT_TIMEOUT:
            return cache.touch(key, version=version)
        return cache.touch(key, timeout=timeout, version=version)

    def delete(self, key: str, version: int | None = None) -> bool:
        """Delete a key."""
        cache = self._ready_cache()
        return cache.delete(key, version=version)

    def has_key(self, key: str, version: int | None = None) -> bool:
        """Whether a key is cached."""
        cache = self._ready_cache()
        return cache.has_key(key, version=version)

    def incr(self, key: str, delta: int = 1, version: int | None = None) -> int:
        """Add ``delta`` to a cached number."""
        cache = self._ready_cache()
        return cache.incr(key, delta, version=version)

    def decr(self, key: str, delta: int = 1, version: int | None = None) -> int:
        """Subtract ``delta`` from a cached number."""
        cache = self._ready_cache()
        return cache.decr(key, delta, version=version)

    def get_many(self, keys: Iterable[str], version: int | None = None) -> dict[str, Any]:
        """Fetch several keys, as a dict of those that are cached."""
        cache = self._ready_cache()
        return cache.get_many(keys, version=version)

    def set_many(
        self, data: dict[str, Any], timeout: Timeout = _DEFAULT_TIMEOUT, version: int | None = None
    ) -> list[str]:
        """Set several values.

        Returns what the backend does: Django's own backends, the keys that could not be set.
        """
        cache = self._ready_cache()
        if timeout is _DEFAULT_TIMEOUT:
            return cache.set_many(data, version=version)
        return cache.set_many(data, timeout=timeout, version=version)

    def delete_many(self, keys: Iterable[str], version: int | None = None) -> None:
        """Delete several keys."""
        cache = self._ready_cache()
        cache.delete_many(keys, version=version)

    def incr_version(self, key: str, delta: int = 1, version: int | None = None) -> int:
        """Move a key to a higher version."""
        cache = self._ready_cache()
        return cache.incr_version(key, delta, version=version)

    def decr_version(self, key: str, delta: int = 1, version: int | None = None) -> int:
        """Move a key to a lower version."""
        cache = self._ready_cache()
        return cache.decr_version(key, delta, version=version)

    def clear(self) -> None:
        """Delete every key in the cache, not only those of this application."""
        cache = self._ready_cache()
        cache.clear()

    def close(self, **kwargs: Any) -> None:
        """Close the connection to the cache."""
        cache = self._ready_cache()
        cache.close(**kwargs)


lazy_cache = LazyCache()
"""Django's default cache, imported on first use, with the api of ``django.core.cache.cache``."""


__all__ = ["LazyCache", "lazy_cache"]
