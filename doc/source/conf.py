import sys
import macpie


# Project --------------------------------------------------------------

project = "MACPie"
copyright = "2022, Regents of the University of California"
version = release = macpie.__version__


# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx_tabs.tabs",
    "numpydoc",
    "sphinx_click",
]
autosummary_generate = True
intersphinx_mapping = {
    "networkx": ("https://networkx.org/documentation/stable/", None),
    "openpyxl": ("https://openpyxl.readthedocs.io/en/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "tablib": ("https://tablib.readthedocs.io/en/stable/", None),
    "xlsxwriter": ("https://xlsxwriter.readthedocs.io/", None),
    "python": ("https://docs.python.org/3/", None),
}
pygments_style = "sphinx"
# Fix issue with warnings from numpydoc (see discussion in PR #534)
numpydoc_show_class_members = False


def setup(app):
    # these modules are actually module aliases, so need
    # to fake the python module system here, otherwise
    # autodoc can't document these modules properly
    sys.modules["macpie.datetimetools"] = macpie.datetimetools
    sys.modules["macpie.itertools"] = macpie.itertools
    sys.modules["macpie.lltools"] = macpie.lltools
    sys.modules["macpie.openpyxltools"] = macpie.openpyxltools
    sys.modules["macpie.pathtools"] = macpie.pathtools
    sys.modules["macpie.shelltools"] = macpie.shelltools
    sys.modules["macpie.strtools"] = macpie.strtools
    sys.modules["macpie.tablibtools"] = macpie.tablibtools
    sys.modules["macpie.validatortools"] = macpie.validatortools
    sys.modules["macpie.xlsxwritertools"] = macpie.xlsxwritertools


# HTML -----------------------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "show_prev_next": False,
    "page_sidebar_items": ["search-field", "page-toc"],
    "github_url": "https://github.com/UCSFMemoryAndAging/macpie",
}
html_logo = "_static/logo/UCSF_Logo_21_Navy_300dpi_RGB.png"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
html_sidebars = {
    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"],
    "index": [],
}
