# cache-results

A Django decorator that caches a function's results by its arguments, in any
Django cache, such as Redis.

```python
from cache_results import cache_results


@cache_results(timeout=600)
def get_book(book_id: int) -> dict:
    return Book.objects.values().get(pk=book_id)


get_book(42)             # computed and cached
get_book(42)             # served from the cache
get_book.invalidate(42)  # clears that entry
```

cache-results grew out of the caching layer of
[Smarter](https://github.com/smarter-sh/smarter), where it caches database
reads and third-party api calls across many application servers.

## Features

- **Safe keys.** The key is the function's module and qualified name, plus a
  hash of its arguments bound to its signature, so `f(1)`, `f(a=1)` and
  `f(1, b=2)` (when `b` defaults to 2) share one entry. Arguments that can't
  be part of a safe key, such as model instances, run the function uncached and
  log an error, rather than be keyed by `str()`.
- **`None` is cached** like any other result.
- **`.invalidate(\*args, **kwargs)`\*\* on every decorated function clears the
  entry of those arguments.
- **async functions** are cached without blocking the event loop.
- **Classmethods** are cached per class. Instance methods are refused, because
  `self` would be part of the key.
- **No stampede within a process.** Threads that miss the same key at once
  wait for the first one to compute it.
- **Safe during startup.** A function called before Django's apps are ready
  runs uncached, rather than initialize the cache framework too early.
- **Configurable** through one Django setting, `CACHE_RESULTS`.
- Depends only on Django and asgiref.

## Installation

cache-results is not on PyPI yet. Until it is, install it from GitHub:

```console
pip install "cache-results @ git+https://github.com/smarter-sh/cache-results"
```

It needs Python 3.10 or newer and Django 4.2 or newer, and works with any
Django cache backend. With a shared cache such as Redis, cached results
survive restarts and are shared by every application server.

## Arguments

The arguments are the cache key, so they must be plain values: `str`, `int`,
`float`, `bool`, `None`, and lists, tuples, dicts and sets of them, plus
datetimes, Decimals, UUIDs, classes and dataclasses. Pass a model's id, not the
model:

```python
@cache_results()
def get_profile(user_id: int) -> Profile:
    return Profile.objects.select_related("user").get(user_id=user_id)


get_profile(request.user.pk)
```

To allow another type, subclass `CacheKeyEncoder` and name your subclass in
the `KEY_ENCODER` setting:

```python
from cache_results import CacheKeyEncoder


class MyCacheKeyEncoder(CacheKeyEncoder):
    def default(self, o):
        if isinstance(o, Money):
            return {"__money__": [str(o.amount), o.currency]}
        return super().default(o)
```

Never pass a secret, such as an api key, as an argument: arguments are part
of the key, and verbose logging writes them to the log. Pass the id of the
record that holds it, and read the secret inside the function.

### Functions defined inside an inherited classmethod

A qualified name records where a function is defined, not who calls it. A
function defined inside a classmethod that subclasses inherit has the same
qualified name for every subclass, so subclasses would share its entries.
Give it the class name as a parameter:

```python
class Resource(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_cached(cls, pk: int):
        @cache_results()
        def _get(pk: int, class_name: str = cls.__name__):
            return cls.objects.get(pk=pk)

        return _get(pk)
```

## Settings

Every entry of the `CACHE_RESULTS` setting is optional:

```python
CACHE_RESULTS = {
    # the CACHES alias that holds cached results.
    "CACHE_ALIAS": "default",
    # the default timeout, in seconds, of a decorated function that names none.
    # Unset, it is the cache alias's own TIMEOUT.
    "TIMEOUT": 3600,
    # text that starts every key. Changing it, or VERSION, abandons every cached
    # result at once, without touching anything else in the same cache.
    "KEY_PREFIX": "",
    "VERSION": None,
    # a subclass of cache_results.CacheKeyEncoder, to allow more argument types.
    "KEY_ENCODER": "cache_results.keys.CacheKeyEncoder",
    # zero-argument callables that return whether to log cache hits, misses and
    # invalidations, and whether those logs include the arguments.
    "LOGGING_ENABLED": None,
    "VERBOSE_LOGGING": None,
    # a callable(text, event) that formats the start of each log message, where
    # event is "hit", "miss", "invalidate" or "".
    "LOG_PREFIX": None,
}
```

Callables and classes are given as dotted paths or as the objects themselves.
Settings are read on every call, so `override_settings` works in tests.

## Decorator options

```python
@cache_results(timeout=None, cache_key=None, logging_enabled=False)
```

- `timeout`: seconds. `None` uses the `TIMEOUT` setting, and `0` caches
  nothing.
- `cache_key`: a fixed key that every call shares, whatever its arguments.
  Use it only for functions whose result doesn't depend on them.
- `logging_enabled`: log this function's hits, misses and invalidations even
  when the `LOGGING_ENABLED` setting is off. Logs name the function and the
  type of its result, never the result.

## Development

```console
make init       # create .venv, install the package and its test tools, install the git hooks
make test       # run the tests against the local-memory cache
make coverage   # run the tests with a coverage report
```

To run the tests against Redis, set `CACHE_RESULTS_TEST_REDIS_URL`, e.g. to
`redis://localhost:6379/15`. The tests clear that database.

## Contributing

Bug reports, questions and pull requests are welcome. Please
[open an issue](https://github.com/smarter-sh/cache-results/issues) before
starting on a larger change, so that we can agree on its design first.

1. Fork the repository, and branch from `main`.
2. Run `make init`. It also installs the pre-commit hooks, which are the lint
   standard (black, flake8, isort, pyupgrade, codespell, bandit, Prettier) and
   check each commit message.
3. Make your change with its tests. `make coverage` must stay at 95% or
   more, and `make test` must pass against both the local-memory cache and
   Redis (see above).
4. Write [conventional commits](https://www.conventionalcommits.org/), e.g.
   `fix(keys): sort frozensets of tuples`. Releases are versioned from them:
   `fix` makes a patch release, `feat` a minor one.
5. Open a pull request that says what changed and why, and links its issue.

A few rules keep @cache_results() safe and readable:

- The package depends only on Django and asgiref. Project-specific behavior
  belongs in a project's own hooks, named by the `CACHE_RESULTS` setting.
- Arguments are never keyed by `str()`, and results and secrets are never
  logged.
- A change to the key format, or to the value stored for `None`, makes every
  cached entry unreadable, so it needs a major release.

Governance of the Smarter projects is described in
[smarter-sh/community](https://github.com/smarter-sh/community). Everyone who
takes part is expected to follow the [code of conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE)
