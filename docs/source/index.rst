cache-results |project_version|
===============================

.. image:: https://img.shields.io/badge/a%20project%20of-The%20Smarter%20Project-2F6FEB
   :target: https://smarter.sh
   :alt: A project of The Smarter Project

.. image:: https://github.com/smarter-sh/cache-results/actions/workflows/release.yml/badge.svg?branch=main
   :target: https://github.com/smarter-sh/cache-results/actions/workflows/release.yml
   :alt: Release

.. image:: https://codecov.io/gh/smarter-sh/cache-results/graph/badge.svg
   :target: https://codecov.io/gh/smarter-sh/cache-results
   :alt: Coverage

.. image:: https://img.shields.io/github/v/release/smarter-sh/cache-results?label=release
   :target: https://github.com/smarter-sh/cache-results/releases
   :alt: Latest release

.. image:: https://img.shields.io/pypi/v/cache-results?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/cache-results/
   :alt: PyPI

.. image:: https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white
   :alt: Python 3.10+

.. image:: https://img.shields.io/badge/django-4.2%2B-0C4B33?logo=django&logoColor=white
   :alt: Django 4.2+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/smarter-sh/cache-results/blob/main/LICENSE
   :alt: MIT License

|

**cache-results** is a Django decorator that caches a function's results by its
arguments, in any Django cache, such as Redis.

It is part of `The Smarter Project <https://smarter.sh>`__. It began as the
caching layer of `Smarter <https://github.com/smarter-sh/smarter>`__, an
open-source platform for building and running AI applications with Django,
where it caches database reads and third-party api calls across many
application servers.

.. code-block:: python

    from cache_results import cache_results


    @cache_results(timeout=600)
    def get_book(book_id: int) -> dict:
        return Book.objects.values().get(pk=book_id)


    get_book(42)             # computed and cached
    get_book(42)             # served from the cache
    get_book.invalidate(42)  # clears that entry

Features
--------

- **Safe keys.** The key is the function's module and qualified name, plus a
  hash of its arguments bound to its signature. Arguments that can't be part
  of a safe key run the function uncached, rather than be keyed by ``str()``.
- **None is cached** like any other result.
- **Invalidation**: every decorated function has an ``invalidate()`` that
  clears the entry of the same arguments.
- **async functions** are cached without blocking the event loop.
- **Classmethods** are cached per class. Instance methods are refused.
- **No stampede within a process**: threads that miss the same key wait for
  the first one to compute it.
- **Safe during startup**: a function called before Django's apps are ready
  runs uncached.
- **lazy_cache**: Django's cache, imported only once Django is ready, for
  raw ``get()`` and ``set()``.
- **One setting**, ``CACHE_RESULTS``, configures the cache, the timeout, keys
  and logging.
- **Small**: depends only on Django and asgiref. MIT licensed.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/arguments
   guide/invalidation
   guide/async
   guide/classmethods
   guide/settings
   guide/logging
   guide/lazy-cache
   guide/testing

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference

.. toctree::
   :maxdepth: 1
   :caption: Project

   project/changelog
   project/contributing
   project/license
   adr

Indices
-------

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`
