# Canonical Git Commit

The commit that created this package, `5357102` (`feat: port the
cache_results decorator from Smarter`), in the required format. What makes it
a good one:

- The type is `feat`, because it introduced a new package: the kind of change
  `feat` is reserved for. semantic-release counts it as a minor release.
- The first paragraph explains why the change exists, where the code came from,
  and what it does not do yet (no PyPI release, Smarter keeps its copy).
- Each area gets a heading paragraph, then one bullet per change, with the
  reason for each non-obvious decision: why `CACHE_NONE_SENTINEL` kept its
  value, why module docstrings start with a sentence, how `.flake8` differs
  from Smarter's.
- The tests are described by what they prove, not just listed.
- It ends with the status: the versions and caches tested, and what is not
  done yet.
- Lawrence McDaniel is the author, and Claude is the co-author.

Note that the body could not use backticks, `$` or `!`: they are inside double
quotes in zsh.

```console
git commit --author="Lawrence McDaniel <lpm0073@gmail.com>" \
  -m "feat: port the cache_results decorator from Smarter" \
  -m "The cache_results decorator was written for Smarter (github.com/smarter-sh/smarter), in smarter/smarter/lib/cache. Its decorator, keys and settings were reworked there to depend only on Django, so that it could be published on its own, as Smarter's ADR-018 intends. This commit ports those modules into this repository as the cache-results package, with the import name cache_results, and adds the tests, packaging, lint configuration, CI and documentation of a standalone library. It is not yet published to PyPI, and Smarter keeps its own copy until it is." \
  -m "Package (src/cache_results/):" \
  -m "- decorators.py, keys.py and conf.py are Smarter's smarter.lib.cache modules of the same names, with every reference to Smarter removed from their docstrings. Behavior is unchanged: keys are the module, qualified name and a hash of the bound arguments; arguments the key encoder doesn't know run the function uncached and log an error once, rather than be keyed by str(); None results are cached; async functions read and write the cache without blocking the event loop; threads that miss one key wait for the first to compute it; calls before Django's apps are ready run uncached; and the CACHE_RESULTS setting configures the cache alias, timeout, key prefix and version, key encoder and logging hooks.
- sentinels.py replaces Smarter's cache_sentinel.py. CacheSentinel no longer pickles and hashes its name for its repr. CACHE_NONE_SENTINEL keeps the exact value Smarter stores, so that entries Smarter caches today stay readable once it installs this package.
- __init__.py exports cache_results, CacheKeyEncoder, CacheKeyArgumentError and __version__. py.typed marks the package as typed.
- pyupgrade rewrote the type hints for Python 3.10 (X | None). Module docstrings start with a sentence rather than a dotted title, which pydocstringformatter would capitalize." \
  -m "Tests (tests/):" \
  -m "- test_decorators.py, test_keys.py and test_conf.py are ported from Smarter's suite, as pytest-django SimpleTestCases. Smarter's LazyCache tests stay in Smarter. The waffle-switch logging test is now a CACHE_RESULTS VERBOSE_LOGGING test, and the Smarter settings test is replaced by KEY_ENCODER tests with a project's own encoder, given as a class and as a dotted path.
- test_package.py covers the public api, the version and the sentinels, including that CACHE_NONE_SENTINEL never changes.
- tests/settings.py uses Django's local-memory cache, or Redis through django-redis when CACHE_RESULTS_TEST_REDIS_URL is set." \
  -m "Packaging and tooling:" \
  -m "- pyproject.toml: PEP 621 metadata built with hatchling, MIT license, Python 3.10 or newer, Django 4.2 or newer and asgiref as the only dependencies, test and redis extras, and the version read from src/cache_results/__version__.py, which semantic-release will write.
- The pre-commit hooks (pydocstringformatter, pyupgrade, codespell, Prettier, black, flake8, isort, autoflake, bandit, pre-commit-hooks, commitlint) follow Smarter's Python hooks. Unlike Smarter's .flake8, which selects only C101, this .flake8 runs flake8's checks, without a complexity limit.
- .github/workflows/test.yml runs the tests with coverage on six pairs of Python and Django versions, from 3.10 with 4.2 to 3.14 with 6.0, and once against a Redis service.
- Makefile: init, test, coverage, lint and clean." \
  -m "Docs: README.md describes the features, installation from GitHub until the package is on PyPI, the argument rules, the class_name parameter of functions defined in inherited classmethods, the settings and decorator options, development, and contributing. CLAUDE.md gives coding agents the hard rules: no project-specific code, no str() keys, no logged results or secrets, and no change to the key format or CACHE_NONE_SENTINEL without a major release. CODE_OF_CONDUCT.md is Smarter's." \
  -m "Status: 55 tests pass with 99% coverage on Python 3.14 with Django 6.1.2, on Python 3.10 with Django 4.2.30, on Python 3.12 with Django 5.2.18, and against Redis. mypy with django-stubs finds no issues, the pre-commit hooks pass, and the wheel builds with the package, py.typed and the license. The CI workflow has not run yet. Not yet done: the Sphinx documentation site, and the semantic-release and PyPI publishing workflows." \
  -m "Co-authored-by: Claude <noreply@anthropic.com>"
```

Notes on the format:

- A bullet list goes in a single `-m` with real newlines between bullets. A
  paragraph gets its own `-m`.
- Inner double quotes are escaped (`\"data\"`). Backticks are avoided
  altogether.
- The header is within 72 characters, measured with `wc -c`.
