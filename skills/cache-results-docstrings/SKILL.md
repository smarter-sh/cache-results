---
name: cache-results-docstrings
description: Use when writing or editing Python docstrings in cache-results. Docstrings are the package's api reference (Sphinx autodoc), so they follow Smarter's reStructuredText field-list style (:param:, :type:, :returns:, :rtype:, :raises:), the layout that pydocstringformatter enforces, and the rule that module docstrings start with a sentence.
---

# cache-results Docstrings

Docstrings explain the code to contributors, and become the package's api
reference through Sphinx autodoc (`cache-results-sphinx-docs`). The style is
Smarter's, so that Smarter's copy and this package read the same.

## Style: reStructuredText field lists

```python
def make_key(func: Callable, args: tuple, kwargs: dict, encoder: type[CacheKeyEncoder] = CacheKeyEncoder) -> str:
    """
    Return the cache key of one call of a decorated function.

    The key is the function's module and qualified name, and a 32-character
    SHA-256 hash of its bound, normalized and serialized arguments.

    :param func: The decorated function.
    :type func: Callable
    :param encoder: The JSON encoder for the arguments.
    :type encoder: type[CacheKeyEncoder]
    :return: The cache key.
    :rtype: str
    :raises CacheKeyArgumentError: If an argument can't be part of a key.
    """
```

- `:param:` for every parameter, with `:type:`, as the existing code does.
- `:return:` says what the value means, including `None` cases, with `:rtype:`.
- `:raises X:` for each exception a caller should handle.
- Never Google style (`Args:`).

## Layout (pydocstringformatter enforces it)

- Opening `"""` on its own line, then a **one-line summary ending with a
  period**, a blank line, then the body. A two-line summary is mangled: the
  formatter puts a period at the end of the first line.
- **pydocstringformatter capitalizes the first word.** A module docstring that
  starts with `cache_results.keys` becomes `Cache_results.keys`. Start module
  docstrings with a sentence ("Cache keys for the `@cache_results`
  decorator."), not a dotted-name title. Sphinx titles the module page itself.
  The same goes for a summary that starts with a name: put it in double
  backticks, or rephrase.

## Content

- **Module docstrings** say what the module is for. `__init__.py` and
  `decorators.py` show a `.. code-block:: python` example.
- **The decorator's docstring is the user manual**: what it caches, the
  argument rules, the `class_name` trap, concurrency, async, every option.
  Keep it in step with the README.
- **Say why** when it isn't obvious, e.g. why `django.core.cache` is imported
  inside a function, or why a lock isn't striped.
- **Never put an argument value or a result in an example of a log message.**
- Be accurate. Change the docstring in the same edit as the behavior.

## reST inside docstrings

- Double backticks for literals (settings, values, file names), and Sphinx
  roles for cross-references, e.g.:

  ```rst
  ``CACHE_RESULTS["TIMEOUT"]``
  :func:`cache_results.decorators.cache_results`
  :class:`~cache_results.keys.CacheKeyEncoder`
  :mod:`cache_results.conf`
  ```

  Don't reference Smarter's modules; this package's docs can't resolve them.

- Lists and code blocks need a blank line before them.

## Test docstrings

A test module has a one-line docstring naming what it tests
(`"""Tests of cache_results.keys, the cache keys of @cache_results."""`), and
each test a one-line docstring stating the behavior it proves.

## Verify

Run the pre-commit hooks on the file and review what pydocstringformatter
changed (`cache-results-code-quality`).
