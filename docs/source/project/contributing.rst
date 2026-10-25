Contributing
============

Bug reports, questions and pull requests are welcome. Please
`open an issue <https://github.com/smarter-sh/cache-results/issues>`__ before
starting on a larger change, so that we can agree on its design first.

Development setup
-----------------

.. code-block:: console

    $ git clone https://github.com/smarter-sh/cache-results.git
    $ cd cache-results
    $ make init

``make init`` creates the repository's own virtual environment, ``venv/``,
from the pinned ``requirements/local.txt``, installs the package in editable
mode, and installs the pre-commit hooks. ``make`` alone lists every command.

.. code-block:: console

    $ make test             # the tests, against the local-memory cache
    $ make test-redis       # the tests, against Redis (REDIS_URL)
    $ make coverage         # with a coverage report: at least 95%
    $ make typecheck        # mypy, with django-stubs
    $ make lint             # the pre-commit hooks, on every file
    $ make sphinx-build     # these docs, with warnings as errors

Pull requests
-------------

1. Fork the repository, and branch from ``main``.
2. Make your change with its tests. ``make coverage`` must stay at 95% or
   more, and both ``make test`` and ``make test-redis`` must pass. CI checks
   all of this, on every supported Python and Django version.
3. Update the docs and docstrings for anything a user can see.
4. Write `conventional commits <https://www.conventionalcommits.org/>`__,
   e.g. ``fix(keys): sort frozensets of tuples``. Releases are versioned from
   them: ``fix`` makes a patch release, ``feat`` a minor one.
5. Open a pull request that says what changed and why, and links its issue.

A few rules keep cached results safe and readable. They are explained in the
:doc:`../adr`:

- The package depends only on Django and asgiref. Project-specific behavior
  belongs in a project's own hooks, named by the ``CACHE_RESULTS`` setting.
- Arguments are never keyed by ``str()``, and results and secrets are never
  logged.
- A change to the key format, or to the value stored for ``None``, makes every
  cached entry unreadable, so it needs a major release.

Code of conduct
---------------

Everyone who takes part is expected to follow the
`code of conduct <https://github.com/smarter-sh/cache-results/blob/main/CODE_OF_CONDUCT.md>`__.
Governance of the Smarter projects is described in
`smarter-sh/community <https://github.com/smarter-sh/community>`__.
