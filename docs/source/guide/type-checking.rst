Type Checking
=============

The package ships type annotations (``py.typed``), and a decorated function
keeps the parameters and result of the function it decorates. Type checkers
such as mypy and Pyright (Pylance) check its calls, and know its
``invalidate()``:

.. code-block:: python

    @cache_results(timeout=600)
    def get_book(book_id: int) -> dict: ...

    get_book(42)               # dict
    get_book("42")             # flagged: book_id is an int
    get_book.invalidate(42)    # no "# type: ignore" needed
    get_book.invalidate("42")  # flagged, like the call

``invalidate()`` takes the same arguments as the function, because it clears
the entry those arguments cached.

An ``async`` function still returns a coroutine of its result, which you
await, while its ``invalidate()`` is synchronous, as it is at runtime.

A cached classmethod is called without ``cls``, like any classmethod, and its
``invalidate()`` takes the class first
(:doc:`classmethods`):

.. code-block:: python

    Report.totals(2026)                    # dict
    Report.totals.invalidate(Report, 2026)

To annotate a decorated function yourself, e.g. a parameter that receives one,
use :class:`~cache_results.CachedFunction`, generic over the function's
parameters and result:

.. code-block:: python

    from cache_results import CachedFunction

    def clear(lookup: CachedFunction[[int], dict], book_id: int) -> None:
        lookup.invalidate(book_id)
