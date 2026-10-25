"""
Django settings for the cache-results test suite.

The tests run against Django's local-memory cache. Set ``CACHE_RESULTS_TEST_REDIS_URL``,
e.g. to ``redis://localhost:6379/15``, to run them against Redis through django-redis
instead (``pip install -e .[test,redis]``).
"""

import os

SECRET_KEY = "cache-results-tests"  # nosec B105: test settings only
USE_TZ = True
INSTALLED_APPS: list[str] = []
DATABASES: dict = {}

_redis_url = os.environ.get("CACHE_RESULTS_TEST_REDIS_URL")

if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "cache-results"}}
