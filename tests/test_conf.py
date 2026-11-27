"""Tests of cache_results.conf, the CACHE_RESULTS setting."""

import json
import os
from unittest.mock import patch

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from cache_results.conf import ENVIRONMENT_VARIABLE, cache_results_settings
from cache_results.keys import CacheKeyEncoder


class _ProjectCacheKeyEncoder(CacheKeyEncoder):
    """A project's own encoder, as KEY_ENCODER names one."""


def _always() -> bool:
    """A LOGGING_ENABLED hook that is always on."""
    return True


def _shout(text: str, event: str) -> str:
    """A LOG_PREFIX hook."""
    return f"{text.upper()}[{event}]"


class TestCacheResultsSettings(SimpleTestCase):
    """Test CacheResultsSettings, with and without a CACHE_RESULTS setting."""

    @override_settings(CACHE_RESULTS=None)
    def test_defaults(self):
        """Without the setting: the default cache and its timeout, no prefix, the strict encoder, no logs."""
        self.assertEqual(cache_results_settings.cache_alias, "default")
        self.assertIsNone(cache_results_settings.cache)
        self.assertIs(cache_results_settings.timeout, DEFAULT_TIMEOUT)
        self.assertEqual(cache_results_settings.key_prefix, "")
        self.assertIs(cache_results_settings.key_encoder, CacheKeyEncoder)
        self.assertFalse(cache_results_settings.logging_enabled)
        self.assertFalse(cache_results_settings.verbose_logging)
        self.assertEqual(cache_results_settings.log_prefix("prefix", "hit"), "prefix")

    def test_cache(self):
        """A cache of the package's own is configured like an entry of CACHES, with a BACKEND."""
        own = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "KEY_PREFIX": "own"}
        with override_settings(CACHE_RESULTS={"CACHE": own}):
            self.assertEqual(cache_results_settings.cache, own)
        for invalid in ("redis://redis:6379/1", {"LOCATION": "redis://redis:6379/1"}):
            with self.subTest(invalid=invalid), override_settings(CACHE_RESULTS={"CACHE": invalid}):
                with self.assertRaises(TypeError):
                    _ = cache_results_settings.cache

    def test_cache_from_the_environment(self):
        """CACHE_RESULTS_CACHE, a JSON object like CACHE, wins over the setting; blank, the setting is used."""
        from_environment = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "KEY_PREFIX": "env"}
        from_setting = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "KEY_PREFIX": "setting"}
        with override_settings(CACHE_RESULTS={"CACHE": from_setting}):
            with patch.dict(os.environ, {ENVIRONMENT_VARIABLE: json.dumps(from_environment)}):
                self.assertEqual(cache_results_settings.cache, from_environment)
                # parsed once per value: the same dict every time, so each thread keeps its backend.
                self.assertIs(cache_results_settings.cache, cache_results_settings.cache)
            with patch.dict(os.environ, {ENVIRONMENT_VARIABLE: "  "}):
                self.assertEqual(cache_results_settings.cache, from_setting)
        with patch.dict(os.environ, {ENVIRONMENT_VARIABLE: json.dumps(from_environment)}):
            with override_settings(CACHE_RESULTS=None):
                self.assertEqual(cache_results_settings.cache, from_environment)

    def test_an_invalid_cache_in_the_environment(self):
        """Invalid JSON, or no BACKEND, names the variable, never its value, which holds credentials."""
        for invalid in ('{"LOCATION": "redis://user:secret@redis:6379/1"', '{"LOCATION": "redis://user:secret@redis"}'):
            with self.subTest(invalid=invalid), patch.dict(os.environ, {ENVIRONMENT_VARIABLE: invalid}):
                with self.assertRaises(ImproperlyConfigured) as raised:
                    _ = cache_results_settings.cache
                self.assertIn(ENVIRONMENT_VARIABLE, str(raised.exception))
                self.assertNotIn("secret", str(raised.exception))
                self.assertIsNone(raised.exception.__cause__)

    @override_settings(CACHE_RESULTS={"KEY_PREFIX": "app:", "VERSION": 3, "TIMEOUT": 10, "CACHE_ALIAS": "results"})
    def test_values(self):
        """Prefix and version start every key, and the alias and timeout are used as given."""
        self.assertEqual(cache_results_settings.key_prefix, "app:v3:")
        self.assertEqual(cache_results_settings.timeout, 10)
        self.assertEqual(cache_results_settings.cache_alias, "results")

    @override_settings(CACHE_RESULTS={"VERSION": 0})
    def test_version_zero(self):
        """A version of 0 is still a version."""
        self.assertEqual(cache_results_settings.key_prefix, "v0:")

    def test_hooks_as_objects_dotted_paths_and_flags(self):
        """Hooks are given as objects, as dotted paths, or as plain flags."""
        with override_settings(CACHE_RESULTS={"LOGGING_ENABLED": _always, "VERBOSE_LOGGING": True}):
            self.assertTrue(cache_results_settings.logging_enabled)
            self.assertTrue(cache_results_settings.verbose_logging)
        with override_settings(
            CACHE_RESULTS={"LOGGING_ENABLED": f"{__name__}._always", "LOG_PREFIX": f"{__name__}._shout"}
        ):
            self.assertTrue(cache_results_settings.logging_enabled)
            self.assertEqual(cache_results_settings.log_prefix("prefix", "miss"), "PREFIX[miss]")
        with override_settings(CACHE_RESULTS={"KEY_ENCODER": _ProjectCacheKeyEncoder}):
            self.assertIs(cache_results_settings.key_encoder, _ProjectCacheKeyEncoder)
        with override_settings(CACHE_RESULTS={"KEY_ENCODER": f"{__name__}._ProjectCacheKeyEncoder"}):
            self.assertIs(cache_results_settings.key_encoder, _ProjectCacheKeyEncoder)

    @override_settings(CACHE_RESULTS={"KEY_ENCODER": "json.JSONEncoder"})
    def test_key_encoder_must_be_a_cache_key_encoder(self):
        """An encoder that isn't a CacheKeyEncoder, which would not refuse unsafe arguments, is refused."""
        with self.assertRaises(TypeError):
            _ = cache_results_settings.key_encoder


class TestOption(SimpleTestCase):
    """Test option(), which hooks use for their own entries of the setting."""

    @override_settings(CACHE_RESULTS={"LOGGING_SWITCH": "my_switch"})
    def test_option(self):
        """An entry is returned as set, and a missing one as the default."""
        self.assertEqual(cache_results_settings.option("LOGGING_SWITCH"), "my_switch")
        self.assertIsNone(cache_results_settings.option("LOG_COLORS"))
        self.assertEqual(cache_results_settings.option("LOG_COLORS", {}), {})
