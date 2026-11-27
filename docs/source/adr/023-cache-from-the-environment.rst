ADR-023: A Cache of Its Own, from the Environment
=================================================

Status
------
Accepted

Context
-------
:doc:`ADR-022 <022-a-cache-of-its-own>` let ``CACHE_RESULTS["CACHE"]`` give
the decorator a cache of its own. But a project's settings are one file that
every process runs, while the processes that need their own cache are only
some of them: in Smarter, the two workers whose Redis user may not write the
platform's cache. To give only those processes a cache of their own, the
project had to write code in its settings that decided, per process, whether
to set ``CACHE``, and built its configuration, often from its other caches.
That is the package's configuration, written in each project, and hard to read:
the setting looks the same in every process, and does something different in
some of them.

Which process gets which cache is a deployment's decision. A deployment already
gives each process its own environment, e.g. a Kubernetes Deployment's
environment variables, and its own credentials, from a Secret.

Decision
--------
The ``CACHE_RESULTS_CACHE`` environment variable holds the same configuration
as ``CACHE_RESULTS["CACHE"]``, as a JSON object, and wins over it. A
deployment sets it on the processes that need a cache of their own, and leaves
it unset on the others, which keep caching where they always have. The
project's settings don't change.

- Empty or unset, it is ignored.
- A value that isn't a JSON object with a ``BACKEND`` raises
  ``ImproperlyConfigured``. Its message names the variable, never its value,
  which holds the cache's credentials, and the JSON error that would quote the
  value isn't chained to it.
- It is parsed once per value, and the same value returns the same mapping, so
  each thread keeps the backend it built from it.

Alternatives Considered
-----------------------
- Code in the project's settings that sets ``CACHE`` for some processes: the
  package's configuration, written in every project that needs it, and a
  setting whose effect isn't what it reads as.
- The project's own mechanism for overriding a setting from the environment, if
  it has one: it replaces the whole ``CACHE_RESULTS`` setting, hooks and timeout
  included, so the deployment would have to repeat all of it.
- One variable per part (``CACHE_RESULTS_LOCATION``, ``CACHE_RESULTS_KEY_PREFIX``,
  ...): more variables to keep in step, and still not every part of a
  ``CACHES`` entry, e.g. ``OPTIONS``.

Consequences
------------
- **Positive:**

  - Which process caches where is decided where the processes are defined, in
    the deployment, next to their other credentials.
  - The project's settings stay the same in every process.

- **Negative:**

  - The variable holds credentials, so it belongs in a secret, not a plain
    manifest.
  - A setting can now be overridden from outside the settings, which a reader
    of the settings alone won't see. The documentation of ``CACHE`` says so.

Related ADRs
------------
- :doc:`ADR-004: Settings and Hooks <004-settings-and-hooks>`
- :doc:`ADR-022: A Cache of Its Own <022-a-cache-of-its-own>`
