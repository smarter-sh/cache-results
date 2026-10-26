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
- A **quoted forward reference** stays `Optional["BaseCache"]`, because
  `"BaseCache" | None` fails at runtime unless the module starts with
  `from __future__ import annotations`.
- **Annotate every function and method** (ADR-015). Some in `lazy.py` and
  `decorators.py` (`LazyCache.get()`, `get_cache()`) still aren't; annotate
  them when you touch them.

## When `Any` is acceptable

Only when the value really can be anything:

- A decorated function's arguments and result: the decorator caches whatever
  the function takes and returns.
- `*args`/`**kwargs` passed straight through.

Otherwise list the types. A setting's value is `str | object | None`, not
`Any`. Avoid `Optional[Any]`: it says no more than `Any`.

- **A value that is only stored, compared or passed on** is `object`, not
  `Any`: it accepts anything and keeps the checker on. `_aget()`, `wrap()` and
  `unwrap()` in `decorators.py` do this with cached results.
- **A return type with a finite set of possibilities** is a union, or
  `X | None`. If callers must then narrow it, that's the truth; consider
  splitting the function in two.
- **A return type that depends on an argument's type** takes `@overload`, or a
  `TypeVar` (a `ParamSpec` too, for a decorator) for a function that returns
  what it was given.
- **A third-party object whose type you didn't look up**, e.g. a cache
  backend, is `django.core.cache.backends.base.BaseCache`, not `Any`.
- **`:type ...: Any` or `:rtype: Any`** in a docstring changes with the
  annotation (`cache-results-docstrings`).

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
