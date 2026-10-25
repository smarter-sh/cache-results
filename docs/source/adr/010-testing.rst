ADR-010: Testing
================

Status
------
Accepted

Context
-------
The package must behave the same on every supported Django and Python version,
and on every kind of cache backend, without services beyond an optional
cache server.

Decision
--------
Tests use pytest with pytest-django, as ``django.test.SimpleTestCase``\ s
without a database, one test module per source module. ``tests/settings.py``
uses Django's local-memory cache, or Redis through django-redis when
``CACHE_RESULTS_TEST_REDIS_URL`` is set. CI runs them on each supported pair of
Python and Django versions, and against Redis. Coverage must stay at 95% or
more, with branch coverage.

Alternatives Considered
-----------------------
- Django's own test runner, which is less convenient for running one test or a version matrix.
- Mocking the cache, which hides the differences between backends.

Consequences
------------
- **Positive:**

  - Tests run in seconds, on the host, with no services except an optional Redis.
  - Version and backend differences surface in CI, not in users' projects.

- **Negative:**

  - The matrix multiplies CI time.
  - Behavior specific to other backends, such as Memcached, isn't tested.

Related ADRs
------------
- `Smarter ADR-013: Testing <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/013-testing.rst>`__
- :doc:`ADR-011: CI/CD <011-ci-cd>`
