# pylint: disable=invalid-name,redefined-builtin,wrong-import-position
"""
Sphinx configuration of the cache-results documentation, published to https://docs.cache-results.smarter.sh/.

Build it with ``make sphinx-build``, which treats every warning as an error,
and publish it with ``make sphinx-publish``.
"""

import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
sys.path.insert(0, REPO_ROOT)

# autodoc imports the package, and the package reads Django's settings when it runs.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django  # noqa: E402

django.setup()

from cache_results import __version__  # noqa: E402

# -- Project ------------------------------------------------------------------

project = "cache-results"
author = "Lawrence McDaniel"
copyright = f"{date.today().year}, {author}"  # noqa: A001
version = __version__
release = __version__

SITE_URL = "https://docs.cache-results.smarter.sh/"
GITHUB_URL = "https://github.com/smarter-sh/cache-results"

# -- General ------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "notfound.extension",
    "sphinx_sitemap",
]

templates_path: list[str] = []
exclude_patterns: list[str] = []
language = "en"

# docstrings carry their own :type: and :rtype: fields (ADR-014), so signatures keep the annotations.
autodoc_typehints = "signature"
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "show-inheritance": True}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", "https://docs.djangoproject.com/en/stable/_objects/"),
}

# copy only the code, not the prompts of console examples.
copybutton_prompt_text = r"\$ |>>> |\.\.\. "
copybutton_prompt_is_regexp = True

# -- HTML -----------------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = f"cache-results {__version__}"
html_short_title = "cache-results"
html_baseurl = SITE_URL
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "style_external_links": True,
    "prev_next_buttons_location": "both",
}
# the "Edit on GitHub" link at the top of each page.
html_context = {
    "display_github": True,
    "github_user": "smarter-sh",
    "github_repo": "cache-results",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}
html_show_sourcelink = False
html_copy_source = False
html_extra_path = ["_extra"]

# sitemap.xml lists every page under the site's root, without a version prefix.
sitemap_url_scheme = "{link}"

# 404.html is served by CloudFront for every missing page, at any depth, so its links are absolute.
notfound_urls_prefix = "/"
