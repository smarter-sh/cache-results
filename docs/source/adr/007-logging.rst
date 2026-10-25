ADR-007: Logging
================

Status
------
Accepted

Context
-------
Cache hits, misses and invalidations are useful when debugging, and noise the
rest of the time, so a project must be able to turn them on and off.
Arguments and results can hold personal data or secrets.

Decision
--------
The package logs with the standard library, to the ``cache_results.*`` loggers.
Hits, misses and invalidations are logged at ``info`` only when the decorator's
``logging_enabled`` or the ``LOGGING_ENABLED`` hook is on, and at ``debug``
otherwise. Messages start with a prefix that the ``LOG_PREFIX`` hook can format.
They name the function and the **type** of its result, never the result.
Arguments are logged only when ``VERBOSE_LOGGING`` is on. A failed key is logged
as an error once per process for each function and reason, then at ``debug``.

Alternatives Considered
-----------------------
- A feature-flag library to switch logging on, which would add a dependency.
- Log results, which is convenient and leaks data.

Consequences
------------
- **Positive:**

  - Quiet by default, and a project can turn logging on at runtime through its own hook.
  - Logs are safe to ship to an aggregator.

- **Negative:**

  - Debugging a wrong result needs verbose logging or a debugger, not the default logs.

Related ADRs
------------
- `Smarter ADR-011: Logging <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/011-logging.rst>`__
- :doc:`ADR-004: Settings and Hooks <004-settings-and-hooks>`
