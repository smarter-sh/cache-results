Quickstart
==========

Decorate a function
-------------------

Decorate a function whose result is expensive to compute, and depends only on
its arguments:

.. code-block:: python

    from cache_results import cache_results

    from .models import Book


    @cache_results(timeout=3600)
    def get_book_summary(book_id: int) -> dict:
        book = Book.objects.select_related("author").get(pk=book_id)
        return {"title": book.title, "author": book.author.name}

The first call with an id runs the function and caches its result for an hour.
Later calls with the same id return the cached result, from every process that
shares the cache, until it expires.

Pass plain values
-----------------

The arguments are the cache key, so pass plain values, such as an id, rather
than objects:

.. code-block:: python

    get_book_summary(book.pk)   # yes
    get_book_summary(book)      # runs uncached, and logs an error

See :doc:`guide/arguments` for every type that can be part of a key.

Clear an entry when the data changes
------------------------------------

Call the function's ``invalidate()`` with the same arguments, e.g. when the
book is saved:

.. code-block:: python

    from django.db.models.signals import post_save
    from django.dispatch import receiver


    @receiver(post_save, sender=Book)
    def book_saved(sender, instance, **kwargs):
        get_book_summary.invalidate(instance.pk)

Choose the timeout
------------------

``timeout`` is in seconds. Leave it out to use the ``TIMEOUT`` setting, or your
cache's own timeout when that isn't set. ``0`` caches nothing:

.. code-block:: python

    @cache_results()            # the default timeout
    def get_exchange_rates() -> dict: ...


    @cache_results(timeout=60)  # one minute
    def get_weather(city: str) -> dict: ...

Next, the :doc:`guide/arguments`.
