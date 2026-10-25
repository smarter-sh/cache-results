"""Tests of cache_results.lazy, Django's cache imported once Django is ready."""

from unittest.mock import patch

from django.core.cache import caches
from django.core.cache.backends.locmem import LocMemCache
from django.test import SimpleTestCase

from cache_results import lazy_cache
from cache_results.lazy import LazyCache


class TestLazyCache(SimpleTestCase):
    """Test LazyCache against the test settings' default cache."""

    def setUp(self):
        caches["default"].clear()

    def test_singleton(self):
        """Lazy_cache is a LazyCache that wraps django.core.cache.cache."""
        from django.core.cache import cache  # pylint: disable=import-outside-toplevel

        self.assertIsInstance(lazy_cache, LazyCache)
        self.assertTrue(lazy_cache.ready)
        self.assertIs(lazy_cache.cache, cache)

    def test_before_apps_are_ready(self):
        """Before Django's apps are ready, the cache is None and a warning is logged."""
        lazy = LazyCache()
        with patch("cache_results.lazy.apps") as apps, self.assertLogs("cache_results.lazy", "WARNING"):
            apps.ready = False
            self.assertIsNone(lazy.cache)
            self.assertFalse(lazy.ready)
        self.assertIsNone(lazy._cache)  # pylint: disable=protected-access

    def test_get_set_delete(self):
        """Values are set, read with a default, and deleted."""
        self.assertIsNone(lazy_cache.get("k"))
        self.assertEqual(lazy_cache.get("k", "fallback"), "fallback")
        lazy_cache.set("k", "v")
        self.assertEqual(lazy_cache.get("k"), "v")
        self.assertTrue(lazy_cache.has_key("k"))
        self.assertTrue(lazy_cache.delete("k"))
        self.assertFalse(lazy_cache.has_key("k"))

    def test_timeouts(self):
        """Without a timeout the cache's own is used; None never expires; 0 stores nothing."""
        lazy_cache.set("default", 1)
        lazy_cache.set("forever", 1, timeout=None)
        lazy_cache.set("never", 1, timeout=0)
        self.assertEqual(lazy_cache.get_many(["default", "forever", "never"]), {"default": 1, "forever": 1})
        with patch.object(lazy_cache.cache, "set") as set_:
            lazy_cache.set("k", 1)
            set_.assert_called_once_with("k", 1, version=None)
            lazy_cache.set("k", 1, timeout=None)
            set_.assert_called_with("k", 1, timeout=None, version=None)

    def test_add_touch(self):
        """Add() sets only a missing key, and touch() renews a key's timeout."""
        self.assertTrue(lazy_cache.add("k", 1))
        self.assertFalse(lazy_cache.add("k", 2, timeout=60))
        self.assertEqual(lazy_cache.get("k"), 1)
        self.assertTrue(lazy_cache.touch("k"))
        self.assertTrue(lazy_cache.touch("k", timeout=60))
        self.assertFalse(lazy_cache.touch("missing"))

    def test_many(self):
        """Several keys are set, read and deleted at once."""
        # Django's backends return the keys that could not be set; django-redis returns None.
        self.assertFalse(lazy_cache.set_many({"a": 1, "b": 2}))
        self.assertFalse(lazy_cache.set_many({"c": 3}, timeout=60))
        self.assertEqual(lazy_cache.get_many(["a", "b", "c"]), {"a": 1, "b": 2, "c": 3})
        lazy_cache.delete_many(["a", "b", "c"])
        self.assertEqual(lazy_cache.get_many(["a", "b", "c"]), {})

    def test_incr_decr_and_versions(self):
        """Numbers are incremented and decremented, and keys moved between versions."""
        lazy_cache.set("n", 0)
        self.assertEqual(lazy_cache.incr("n"), 1)
        self.assertEqual(lazy_cache.decr("n", 1), 0)
        self.assertEqual(lazy_cache.incr_version("n"), 2)
        self.assertEqual(lazy_cache.get("n", version=2), 0)
        self.assertEqual(lazy_cache.decr_version("n", version=2), 1)
        self.assertEqual(lazy_cache.get("n"), 0)

    def test_clear_close(self):
        """Clear() empties the cache, and close() is passed through."""
        lazy_cache.set("k", 1)
        self.assertIsNone(lazy_cache.clear())
        self.assertIsNone(lazy_cache.get("k"))
        self.assertIsNone(lazy_cache.close())

    def test_first_use_checks_the_cache(self):
        """On first use the cache is checked, and a local-memory default cache is warned about."""
        with self.assertLogs("cache_results.lazy", "DEBUG") as logs:
            cache = LazyCache().cache
        output = "\n".join(logs.output)
        if isinstance(cache, LocMemCache):
            self.assertIn("persists nothing across processes", output)
        self.assertIn("the cache is ready", output)

    def test_check_reports_a_broken_cache(self):
        """A cache that loses what was written, or raises, is logged as an error."""
        lazy = LazyCache()
        with patch.object(LocMemCache, "get", return_value=None), self.assertLogs("cache_results.lazy", "ERROR"):
            lazy._check(LocMemCache("broken", {}))  # pylint: disable=protected-access
        with patch.object(LocMemCache, "set", side_effect=ConnectionError("down")):
            with self.assertLogs("cache_results.lazy", "ERROR") as logs:
                lazy._check(LocMemCache("broken", {}))  # pylint: disable=protected-access
        self.assertIn("down", "\n".join(logs.output))
