Logging
=======

cache-results logs with Python's standard :mod:`logging`, to the
``cache_results.decorators`` logger. Configure it in your ``LOGGING`` setting
like any other.

What is logged
--------------

``ERROR``
    A call whose arguments can't be part of a key, and so runs uncached. It is
    logged once per process for each function and reason, then at ``DEBUG``, so
    that a frequently called function can't flood your logs. See
    :doc:`arguments`.

``INFO``
    Every cache hit, miss and invalidation, when logging is enabled for the
    function: by its decorator's ``logging_enabled=True``, or by the
    ``LOGGING_ENABLED`` setting.

``DEBUG``
    The same events when logging isn't enabled, and calls made before Django is
    ready.

Messages name the function and the **type** of its result, never the result
itself, so that cached data doesn't end up in your logs:

.. code-block:: text

    INFO cache_results.decorators.@cache_results() caching dict for get_book_summary: myapp.books.get_book_summary()_3f0c..., with timeout 3600
    INFO cache_results.decorators.@cache_results() cache hit for get_book_summary: myapp.books.get_book_summary()_3f0c... (dict)

Arguments are added only when ``VERBOSE_LOGGING`` is on. Turn it on only where
arguments can't hold personal data.

Turning logging on at runtime
-----------------------------

``LOGGING_ENABLED`` and ``VERBOSE_LOGGING`` can be callables, called on every
cached call. Point them at a feature flag to switch cache logging on in
production without a redeploy:

.. code-block:: python

    # myapp/cache.py
    from waffle import switch_is_active


    def cache_logging_enabled() -> bool:
        return switch_is_active("cache_logging")

.. code-block:: python

    # settings.py
    CACHE_RESULTS = {"LOGGING_ENABLED": "myapp.cache.cache_logging_enabled"}

The callable may query the database: for ``async`` functions it is called in a
worker thread. Keep it fast, or cache its answer, because it runs on every
call.

Formatting the prefix
---------------------

``LOG_PREFIX`` formats the start of each message. The package's own
:func:`cache_results.colors.log_prefix` colors it by event, for a development
console: hits green, misses red, invalidations gray, and other messages, such
as errors, bold red.

.. code-block:: python

    CACHE_RESULTS = {"LOG_PREFIX": "cache_results.colors.log_prefix"}

``LOG_COLORS`` changes a color, as an ANSI code, or turns one off with
``None``:

.. code-block:: python

    CACHE_RESULTS = {
        "LOG_PREFIX": "cache_results.colors.log_prefix",
        "LOG_COLORS": {"hit": "\033[94m", "": None},
    }

Any other callable ``(text, event)`` works too.
