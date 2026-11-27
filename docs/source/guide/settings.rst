Settings
========

cache-results is configured by one optional Django setting, ``CACHE_RESULTS``,
a dict. Every entry is optional, and an empty or missing setting means the
defaults below.

.. code-block:: python

    # settings.py
    CACHE_RESULTS = {
        "CACHE_ALIAS": "default",
        "CACHE": None,
        "TIMEOUT": 3600,
        "KEY_PREFIX": "",
        "VERSION": None,
        "KEY_ENCODER": "cache_results.keys.CacheKeyEncoder",
        "LOGGING_ENABLED": None,
        "VERBOSE_LOGGING": None,
        "LOG_PREFIX": None,
        "LOG_COLORS": None,
    }

The setting is read on every call, so
:func:`~django.test.override_settings` works in tests, and changes made by a
settings reload take effect at once.

Entries
-------

``CACHE_ALIAS``
    The name, in your ``CACHES`` setting, of the cache that holds cached results.
    Default: ``"default"``. A cache of their own lets you clear cached results
    without clearing sessions or anything else.

``CACHE``
    A cache of the package's own, configured like an entry of ``CACHES``:
    ``BACKEND``, ``LOCATION``, ``KEY_PREFIX``, ``OPTIONS`` and the rest. When it
    is set, cached results go there, and ``CACHE_ALIAS`` is not used. Default:
    none. It gives the decorator a connection of its own, e.g. a Redis user
    that may read and write only the keys under its ``KEY_PREFIX``, in a process
    whose own Redis user may not write the project's cache. Each thread builds
    its own backend from it, as Django does for ``CACHES``. Anything else than a
    mapping with a ``BACKEND`` raises ``TypeError``. The
    ``CACHE_RESULTS_CACHE`` environment variable, when it is set, wins over it
    (see below).

    .. code-block:: python

        CACHE_RESULTS = {
            "CACHE": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://results-user:password@redis:6379/1",
                "KEY_PREFIX": "results",
            },
        }

    Whichever cache holds cached results, the first time a process uses it,
    it writes and reads a test key there, and logs an error if it can't: every
    cached function would then run uncached. See :mod:`cache_results.backend`.

The ``CACHE_RESULTS_CACHE`` environment variable
------------------------------------------------

The same configuration as ``CACHE``, as a JSON object, from the environment. It
wins over ``CACHE``, so that a deployment can give one process a cache of its
own, e.g. a worker whose Redis user may not write the project's cache, without
a change to the project's settings: the other processes, which don't set it,
keep caching where they always have.

.. code-block:: console

    CACHE_RESULTS_CACHE='{"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": "redis://results-user:password@redis:6379/1", "KEY_PREFIX": "results"}'

Empty or unset, it is ignored. A value that isn't a JSON object with a
``BACKEND`` raises ``ImproperlyConfigured``, whose message names the variable,
never its value, which holds the cache's credentials: keep it in a secret, e.g.
a Kubernetes Secret, rather than in a plain manifest. It is parsed once per
value.

``TIMEOUT``
    The timeout, in seconds, of a decorated function that names none. Default:
    the cache's own ``TIMEOUT`` (300 seconds unless you set it in ``CACHES``).
    A decorator's own ``timeout`` always wins.

``KEY_PREFIX``
    Text that starts every key. Default: none.

``VERSION``
    When set, ``v<VERSION>:`` follows the prefix in every key. Change it, or
    ``KEY_PREFIX``, to make every cached result a miss at once. Default: none.

``KEY_ENCODER``
    A subclass of :class:`~cache_results.keys.CacheKeyEncoder`, which allows
    more argument types. See :doc:`arguments`. Default: ``CacheKeyEncoder``.
    Anything that isn't a subclass of it raises ``TypeError``, so that a
    misconfiguration can't make unsafe keys.

``LOGGING_ENABLED``
    A callable without arguments that returns whether to log every cache hit,
    miss and invalidation at ``INFO``, or a plain ``True``/``False``. Default:
    off. See :doc:`logging`.

``VERBOSE_LOGGING``
    The same, for whether those messages include the arguments. Default: off.

``LOG_PREFIX``
    A callable ``(text, event)`` that formats the start of each log message,
    where ``event`` is ``"hit"``, ``"miss"``, ``"invalidate"`` or ``""``.
    Default: the text unchanged. :func:`cache_results.colors.log_prefix`
    colors it by event. See :doc:`logging`.

``LOG_COLORS``
    A dict from event to ANSI code, for :func:`cache_results.colors.log_prefix`.
    Default: green hits, red misses, gray invalidations, bold red otherwise.

Callables and classes are given as dotted paths (``"myapp.cache.logging_on"``),
imported once, or as the objects themselves.

Decorator options
-----------------

.. code-block:: python

    @cache_results(timeout=None, cache_key=None, logging_enabled=False)

``timeout``
    Seconds. ``None`` uses the ``TIMEOUT`` setting. ``0`` caches nothing.

``cache_key``
    A fixed key that every call shares, whatever its arguments. See
    :doc:`arguments`.

``logging_enabled``
    Log this function's hits, misses and invalidations at ``INFO``, even when
    ``LOGGING_ENABLED`` is off.
