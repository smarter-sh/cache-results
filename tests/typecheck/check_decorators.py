"""
Type checks for decorated functions, run by mypy (``make typecheck``), not pytest.

Each ``assert_type()`` fails the check if a decorated function loses its
parameters, its result or ``invalidate()``. Each ``# type: ignore[...]`` marks
a call that must be flagged: ``warn_unused_ignores`` fails the check if it
isn't.
"""

from collections.abc import Callable, Coroutine
from typing import Any

from typing_extensions import assert_type

from cache_results import cache_results


@cache_results(timeout=60)
def get_thing(pk: int, name: str = "x") -> str:
    """A cached function."""
    return f"{pk}{name}"


@cache_results()
async def aget_thing(pk: int) -> str:
    """A cached async function."""
    return str(pk)


@cache_results()
def get_all() -> list[int]:
    """A cached function without parameters."""
    return [1]


class Shape:  # pylint: disable=too-few-public-methods
    """A class with a cached classmethod."""

    @classmethod
    @cache_results(timeout=60)
    def describe(cls, size: int) -> str:
        """A cached classmethod."""
        return f"{cls.__name__}:{size}"


def check_sync() -> None:
    """A sync function keeps its signature and result, and has invalidate()."""
    assert_type(get_thing(1), str)
    assert_type(get_thing(1, name="y"), str)
    assert_type(get_thing.invalidate(1), None)
    assert_type(get_thing.invalidate(pk=1, name="y"), None)
    assert_type(get_all(), list[int])
    assert_type(get_all.invalidate(), None)
    assert_type(get_thing.__qualname__, str)
    wrapped: Callable[[int, str], str] = get_thing.__wrapped__
    assert_type(wrapped(1, "y"), str)
    get_thing("1")  # type: ignore[arg-type]
    get_thing.invalidate("1")  # type: ignore[arg-type]
    get_thing.invalidate(1, "y", "z")  # type: ignore[call-arg]
    get_all.invalidate(1)  # type: ignore[call-arg]


async def check_async() -> None:
    """An async function still returns a coroutine of its result, and invalidate() stays synchronous."""
    # mypy calls it a Coroutine, and pyright a CoroutineType, so check that it is one rather than which.
    coroutine: Coroutine[Any, Any, str] = aget_thing(1)
    assert_type(await coroutine, str)
    await aget_thing("1")  # type: ignore[arg-type]
    assert_type(aget_thing.invalidate(1), None)
    aget_thing.invalidate("1")  # type: ignore[arg-type]


def check_classmethod() -> None:
    """A cached classmethod is called without cls, and invalidated with it."""
    assert_type(Shape.describe(2), str)
    assert_type(Shape.describe.invalidate(Shape, 2), None)
    Shape.describe("2")  # type: ignore[arg-type]
    Shape.describe.invalidate(2)  # type: ignore[arg-type, call-arg]
