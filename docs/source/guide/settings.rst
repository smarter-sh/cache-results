Settings
========

cache-results is configured by one optional Django setting, ``CACHE_RESULTS``,
a dict. Every entry is optional, and an empty or missing setting means the
defaults below.

.. code-block:: python

    # settings.py
    CACHE_RESULTS = {
        "CACHE_ALIAS": "default",
        "TIMEOUT": 3600,
        "KEY_PREFIX": "",
        "VERSION": None,
        "KEY_ENCODER": "cache_results.keys.CacheKeyEncoder",
        "LOGGING_ENABLED": None,
        "VERBOSE_LOGGING": None,
        "LOG_PREFIX": None,
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
    Default: the text unchanged.

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
