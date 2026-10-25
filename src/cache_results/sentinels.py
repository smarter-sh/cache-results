"""
Sentinel values that let the ``@cache_results`` decorator tell a cached.

``None`` from a cache miss.

- :data:`CACHE_MISS_SENTINEL` is a unique object, passed as the default of a
  cache read. Getting it back means the key is not cached.
- :data:`CACHE_NONE_SENTINEL` is the string that is stored in place of a
  ``None`` result, because many cache backends can't tell a stored ``None``
  from a missing key.

.. code-block:: python

    value = cache.get(key, CACHE_MISS_SENTINEL)
    if value is CACHE_MISS_SENTINEL:
        ...  # not cached
    elif value == CACHE_NONE_SENTINEL:
        value = None  # a cached None
"""


class CacheSentinel:
    """
    A unique, named marker object.

    Two sentinels are never equal unless they are the same object, so one can
    be passed as the default of a cache read without colliding with any
    cached value.

    :param name: The name shown by ``str()`` and ``repr()``.
    :type name: str
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"<CacheSentinel: {self.name}>"

    __str__ = __repr__


CACHE_NONE_SENTINEL = 'CacheSentinel("CACHE_NONE")'
"""The value stored in place of a ``None`` result."""

CACHE_MISS_SENTINEL = CacheSentinel("CACHE_MISS")
"""The default of a cache read, returned only when the key is not cached."""


__all__ = ["CACHE_MISS_SENTINEL", "CACHE_NONE_SENTINEL", "CacheSentinel"]
