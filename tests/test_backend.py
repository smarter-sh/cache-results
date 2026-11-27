"""Tests of cache_results.backend, the cache that holds cached results: a CACHES alias, or one of its own."""

import json
import os
import threading
from unittest.mock import patch

from django.core.cache import caches
from django.core.cache.backends.locmem import LocMemCache
from django.test import SimpleTestCase, override_settings

from cache_results import backend, cache_results
from cache_results.backend import (
    CHECK_KEY,
    check_cache,
    check_once,
    create_cache,
    results_cache,
)
from cache_results.conf import ENVIRONMENT_VARIABLE
from cache_results.keys import make_key

OWN_CACHE = {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "cache-results-own",
    "KEY_PREFIX": "own",
}
"""A cache of the package's own, configured like an entry of CACHES."""


class TestResultsCache(SimpleTestCase):
    """The cache of cached results is the CACHES alias, unless CACHE_RESULTS["CACHE"] gives one of its own."""

    def setUp(self):
        caches["default"].clear()
        create_cache(OWN_CACHE).clear()
        backend._checked.clear()  # pylint: disable=protected-access
        backend._local.__dict__.clear()  # pylint: disable=protected-access

    def test_the_alias_by_default(self):
        """Without CACHE, it is the cache that CACHE_ALIAS names, as before."""
        self.assertIs(results_cache(), caches["default"])

    @override_settings(CACHE_RESULTS={"CACHE": OWN_CACHE})
    def test_a_cache_of_its_own(self):
        """With CACHE, results go to a cache of the package's own, and the project's cache is left as it is."""
        calls = []

        @cache_results(timeout=60)
        def double(x: int) -> int:
            calls.append(x)
            return x * 2

        self.assertEqual(double(21), 42)
        self.assertEqual(double(21), 42)
        self.assertEqual(calls, [21])
        own = results_cache()
        self.assertIsNot(own, caches["default"])
        self.assertEqual(own.key_prefix, "own")
        key = make_key(double.__wrapped__, (21,), {})
        self.assertEqual(own.get(key), 42)
        self.assertIsNone(caches["default"].get(key))

    def test_a_cache_of_its_own_from_the_environment(self):
        """With only CACHE_RESULTS_CACHE set, as a deployment sets it for one process, results go to that cache."""
        calls = []

        @cache_results(timeout=60)
        def triple(x: int) -> int:
            calls.append(x)
            return x * 3

        with patch.dict(os.environ, {ENVIRONMENT_VARIABLE: json.dumps(OWN_CACHE)}):
            self.assertEqual(triple(7), 21)
            self.assertEqual(triple(7), 21)
            own = results_cache()
        self.assertEqual(calls, [7])
        self.assertEqual(own.key_prefix, "own")
        key = make_key(triple.__wrapped__, (7,), {})
        self.assertEqual(own.get(key), 21)
        self.assertIsNone(caches["default"].get(key))

    def test_one_backend_per_thread_and_setting(self):
        """A thread keeps its backend while the setting is unchanged; another thread, or a new setting, builds one."""
        with override_settings(CACHE_RESULTS={"CACHE": OWN_CACHE}):
            first = results_cache()
            self.assertIs(results_cache(), first)
            others = []
            thread = threading.Thread(target=lambda: others.append(results_cache()))
            thread.start()
            thread.join()
            self.assertIsNot(others[0], first)
        with override_settings(CACHE_RESULTS={"CACHE": dict(OWN_CACHE)}):
            self.assertIsNot(results_cache(), first)

    def test_each_cache_is_checked_once_per_process(self):
        """The first use of each cache checks it, and later uses don't."""
        with patch.object(backend, "check_cache") as check:
            results_cache()
            results_cache()
            with override_settings(CACHE_RESULTS={"CACHE": OWN_CACHE}):
                results_cache()
                results_cache()
        self.assertEqual(check.call_count, 2)

    def test_the_identity_of_an_own_cache_holds_no_secret(self):
        """An own cache is told apart by a hash of its configuration, which may hold a password."""
        config = {**OWN_CACHE, "LOCATION": "redis://user:a-password@redis:6379/1"}
        identity = backend._config_identity(config)  # pylint: disable=protected-access
        self.assertTrue(identity.startswith("own:"))
        self.assertNotIn("a-password", identity)
        self.assertNotEqual(identity, backend._config_identity(OWN_CACHE))  # pylint: disable=protected-access

    def test_create_cache(self):
        """BACKEND is the class, LOCATION its location, and the other entries its params, as in CACHES."""
        cache = create_cache(OWN_CACHE)
        self.assertIsInstance(cache, LocMemCache)
        self.assertEqual(cache.key_prefix, "own")
        self.assertEqual(OWN_CACHE["BACKEND"], "django.core.cache.backends.locmem.LocMemCache")


class TestCheckCache(SimpleTestCase):
    """Check_cache() writes and reads a test key, and logs an error when every cached function would run uncached."""

    def test_a_working_cache(self):
        """The test key is written, read back and deleted."""
        cache = create_cache(OWN_CACHE)
        with self.assertLogs("cache_results.backend", "DEBUG") as logs:
            self.assertTrue(check_cache(cache))
        self.assertIn("is ready", "\n".join(logs.output))
        self.assertIsNone(cache.get(CHECK_KEY))

    def test_a_cache_that_refuses(self):
        """A refused write is an error that names the exception's class, never its message, which can name the host."""
        cache = create_cache(OWN_CACHE)
        with patch.object(LocMemCache, "set", side_effect=PermissionError("NOPERM at redis.internal")):
            with self.assertLogs("cache_results.backend", "ERROR") as logs:
                self.assertFalse(check_cache(cache))
        output = "\n".join(logs.output)
        self.assertIn("PermissionError", output)
        self.assertIn("runs uncached", output)
        self.assertNotIn("redis.internal", output)

    def test_a_cache_that_loses_the_value(self):
        """A cache that doesn't return what was just written persists nothing."""
        cache = create_cache(OWN_CACHE)
        with patch.object(LocMemCache, "get", return_value=None):
            with self.assertLogs("cache_results.backend", "ERROR") as logs:
                self.assertFalse(check_cache(cache))
        self.assertIn("persists nothing", "\n".join(logs.output))

    def test_check_once(self):
        """A cache is checked the first time only."""
        backend._checked.clear()  # pylint: disable=protected-access
        with patch.object(backend, "check_cache") as check:
            check_once(caches["default"], "alias:once")
            check_once(caches["default"], "alias:once")
        check.assert_called_once_with(caches["default"])
