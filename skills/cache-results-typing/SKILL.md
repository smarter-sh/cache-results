---
name: cache-results-typing
description: Use when writing or reviewing type annotations in cache-results, which ships py.typed so that its users' type checkers read them. Covers the Python 3.10 syntax that pyupgrade enforces, when Any is honest, the DEFAULT_TIMEOUT cast, and checking with make typecheck (mypy with django-stubs).
---

# cache-results Type Annotations

The package ships `py.typed`, so **its users' type checkers** read these
annotations, and their editors show them. An annotation is a claim; make it
true. This is Smarter's rule (`../smarter/skills/smarter-python-typing`),
without Smarter's aliases: this package depends only on Django.

## Syntax

- Python 3.10 and newer: `X | None`, `list[int]`, `type[CacheKeyEncoder]`,
  `collections.abc.Callable`. pyupgrade (`--py310-plus`) rewrites the old forms
  in annotations; write the new ones to begin with.
- In an **expression**, e.g. `cast(Optional[float], value)`, the `typing` form
  stays: pyupgrade leaves it, and it is what the code means at runtime.

## When `Any` is acceptable

Only when the value really can be anything:

- A decorated function's arguments and result: the decorator caches whatever
  the function takes and returns.
- `*args`/`**kwargs` passed straight through.

Otherwise list the types. A setting's value is `str | object | None`, not
`Any`. Avoid `Optional[Any]`: it says no more than `Any`.

## Django's types

- `DEFAULT_TIMEOUT` is a bare `object()` that cache methods accept, while their
  stubs declare `timeout: float | None`. `conf.timeout` returns
  `Optional[float]` with a `cast()` and a comment saying why. Don't widen
  timeout parameters to `object` to avoid it: Pylance then flags every call.
- Import Django types for annotations only inside functions, or under
  `if TYPE_CHECKING:`, if the import would touch `django.core.cache`
  (`cache-results-development`).

## Checking your work

```console
make typecheck          # mypy, with django-stubs and tests.settings
git diff --name-only -- '*.py' | xargs grep -nE '(: *|-> *|\[)Any\b'
```

`make typecheck` must pass. CI doesn't run it yet, so run it yourself after
changing annotations. For each `Any` the grep finds, ask whether you can list
the types instead.
