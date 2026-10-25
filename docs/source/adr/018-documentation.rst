ADR-018: Documentation
======================

Status
------
Accepted

Context
-------
Users need a guide and an api reference that match the installed version, at a
stable address. The api reference must come from the code, so that it can't
drift from it, and the site's hosting must be reproducible and reviewable.

Decision
--------
The documentation is a Sphinx site in ``docs/source``, with the Read the Docs
theme, published to https://docs.cache-results.smarter.sh/. The api reference is
generated from docstrings by autodoc. ``make sphinx-build`` treats every warning
as an error. The site is served by CloudFront from a private S3 bucket, with an
ACM certificate and Route53 records, all defined in Terraform in
``terraform/docs`` and changed only through it. ``make sphinx-publish`` uploads a
build and invalidates CloudFront. The AWS account id is read from the caller's
credentials at run time, and never committed.

Alternatives Considered
-----------------------
- Read the Docs' hosting, which builds on its own servers, with its own domain and ads on the free tier.
- GitHub Pages, which can't share the ``smarter.sh`` zone's certificates and records with the rest of the project's sites.
- Creating the AWS resources by hand, which leaves no record of how they are configured.

Consequences
------------
- **Positive:**

  - The api reference always matches the code it was built from.
  - The hosting can be reviewed, recreated or removed with Terraform.

- **Negative:**

  - Publishing needs AWS credentials for the account, so it is done by a maintainer, not by CI.
  - The site shows one version, the latest published.

Related ADRs
------------
- :doc:`ADR-014: Docstring Style <014-docstrings>`
- :doc:`ADR-011: CI/CD <011-ci-cd>`
