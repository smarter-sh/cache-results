Installation
============

Requirements
------------

- Python 3.10 or newer
- Django 4.2 or newer
- Any Django cache backend. With a shared cache such as Redis, cached results
  survive restarts and are shared by every process and server of your project.

Install the package
-------------------

Install it from PyPI:

.. code-block:: console

    $ pip install cache-results

Its only dependencies are Django and asgiref. To use Redis, install a Redis
backend too, e.g. `django-redis <https://github.com/jazzband/django-redis>`__:

.. code-block:: console

    $ pip install django-redis

Configure a cache
-----------------

cache-results stores results in one of your project's Django caches, the
``default`` one unless you say otherwise. If your project doesn't configure
``CACHES``, Django uses a local-memory cache, which is private to each process
and lost on restart. For a production site, configure a shared cache:

.. code-block:: python

    # settings.py
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/1",
        }
    }

There is nothing to add to ``INSTALLED_APPS``. Every cache-results setting is
optional: see :doc:`guide/settings`.

Next: :doc:`quickstart`.
