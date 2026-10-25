ADR-021: Publish the Docs Site From the Release Workflow
========================================================

Status
------
Accepted

Context
-------
The Release workflow tags a version and publishes it to PyPI by itself, but
the documentation site was published only when a maintainer ran
``make sphinx-publish`` with AWS credentials. After a release, the site could
describe a version older than PyPI's for as long as nobody remembered, as it
did after 0.2.0, whose new ``lazy_cache`` and ``colors`` pages other projects'
docs already linked to.

Decision
--------
The Release workflow's ``publish-docs`` job publishes the site after every
release from ``main``, once ``verify-pypi`` has installed the release back
from PyPI. It builds the site from the release tag, with warnings as errors,
syncs it to the docs bucket, invalidates CloudFront, and waits until the site
shows the new version.

The job signs in to AWS with GitHub's OIDC token, as an IAM role that
``terraform/docs`` creates. Only a job in the repository's ``docs``
environment, which allows only ``main``, can assume it, and it can only sync
the docs bucket and invalidate its distribution. The role, bucket and
distribution are repository variables, because this public repository must
not contain an account or distribution id. ``PUBLISH_DOCS`` turns the job on.

Alternatives Considered
-----------------------
- An AWS access key in the repository's secrets: a long-lived credential that
  can leak, and must be rotated by hand.
- Publishing on every push to ``main``: the site would document commits that
  aren't on PyPI yet, or never will be.
- Publishing prereleases from ``alpha`` and ``beta``: the site shows one
  version, and it should be the one that ``pip install cache-results`` installs.

Consequences
------------
- **Positive:**

  - The site always documents the version on PyPI, with no step to forget.
  - No AWS credential is stored in GitHub, and the role can't touch anything
    but the site.

- **Negative:**

  - The role and GitHub's OIDC provider are more AWS resources to keep in
    Terraform, and the provider is shared by the whole account.
  - A docs fix between releases is still published by hand, with
    ``make sphinx-publish``.

Related ADRs
------------
- :doc:`ADR-011: CI/CD <011-ci-cd>`
- :doc:`ADR-018: Documentation <018-documentation>`
- :doc:`ADR-019: Release on Every Push <019-release-on-push>`
