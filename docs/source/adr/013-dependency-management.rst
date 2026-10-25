ADR-013: Dependency Management
==============================

Status
------
Accepted

Context
-------
A library's dependencies become its users' dependencies, so each one narrows
what they can install. Developers, CI and the docs need many more tools than
the package itself.

Decision
--------
The published package depends only on Django and asgiref, with lower bounds and
no upper bounds, set in ``pyproject.toml``. Optional extras add what tests,
Redis, type checking and the docs need. The development environment is pinned
separately: ``requirements/in/constraints.in`` holds the
global version constraints, ``in/base.in`` the runtime requirements and
``in/local.in`` the developer tools, each starting with ``-r constraints.in``.
``make python-requirements`` compiles them with pip-compile into the pinned
``requirements/base.txt`` and ``local.txt``. ``make init`` installs
``local.txt`` into this repository's own ``venv/``, then the package itself,
editable.

Alternatives Considered
-----------------------
- Pin the package's dependencies, which conflicts with every project that pins its own.
- Develop in another project's virtual environment, which hides missing dependencies.

Consequences
------------
- **Positive:**

  - The package installs alongside any project's own pins.
  - Every developer gets the same tool versions.

- **Negative:**

  - ``constraints.in`` repeats the lower bounds of ``pyproject.toml``, and the two must be kept the same.
  - Dependency updates are not automated.

Related ADRs
------------
- `Smarter ADR-015: Dependency Management <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/015-dependency-management.rst>`__
