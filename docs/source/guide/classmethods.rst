Methods and Nested Functions
============================

Classmethods
------------

Put ``@cache_results`` below ``@classmethod``:

.. code-block:: python

    class Report:
        @classmethod
        @cache_results(timeout=600)
        def totals(cls, year: int) -> dict: ...

``cls`` is part of the key, identified by its qualified name, so a subclass's
results are cached apart from its parent's. Pass the class to ``invalidate()``,
because it receives the arguments of the undecorated function:

.. code-block:: python

    Report.totals.invalidate(Report, 2026)

Static methods and plain functions work as you would expect. Put
``@cache_results`` below ``@staticmethod`` too.

Instance methods are refused
----------------------------

Decorating a method whose first parameter is ``self`` raises ``TypeError`` when
the class is defined:

.. code-block:: python

    class Book(models.Model):
        @cache_results()             # TypeError
        def summary(self) -> dict: ...

``self`` would be part of the key, and an instance can't be part of a safe key.
Cache a function of the values that matter instead, and call it from the
method:

.. code-block:: python

    @cache_results()
    def book_summary(book_id: int) -> dict: ...


    class Book(models.Model):
        def summary(self) -> dict:
            return book_summary(self.pk)

Functions defined inside an inherited classmethod
-------------------------------------------------

A function's qualified name records where it is defined, not who calls it. A
cached function defined inside a classmethod of a base class has the **same**
qualified name for every subclass, so without help, ``Book`` 5 and ``Author`` 5
would share one entry. Give it the class name as a parameter, so that it is
part of the key:

.. code-block:: python

    class CachedModel(models.Model):
        class Meta:
            abstract = True

        @classmethod
        def get_cached(cls, pk: int):
            @cache_results()
            def _get(pk: int, class_name: str = cls.__name__):
                return cls.objects.get(pk=pk)

            return _get(pk)

The nested function is created again on every call, which is fine: its key
depends on its module, qualified name and arguments, not on the function
object. For the same reason, ``_get.invalidate(pk)`` called on a new copy of
the nested function clears the entry.
