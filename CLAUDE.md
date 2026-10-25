# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

cache-results is a Django decorator, `@cache_results`, that caches a
function's results by its arguments. It is published to PyPI as
`cache-results`, with the import name `cache_results`. It grew out of the
caching layer of [Smarter](https://github.com/smarter-sh/smarter) (usually
checked out beside this repository as `../smarter`), which uses it through its
own hooks in `smarter/smarter/lib/cache/hooks.py`.

## Hard rules

1. **Never run git write commands**, here or in `../smarter`. "Write a git
   commit" means print the command as text: one `git commit` with one `-m` per
   paragraph, conventional-commit header of 72 characters or fewer, authored by
   `Claude <noreply@anthropic.com>`, co-authored by
   `Lawrence McDaniel <lpm0073@gmail.com>`.
2. **Run the tests yourself** after any change (`make test`), and against
   Redis when you touch how the cache is read or written. Report failures
   honestly.
3. **Depend only on Django and asgiref.** Nothing project-specific belongs
   here: a project adapts the decorator through the `CACHE_RESULTS` setting
   and its hooks (`KEY_ENCODER`, `LOGGING_ENABLED`, `VERBOSE_LOGGING`,
   `LOG_PREFIX`).
4. **Never key by `str()`.** An argument the key encoder doesn't know runs the
   function uncached. Two objects with the same string would share an entry,
   and an object without its own `__str__` gets a new key in every process.
5. **Never log a result or a secret.** Logs name the function and the type of
   its result. Arguments are logged only when verbose logging is on.
6. **Don't change `CACHE_NONE_SENTINEL` or the key format** without a major
   version: either change makes every existing cached entry unreadable.
7. **The pre-commit hooks are the lint standard** (`make lint`).
8. **Coverage:** at least 95% (`make coverage`).
9. **This repository is public.** No credentials, private hostnames or
   customer data.

## Repository map

| Path                              | Contents                                                    |
| --------------------------------- | ----------------------------------------------------------- |
| `src/cache_results/decorators.py` | `cache_results`, its wrappers and `invalidate()`            |
| `src/cache_results/keys.py`       | Cache keys: `CacheKeyEncoder`, `normalize()`, `make_key()`  |
| `src/cache_results/conf.py`       | The `CACHE_RESULTS` setting and its defaults                |
| `src/cache_results/sentinels.py`  | The markers for a cache miss and a cached `None`            |
| `tests/`                          | pytest-django tests, one module per source module           |
| `tests/settings.py`               | Test settings: local-memory cache, or Redis from an env var |

## Conventions

- Docstrings are reStructuredText (`:param:`, `:returns:`, `:raises:`), for
  Sphinx autodoc.
- Log messages start with `_prefix(event)`, use %-style arguments, and say
  why something happened.
- Import `django.core.cache` only inside functions: importing it while Django
  is starting can leave the cache on the wrong backend.
- Tests use `SimpleTestCase` and clear the cache in `setUp`. Settings
  changes go through `override_settings`.
