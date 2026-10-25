ADR-015: Type Annotations
=========================

Status
------
Accepted

Context
-------
The package ships ``py.typed``, so its users' type checkers and editors read its
annotations, and an annotation is a promise to them.

Decision
--------
Every function and method is annotated, in Python 3.10 syntax (``X | None``),
which the pyupgrade hook enforces. ``Any`` is used only where a value really
can be anything, such as a decorated function's arguments. ``make typecheck``
runs mypy with django-stubs, which is a development dependency.

Alternatives Considered
-----------------------
- Leave the package untyped, which leaves users' type checkers blind to it.

Consequences
------------
- **Positive:**

  - Errors are caught by the type checker, in this repository and in users' projects.

- **Negative:**

  - Django's types sometimes disagree with its behavior, e.g. ``DEFAULT_TIMEOUT`` is an ``object()`` that is accepted as a ``float``, which needs a ``cast()``.

Related ADRs
------------
- `Smarter ADR-027: Annotations <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/027-annotations.rst>`__
- :doc:`ADR-014: Docstrings <014-docstrings>`
