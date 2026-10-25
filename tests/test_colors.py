"""Tests of cache_results.colors, log prefixes colored by event."""

from django.test import SimpleTestCase, override_settings

from cache_results.colors import DEFAULT_COLORS, RESET, log_prefix
from cache_results.conf import cache_results_settings


class TestLogPrefix(SimpleTestCase):
    """Test the colors of each event."""

    def test_default_colors(self):
        """Hits are green, misses red, invalidations gray, and other messages bold red."""
        for event, color in DEFAULT_COLORS.items():
            self.assertEqual(log_prefix("p", event), f"{color}p{RESET}")
        self.assertEqual(log_prefix("p"), f"{DEFAULT_COLORS['']}p{RESET}")

    @override_settings(CACHE_RESULTS={"LOG_COLORS": {"hit": "\033[94m", "": None}})
    def test_log_colors(self):
        """LOG_COLORS changes a color, and an empty one leaves the text uncolored."""
        self.assertEqual(log_prefix("p", "hit"), f"\033[94mp{RESET}")
        self.assertEqual(log_prefix("p", "miss"), f"{DEFAULT_COLORS['miss']}p{RESET}")
        self.assertEqual(log_prefix("p", ""), "p")

    @override_settings(CACHE_RESULTS={"LOG_PREFIX": "cache_results.colors.log_prefix"})
    def test_named_by_log_prefix(self):
        """Named by LOG_PREFIX, it formats every log message."""
        self.assertEqual(cache_results_settings.log_prefix("p", "miss"), f"{DEFAULT_COLORS['miss']}p{RESET}")
