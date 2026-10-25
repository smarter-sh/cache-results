"""Tests of the package's public API and its sentinels."""

import re

from django.test import SimpleTestCase

import cache_results
from cache_results.sentinels import CACHE_MISS_SENTINEL, CACHE_NONE_SENTINEL, CacheSentinel


class TestPackage(SimpleTestCase):
    """Test what ``import cache_results`` provides."""

    def test_public_api(self):
        """The decorator, the encoder and its error are importable from the package."""
        self.assertTrue(callable(cache_results.cache_results))
        self.assertTrue(issubclass(cache_results.CacheKeyArgumentError, TypeError))
        self.assertEqual(
            sorted(cache_results.__all__), ["CacheKeyArgumentError", "CacheKeyEncoder", "__version__", "cache_results"]
        )

    def test_version(self):
        """The version is a semantic version, as semantic-release writes it."""
        self.assertRegex(cache_results.__version__, re.compile(r"^\d+\.\d+\.\d+"))


class TestSentinels(SimpleTestCase):
    """Test the sentinels that tell a cached None from a miss."""

    def test_miss_sentinel_is_unique(self):
        """A sentinel equals only itself, and names itself."""
        self.assertNotEqual(CACHE_MISS_SENTINEL, CacheSentinel("CACHE_MISS"))
        self.assertEqual(str(CACHE_MISS_SENTINEL), "<CacheSentinel: CACHE_MISS>")
        self.assertEqual(repr(CACHE_MISS_SENTINEL), str(CACHE_MISS_SENTINEL))

    def test_none_sentinel_is_stable(self):
        """The stored stand-in for None never changes, so that entries written by older versions still read as None."""
        self.assertEqual(CACHE_NONE_SENTINEL, 'CacheSentinel("CACHE_NONE")')
