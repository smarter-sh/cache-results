Invalidation
============

Every decorated function has an ``invalidate()`` method, which deletes the
cached result of the arguments you pass it:

.. code-block:: python

    @cache_results()
    def get_book_summary(book_id: int) -> dict: ...


    get_book_summary.invalidate(42)

The arguments are bound to the signature exactly as a call's are, so
``invalidate(42)``, ``invalidate(book_id=42)`` and a call written either way
all refer to the same entry. Invalidating an entry that isn't cached does
nothing.

When to invalidate
------------------

Invalidate where the data changes, e.g. in a model's ``save()`` or a
``post_save`` receiver, or after a call to the api whose answer you cached:

.. code-block:: python

    @receiver([post_save, post_delete], sender=Book)
    def book_changed(sender, instance, **kwargs):
        get_book_summary.invalidate(instance.pk)

A result that changes on its own, such as an exchange rate, needs no
invalidation: give it a timeout that matches how stale it may be.

Functions with a fixed key
--------------------------

A function decorated with ``cache_key`` is invalidated with no arguments:

.. code-block:: python

    get_countries.invalidate()

Abandoning every entry at once
------------------------------

To make every cached result a miss, e.g. after a deploy that changes what your
functions return, change the ``VERSION`` or ``KEY_PREFIX`` setting. Every key
starts with them, so old entries are never read again, and expire on their own.
Nothing else in the same cache is touched:

.. code-block:: python

    CACHE_RESULTS = {"VERSION": 2}

Or give cached results a cache of their own (``CACHE_ALIAS``), and clear it.

Before Django is ready
----------------------

``invalidate()`` does nothing when it is called before Django's apps are
ready, because nothing can have been cached yet. See :doc:`async` for how calls
behave during startup.
