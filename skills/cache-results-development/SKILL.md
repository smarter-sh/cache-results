---
name: cache-results-development
description: Start here for any change to the cache-results repository, the @cache_results Django decorator published to PyPI as cache-results. Gives the non-negotiable rules, the package's architecture (decorators, keys, conf, sentinels), the compatibility promises that protect cached entries, the Django and async traps, the logging style, how Smarter uses the package, and an index of the narrower skills to load for each kind of work.
---

# cache-results Development

`cache-results` (import name `cache_results`) is a Django decorator that caches
a function's results by its arguments, in any Django cache. It grew out of the
caching layer of [Smarter](https://github.com/smarter-sh/smarter), usually
checked out beside this repository as `../smarter`, which installs it from
PyPI and configures it with its own hooks in `smarter/smarter/lib/cache/hooks.py`.

## Repository map

| Path                               | What lives there                                                     |
| ---------------------------------- | -------------------------------------------------------------------- |
| `src/cache_results/decorators.py`  | `cache_results`, its sync and async wrappers, `invalidate()`         |
| `src/cache_results/keys.py`        | `CacheKeyEncoder`, `normalize()`, `make_key()`: what a key is        |
| `src/cache_results/conf.py`        | `CacheResultsSettings`: the `CACHE_RESULTS` setting, with defaults   |
| `src/cache_results/sentinels.py`   | `CACHE_MISS_SENTINEL`, `CACHE_NONE_SENTINEL`                         |
| `src/cache_results/lazy.py`        | `lazy_cache`: Django's cache, imported once Django is ready          |
| `src/cache_results/colors.py`      | `log_prefix()`: a `LOG_PREFIX` hook that colors messages by event    |
| `src/cache_results/__version__.py` | The version. **Written by semantic-release**, never by hand          |
| `tests/`                           | pytest-django tests, one module per source module                    |
| `docs/source/`                     | Sphinx docs: the api reference and the ADRs (`docs/source/adr/`)     |
| `requirements/in/*.in`             | Unpinned requirements, compiled into the pinned `requirements/*.txt` |
| `.vscode/settings.json`            | Points VS Code at this repository's own `venv/`                      |
| `.github/workflows/`               | `ci.yml` (lint, test, build), `release.yml` (semantic-release, PyPI) |
| `release.config.js`                | semantic-release's configuration                                     |
| `.pre-commit-config.yaml`          | The lint standard                                                    |
| `skills/`                          | These skills                                                         |

## Non-negotiable rules

1. **Never execute git write commands**, here or in `../smarter`. "Write a git
   commit" means output the command text. See `cache-results-git-commits`.
2. **Run the tests yourself** after every change: `make test`, and
   `make test-redis` when you touch how the cache is read or written. Never ask
   the user to re-run them. Report failures honestly. See `cache-results-testing`.
3. **Depend only on Django and asgiref.** Nothing project-specific belongs
   here. A project adapts the decorator through the `CACHE_RESULTS` setting and
   its hooks (`KEY_ENCODER`, `LOGGING_ENABLED`, `VERBOSE_LOGGING`,
   `LOG_PREFIX`), as Smarter does in `smarter/smarter/lib/cache/hooks.py`.
4. **Never key by `str()`.** An argument the key encoder doesn't know runs the
   function uncached and logs an error. `str()` of two model rows can be equal,
   and `<Foo object at 0x...>` differs in every process.
5. **Never log a result or a secret.** Logs name the function and the type of
   its result. Arguments are logged only when verbose logging is on.
6. **Protect existing cached entries.** Changing the key format (`make_key()`,
   `normalize()`, the encoder's output for an existing type) or the value of
   `CACHE_NONE_SENTINEL` makes every entry in every user's cache unreadable.
   That needs a major release, with a `BREAKING CHANGE:` footer
   (`cache-results-release`), and tests that pin the old behavior must change
   deliberately, not by accident.
7. **The pre-commit hooks are the lint standard.** See `cache-results-code-quality`.
8. **Coverage:** at least 95% (`pyproject.toml` fails the report below it).
9. **This repository is public.** No credentials, private hostnames or
   customer data in code, tests, docs or skills.
10. **Use this repository's own `venv/`**, built by `make init` from
    `requirements/local.txt`, never another project's (e.g. `../smarter/venv`).
    A requirement is added to `requirements/in/*.in` (constraints in
    `constraints.in`), then compiled with `make python-requirements`; never
    `pip install` something that isn't in them. See `cache-results-release`.
11. **Decisions are recorded as ADRs** in `docs/source/adr/`. Read the one that
    covers what you are changing, and add one, or supersede one, when you make
    a decision of that size. See `cache-results-sphinx-docs`.

## When the user reports that something didn't happen

If the user says that something didn't happen, e.g. "it did not create a
release", "PyPI still has the old version" or "Smarter still logs the old
message", that is a problem to fix, not a claim to debate. Don't answer with
evidence that it did happen somewhere else, e.g. a prerelease on `alpha` or
TestPyPI when they mean `main` and PyPI, or a release that Smarter's pin
doesn't use yet. Find out what is missing from their point of view, why, and
fix it, or hand them the one command or click that fixes it.

## Pattern-first workflow

The package is small and consistent, and almost every change has a precedent.

1. Identify what kind of change it is: a setting or hook, a type the key
   encoder knows, a wrapper behavior (sync and async), a log message, a test.
2. Find the existing code of the same kind, and its tests and docs. A sync
   change usually has an async twin in `decorators.py`.
3. Copy their structure, naming, docstrings, logging and error handling.
   Don't introduce a new pattern when one exists.
4. Make the change, then its tests, docstrings, README and docs.
5. Run the hooks and the tests, and fix what they find.

When existing code disagrees with these skills, the code that is newest and
consistent with most of the package wins. Say so in your summary.

## Architecture, and why

- **A key is** `KEY_PREFIX` + `v<VERSION>:` + `module.qualname()_` + 32 hex
  characters of a SHA-256 of the qualified name and the arguments, bound to the
  signature with defaults applied, normalized and serialized as canonical JSON.
  Binding makes `f(1)`, `f(a=1)` and `f(1, b=2)` share an entry, so that
  `invalidate()` finds what the call cached however each was written.
- **The qualified name records where a function is defined, not its caller.**
  A function defined inside an inherited classmethod has one qualified name for
  every subclass, so it needs a `class_name: str = cls.__name__` parameter.
  The README documents this; keep it documented.
- **Instance methods are refused** at decoration time (`self` can't be a safe
  key). Classmethods are fine: `cls` is keyed by its qualified name.
- **`None` is stored as `CACHE_NONE_SENTINEL`**, a string, because many
  backends can't tell a stored `None` from a miss. Reads pass
  `CACHE_MISS_SENTINEL` as the default.
- **Threads in one process that miss the same key wait** on a per-key `RLock`
  in a `WeakValueDictionary`. Not lock striping: nested cached calls on
  different keys could deadlock. Other processes and async callers don't wait.
- **Settings are read on every call**, so `override_settings` works, and a
  dotted path is imported once (`lru_cache`).

## Django traps

- **Import `django.core.cache` only inside functions.** Decorators run at
  import time, often while Django is starting, and touching the cache then can
  leave it on a local-memory backend that persists nothing. For the same
  reason, `cache_ready()` (`apps.ready`) gates every read and write: calls
  before it run uncached.
- **Async code can't touch the database.** Django raises
  `SynchronousOnlyOperation`. A project's logging hook may query a feature
  flag, so the async wrapper calls the log functions through `sync_to_async`.
- **Django's `BaseCache.aget()` and `aset()` are `sync_to_async(...,
thread_sensitive=True)`**: every call queues on one thread. The wrapper uses a
  backend's own async methods only when it overrides them
  (`_has_native_async()`), and otherwise runs `get()`/`set()` in the thread
  pool (`thread_sensitive=False`). django-redis has no native async methods.
- **`DEFAULT_TIMEOUT` is a bare `object()`** that cache methods accept as
  "the alias's own timeout". `conf.timeout` casts it to `Optional[float]`,
  which the cache methods' signatures declare.
- **Supported versions** are Django 4.2 and newer on Python 3.10 and newer,
  tested on each Django release's own Python range (`ci.yml`). A new Django or
  Python release means a new matrix entry, a classifier in `pyproject.toml`,
  and the README's badge text.

## Logging

```python
logger = logging.getLogger(__name__)  # standard library
logger.error("%s %s() runs uncached: %s", _prefix(), func.__qualname__, reason)
```

- Every message starts with `_prefix(event)`, which `CACHE_RESULTS["LOG_PREFIX"]`
  formats (Smarter colors it), then the unformatted function name with `()`.
- %-style arguments, never f-strings: a message that isn't emitted is never
  formatted, which matters on a path as hot as a cache read.
- Levels: hits, misses and invalidations at `info` only when logging is
  enabled, otherwise `debug`. A key failure is an `error` once per process for
  each function and reason (`_key_errors_logged`), then `debug`, so that a hot
  path can't flood the log.
- Name types, never values. `describe_key_error()` never includes an argument.

## How Smarter uses the package

Smarter (`../smarter`) pins `cache-results` in `smarter/requirements/` and
imports `cache_results` and `lazy_cache` from it. Its `CACHE_RESULTS` setting
names this package's `colors.log_prefix` and Smarter's own hooks in
`smarter/smarter/lib/cache/hooks.py`: a waffle-switched `LOGGING_ENABLED` and
a Pydantic-aware `KEY_ENCODER`. Those stay in Smarter because they need
django-waffle and Pydantic. **Never add them here**: a hook that needs another
library belongs to the project that uses that library. A release reaches
Smarter when its pin is bumped (`cache-results-release`).

To see how a change here lands there, read the local checkout `../smarter`
(read only, unless the user asks you to change it), not GitHub. First check
that it is current:
`../smarter/skills/smarter-project-repositories/scripts/repos-status.sh smarter`
(read only: its branch, uncommitted changes, and whether it matches its
remote). A checkout that is behind can mislead you. Say so, and give the user
the `git -C ../smarter pull` to run; rule 1 applies there too. Smarter has its
own `CLAUDE.md` and skills: read them before changing anything there, and
follow their rules, e.g. its tests run in its Docker containers, not on the
host.

## Which skill to load

| Task                                                         | Skill                        |
| ------------------------------------------------------------ | ---------------------------- |
| Tests, the version matrix, Redis, coverage                   | `cache-results-testing`      |
| Docstrings                                                   | `cache-results-docstrings`   |
| Type annotations, `Any`, mypy                                | `cache-results-typing`       |
| Lint, format, pre-commit                                     | `cache-results-code-quality` |
| Writing a commit message                                     | `cache-results-git-commits`  |
| CI, Codecov, semantic-release, versions, PyPI, Smarter's pin | `cache-results-release`      |
| Documentation pages                                          | `cache-results-sphinx-docs`  |

## Definition of done

- The change follows the existing code, and keeps rules 3 to 6.
- Tests cover it, and you ran `make test`, `make test-redis` and
  `make coverage` yourself. Report failures honestly, including pre-existing
  ones.
- `make typecheck` and the pre-commit hooks pass.
- Public objects have reST docstrings, and the README describes any change a
  user can see.
- Your summary says whether Smarter needs its pin bumped, or other changes, to use it.
- Your summary says what changed, what you verified, and what you skipped.
