---
name: cache-results-testing
description: Use when writing, fixing or running the cache-results tests, or raising coverage. Covers pytest-django with SimpleTestCase and tests/settings.py, testing against the local-memory cache and Redis, the Python and Django version matrix, the traps (shared local-memory storage, errors logged once per process, async tests, patch points), coverage, and how to report results.
---

# cache-results Testing

## How to run

From the repository root, with this repository's own virtual environment,
`venv/`, which `make init` builds from `requirements/local.txt`. Never run
them in another project's environment, e.g. Smarter's `../smarter/venv`: it
hides missing or wrong dependencies.

```console
make test                          # local-memory cache
make test-redis                    # Redis, at REDIS_URL (default redis://localhost:6379/15)
make coverage                      # with a coverage report; fails below 95%
venv/bin/python -m pytest tests/test_keys.py -k sets   # one module or test
```

- Run the tests yourself, after every change, and report the counts. Never
  ask the user to re-run them.
- Read the pass and fail counts, not only the coverage table: a coverage
  report alone is not a result.
- **`make test-redis` clears its database.** Use a database nothing else uses,
  and check that it's empty first (`redis-cli -n 15 dbsize`). Never point it
  at a database that holds another application's data, e.g. Smarter's dev
  Redis uses database 1. That one needs a password:
  `make test-redis REDIS_URL=redis://:<password>@localhost:6379/15`.
- Change how the cache is read or written, and run both. They catch different
  bugs: Redis pickles values, the local-memory cache does too but shares one
  process.

## Other Python and Django versions

CI runs six pairs (`ci.yml`). To try one locally, make a throwaway virtual
environment outside the repository:

```console
python3.10 -m venv /tmp/venv-dj42
/tmp/venv-dj42/bin/pip install -e ".[test]" "Django~=4.2.0"
/tmp/venv-dj42/bin/python -m pytest -q -p no:cacheprovider
```

Under zsh, a loop over `"3.10 4.2"` pairs with `set -- $pair` doesn't split
the words. Use a shell function with two arguments.

## Layout and conventions

- One test module per source module: `keys.py` is tested by `tests/test_keys.py`.
  `test_package.py` covers `__init__.py` and `sentinels.py`.
- Tests are `django.test.SimpleTestCase`: there is no database
  (`DATABASES = {}` in `tests/settings.py`). A test that needs one is testing
  the wrong thing; use plain values.
- `TestCacheResults.setUp()` clears `caches["default"]` and
  `decorators._key_errors_logged`. Keep both.
- Change settings with `override_settings(CACHE_RESULTS={...})`, never by
  assigning to `settings`.
- Test names say what's being proven, and each test has a one-line docstring
  stating the behavior it proves.
- Prefer real behavior to mocks: decorate a small function in the test, call
  it, and count its calls. Mock only what can't be reached otherwise.

## Things that will bite you

- **Local-memory caches of one `LOCATION` share storage**, across instances
  and tests. A test's own `LocMemCache("name", {})` must `clear()` first.
- **Key errors are logged as `error` once per process** for each function and
  reason. A second identical call logs at `debug`: assert it with
  `assertNoLogs(..., level="ERROR")`, and clear `_key_errors_logged` in `setUp`.
- **Logger names** are module paths: `assertLogs("cache_results.decorators", ...)`.
- **Patch points** are module attributes the code reads at call time:
  `patch.object(decorators, "cache_ready", return_value=False)` and
  `patch.object(decorators, "get_cache", return_value=mock)`. A
  `MagicMock(wraps=decorators.get_cache())` spies on the real cache.
- **Async tests** run the coroutine with `asyncio.run()` inside a sync test.
  Don't make the test method `async`. A hook that touches the database fails in
  async code; the wrapper calls hooks through `sync_to_async`.
- **The concurrency test** uses `threading.Event`s, and a short sleep to let
  the second thread reach the lock. Keep its timeouts, so that a regression
  fails rather than hangs.
- **Pinned values are promises.** `test_none_sentinel_is_stable` and the key
  format tests protect users' cached entries. Don't update them to make a
  change pass: a change that breaks them is a major release
  (`cache-results-development`, rule 6).

## Coverage

At least 95%, with branch coverage (`pyproject.toml`). CI uploads every job's
`coverage.xml` to Codecov, flagged `locmem` or `redis`. Test through the public
interface, the decorator and `invalidate()`, rather than private helpers, except
where a helper is a documented patch point.

## Reporting

Report the pass, fail and skip counts honestly, the coverage, which cache and
which Python and Django versions you ran, and anything you didn't run. Name
pre-existing failures and separate them from anything your change caused.
Confirm "pre-existing" by running the test on unchanged code, e.g. a copy of
the repository in your scratchpad with the changed files replaced by
`git show HEAD:<path>`: don't assume it. Never `git stash` or `git checkout`
to do so.
