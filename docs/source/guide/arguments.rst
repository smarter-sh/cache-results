Arguments and Cache Keys
========================

How a key is made
-----------------

A cache key is the function's module and qualified name, followed by a
32-character SHA-256 hash of its arguments:

.. code-block:: text

    myapp.books.get_book_summary()_3f0c9d1e8b7a4c2f9e6d5b4a3c2f1e0d

Before hashing, the arguments are bound to the function's signature, with
defaults applied. So these calls share one entry:

.. code-block:: python

    @cache_results()
    def search(query: str, limit: int = 10) -> list: ...


    search("django")
    search("django", 10)
    search(query="django", limit=10)

Two functions never share an entry, even with the same name in one module,
because the key uses the qualified name (``ClassName.method``,
``outer.<locals>.inner``).

Types that can be part of a key
-------------------------------

- ``str``, ``int``, ``float``, ``bool`` and ``None``
- lists, tuples, dicts, sets and frozensets of them, nested as deeply as you
  like
- :class:`~datetime.datetime`, :class:`~datetime.date`,
  :class:`~datetime.time`, :class:`~datetime.timedelta`,
  :class:`~decimal.Decimal` and :class:`~uuid.UUID`
- Django's lazy translation strings
- classes, identified by their module and qualified name
- dataclass instances, identified by their class and their fields

Equal values make equal keys, in every process: sets are sorted, and dict keys
are sorted. A dict and a list of its pairs make different keys, and so do a set
and a list of the same items.

Anything else runs uncached
---------------------------

Any other argument, such as a model instance, a request or an open file, can't
be part of a safe key. ``str()`` of two different model rows can be equal, and
``<Book object at 0x...>`` changes in every process. So instead of guessing,
cache-results runs the function **uncached** and logs an error that names the
function and the argument's type, once per process:

.. code-block:: text

    ERROR cache_results.decorators.@cache_results() get_book_summary() runs uncached:
    a myapp.models.Book can't be part of a cache key. Pass plain values (str, int, bool, tuples), such as an id.

Arguments that can't be serialized for another reason, such as a list that
contains itself or a timezone-aware :class:`~datetime.time`, also run uncached.

The fix is to pass what identifies the object, and to load it inside the
function:

.. code-block:: python

    @cache_results()
    def get_book_summary(book_id: int) -> dict:
        book = Book.objects.get(pk=book_id)
        ...

Adding a type
-------------

To allow another type, subclass :class:`~cache_results.keys.CacheKeyEncoder`,
encode your type into JSON-ready values that are equal for equal objects, and
name your class in the ``KEY_ENCODER`` setting:

.. code-block:: python

    # myapp/cache.py
    from cache_results import CacheKeyEncoder


    class MyCacheKeyEncoder(CacheKeyEncoder):
        def default(self, o):
            if isinstance(o, Money):
                return {"__money__": [str(o.amount), o.currency]}
            return super().default(o)

.. code-block:: python

    # settings.py
    CACHE_RESULTS = {"KEY_ENCODER": "myapp.cache.MyCacheKeyEncoder"}

Tag the value with the type's name, as above, so that it can't share a key
with a plain dict or list.

Never pass a secret
-------------------

Arguments are part of the key, and verbose logging writes them to the log. Never
pass an api key, password or token. Pass the id of the record that holds it, and
read the secret inside the function:

.. code-block:: python

    @cache_results(timeout=300)
    def fetch_report(account_id: int) -> dict:
        api_key = Account.objects.get(pk=account_id).api_key
        return requests.get(REPORT_URL, headers={"Authorization": api_key}, timeout=10).json()

A fixed key
-----------

``cache_key`` gives a function one fixed key, which every call shares, whatever
its arguments. Use it only for a function whose result doesn't depend on them:

.. code-block:: python

    @cache_results(timeout=86400, cache_key="myapp.country_list")
    def get_countries() -> list[str]: ...
