"""
Log prefixes colored by event, with ANSI codes.

.. code-block:: python

    CACHE_RESULTS = {"LOG_PREFIX": "cache_results.colors.log_prefix"}

Hits are green, misses red, invalidations gray, and other messages, such as
errors, bold red. Colors can be changed with ``CACHE_RESULTS["LOG_COLORS"]``,
a dict from event (``"hit"``, ``"miss"``, ``"invalidate"`` or ``""``) to an
ANSI code.
"""

from typing import Optional, cast

from .conf import cache_results_settings

RESET = "\033[0m"
"""The ANSI code that ends a color."""

DEFAULT_COLORS = {
    "hit": "\033[32m",
    "miss": "\033[31m",
    "invalidate": "\033[37m",
    "": "\033[1;31m",
}
"""The color of each event, unless ``CACHE_RESULTS["LOG_COLORS"]`` sets it."""


def log_prefix(text: str, event: str = "") -> str:
    """
    Color the start of a log message by its event.

    :param text: e.g. ``cache_results.decorators.@cache_results()``.
    :type text: str
    :param event: ``"hit"``, ``"miss"``, ``"invalidate"`` or ``""``.
    :type event: str
    :return: The colored text, or ``text`` for an event without a color.
    :rtype: str
    """
    overrides = cast(Optional[dict[str, Optional[str]]], cache_results_settings.option("LOG_COLORS"))
    colors = {**DEFAULT_COLORS, **(overrides or {})}
    color = colors.get(event)
    if not color:
        return text
    return f"{color}{text}{RESET}"


__all__ = ["DEFAULT_COLORS", "RESET", "log_prefix"]
