"""
The cache that holds cached results.

By default it is a cache of the project's ``CACHES`` setting, named by
``CACHE_RESULTS["CACHE_ALIAS"]``. ``CACHE_RESULTS["CACHE"]`` gives the package a
cache of its own instead, configured like an entry of ``CACHES``, e.g. with its
own Redis url, credentials and key prefix:

.. code-block:: python

    CACHE_RESULTS = {
        "CACHE": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://results-user:password@redis:6379/1",
            "KEY_PREFIX": "results",
        },
    }

The project's own caches are then left as they are. A process whose Redis user
may not touch the project's cache, for instance one that runs untrusted code,
can cache results in keys of its own, with a user of its own.

The first time a process uses the cache, it writes and reads a test key in it,
and logs an error if it can't: then every cached function would run uncached.
That check is made once per process for each cache, synchronously, also when an
``async`` function is the first to use it.
"""

import hashlib
import json
import logging
import threading
from collections.abc import Mapping
from typing import TYPE_CHECKING

from django.utils.module_loading import import_string

from .conf import cache_results_settings

if TYPE_CHECKING:
    # only for annotations: importing django.core.cache at runtime, before Django is
    # ready, can leave its caches on the wrong backend.
    from django.core.cache.backends.base import BaseCache

logger = logging.getLogger(__name__)
LOGGER_PREFIX = f"{__name__}.results_cache()"
"""The unformatted start of every log message.

``CACHE_RESULTS["LOG_PREFIX"]`` formats it.
"""

CHECK_KEY = "cache_results.backend.check"
"""The key that the first use of a cache writes and reads back.

The backend adds its own ``KEY_PREFIX``.
"""

CHECK_TIMEOUT = 5
"""Seconds that the test key lives."""

# each thread builds its own backend, as Django's CACHES handler does: a backend
# isn't promised to be thread-safe. (config, backend, identity) of the thread's last build.
_local = threading.local()

# the caches that have been checked in this process, by identity: "alias:<name>",
# or a hash of an own cache's configuration, which holds a password.
_checked: set[str] = set()
_checked_guard = threading.Lock()


def _prefix() -> str:
    """
    Return the formatted start of a log message.

    :return: The prefix.
    :rtype: str
    """
    return cache_results_settings.log_prefix(LOGGER_PREFIX)


def create_cache(config: Mapping[str, object]) -> "BaseCache":
    """
    Build a cache backend from a configuration like an entry of Django's ``CACHES`` setting.

    As Django's own ``CacheHandler.create_connection()`` does: ``BACKEND`` is the
    class's dotted path, ``LOCATION`` its location, and every other entry its params.

    :param config: The configuration, e.g. ``{"BACKEND": "...RedisCache", "LOCATION": "redis://..."}``.
    :type config: Mapping[str, object]
    :return: The backend.
    :rtype: django.core.cache.backends.base.BaseCache
    :raises django.core.exceptions.ImproperlyConfigured: If ``BACKEND`` can't be imported.
    """
    params = dict(config)
    backend_path = str(params.pop("BACKEND"))
    location = params.pop("LOCATION", "")
    backend_class = import_string(backend_path)
    backend: "BaseCache" = backend_class(location, params)
    return backend


def _config_identity(config: Mapping[str, object]) -> str:
    """
    Return a name for an own cache's configuration that holds none of it, e.g. its password.

    :param config: The configuration.
    :type config: Mapping[str, object]
    :return: ``"own:"`` and a hash of the configuration.
    :rtype: str
    """
    text = json.dumps(config, sort_keys=True, default=str)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"own:{digest}"


def _own_cache(config: Mapping[str, object]) -> tuple["BaseCache", str]:
    """
    Return this thread's backend for an own cache, built on first use, and again when the setting changes.

    :param config: ``CACHE_RESULTS["CACHE"]``.
    :type config: Mapping[str, object]
    :return: The backend, and the configuration's identity, for :func:`check_once`.
    :rtype: tuple[django.core.cache.backends.base.BaseCache, str]
    """
    built = getattr(_local, "own_cache", None)
    if built is not None and built[0] is config:
        return built[1], built[2]
    backend = create_cache(config)
    identity = _config_identity(config)
    _local.own_cache = (config, backend, identity)
    return backend, identity


def check_cache(cache: "BaseCache") -> bool:
    """
    Write and read a test key in a cache, and log an error if it can't be done.

    :param cache: The cache.
    :type cache: django.core.cache.backends.base.BaseCache
    :return: True if the test value was read back.
    :rtype: bool
    """
    try:
        cache.set(CHECK_KEY, "ready", timeout=CHECK_TIMEOUT)
        value = cache.get(CHECK_KEY)
        cache.delete(CHECK_KEY)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # only the exception's class: its message can name the cache's host.
        logger.error(
            "%s the cache of cached results can't be read or written (%s): every cached function runs uncached.",
            _prefix(),
            type(e).__name__,
        )
        return False
    if value != "ready":
        logger.error(
            "%s the cache of cached results didn't return a test value that was just written: it persists nothing.",
            _prefix(),
        )
        return False
    logger.debug("%s the cache of cached results is ready.", _prefix())
    return True


def check_once(cache: "BaseCache", identity: str) -> None:
    """
    Check a cache with :func:`check_cache`, the first time this process uses it.

    :param cache: The cache.
    :type cache: django.core.cache.backends.base.BaseCache
    :param identity: The cache's name in this process, e.g. ``"alias:default"``.
    :type identity: str
    """
    with _checked_guard:
        if identity in _checked:
            return
        _checked.add(identity)
    check_cache(cache)


def results_cache() -> "BaseCache":
    """
    Return the cache that holds cached results: ``CACHE_RESULTS["CACHE"]``, or the ``CACHES`` alias ``CACHE_ALIAS``.

    Call it only once Django's apps are ready. The first use of each cache in a
    process checks it (:func:`check_once`).

    :return: The cache.
    :rtype: django.core.cache.backends.base.BaseCache
    """
    config = cache_results_settings.cache
    if config is not None:
        cache, identity = _own_cache(config)
    else:
        from django.core.cache import caches  # pylint: disable=import-outside-toplevel

        alias = cache_results_settings.cache_alias
        cache = caches[alias]
        identity = f"alias:{alias}"
    check_once(cache, identity)
    return cache


__all__ = ["CHECK_KEY", "check_cache", "check_once", "create_cache", "results_cache"]
