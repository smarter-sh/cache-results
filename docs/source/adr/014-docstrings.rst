ADR-014: Docstring Style
========================

Status
------
Accepted

Context
-------
Docstrings are read by contributors, and rendered by Sphinx autodoc as the api
reference. They must render without translation.

Decision
--------
Docstrings use reStructuredText field lists:
``:param:``, ``:type:``, ``:return:``, ``:rtype:`` and ``:raises:``. The
pydocstringformatter pre-commit hook enforces the layout: an opening ``"""`` on
its own line, then a one-line summary that ends with a period. Because the hook
capitalizes the first word, module docstrings start with a sentence rather than
the module's dotted name.

Alternatives Considered
-----------------------
- Google or NumPy style, which need the napoleon extension and mix a second syntax into reST.

Consequences
------------
- **Positive:**

  - The api reference renders directly from the code.

- **Negative:**

  - ``:type:`` fields repeat the annotations.

Related ADRs
------------
- `Smarter ADR-029: Docstrings <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/029-docstrings.rst>`__
- :doc:`ADR-015: Annotations <015-annotations>`
