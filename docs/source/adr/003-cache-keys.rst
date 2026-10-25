ADR-003: Cache Keys: Bound Arguments, Never str()
=================================================

Status
------
Accepted

Context
-------
A cache key must be the same for equal arguments, in every process, and
different for different ones, and two functions must never share one.
``str()`` of an arbitrary object is not such a key: two model rows can have the
same string, and an object without its own ``__str__``
(``<Foo object at 0x...>``) has a different one in every process.

Decision
--------
A key is the function's module and qualified name, then a 32-character SHA-256
hash of its arguments, bound to its signature with defaults applied,
normalized (dicts and lists kept apart, sets sorted, classes and dataclasses
tagged) and serialized as canonical JSON by ``CacheKeyEncoder``. The encoder
knows what Django's ``DjangoJSONEncoder`` knows, and **refuses everything
else**: such a call runs uncached and logs an error. Projects add types by
subclassing the encoder (``KEY_ENCODER``). Instance methods are refused at
decoration time, because ``self`` would be part of the key.

Alternatives Considered
-----------------------
- Fall back to ``str()`` for unknown objects, with a warning.
- Key by ``repr()`` or ``pickle``, which are no more stable across processes.
- Require hashable arguments and use ``hash()``, which is randomized per process for strings.

Consequences
------------
- **Positive:**

  - A cached result is never served for the wrong arguments.
  - ``f(1)``, ``f(a=1)`` and ``f(1, b=2)`` (when ``b`` defaults to 2) share an entry, so ``invalidate()`` finds it however the call was written.

- **Negative:**

  - Callers must pass plain values, such as ids, rather than model instances.
  - A function defined inside an inherited classmethod needs a ``class_name`` parameter: its qualified name is the same for every subclass.

Related ADRs
------------
- :doc:`ADR-002: Function Result Caching <002-function-result-caching>`
- :doc:`ADR-009: Compatibility <009-compatibility>`
