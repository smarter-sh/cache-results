Testing Your Code
=================

Code that calls cached functions needs a little care in tests: a result cached
by one test can be served to the next.

Clear the cache between tests
-----------------------------

Use a local-memory cache in your test settings, and clear it in ``setUp``:

.. code-block:: python

    from django.core.cache import cache
    from django.test import TestCase


    class BookSummaryTests(TestCase):
        def setUp(self):
            cache.clear()

Or invalidate only the entries a test depends on:

.. code-block:: python

    get_book_summary.invalidate(self.book.pk)

Turn caching off
----------------

A timeout of ``0`` caches nothing, so this runs every decorated function that
names no timeout of its own, every time:

.. code-block:: python

    from django.test import override_settings


    @override_settings(CACHE_RESULTS={"TIMEOUT": 0})
    class UncachedTests(TestCase): ...

Call the undecorated function
-----------------------------

The decorator keeps the original function as ``__wrapped__``, to test the
function itself without the cache:

.. code-block:: python

    self.assertEqual(get_book_summary.__wrapped__(self.book.pk), {...})

Prove that a result is cached
-----------------------------

Count the calls of what the function does, e.g. its queries:

.. code-block:: python

    def test_summary_is_cached(self):
        get_book_summary(self.book.pk)
        with self.assertNumQueries(0):
            get_book_summary(self.book.pk)

Find uncached calls
-------------------

A call whose arguments can't be part of a key logs an error once per process,
for each function and reason, then runs uncached quietly. Read your test run's
log for ``runs uncached`` to find calls that pass a model instead of its id.
The message names the function and the argument's type.
