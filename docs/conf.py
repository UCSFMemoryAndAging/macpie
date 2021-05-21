from macpie import __version__

# -- Project information -----------------------------------------------------

project = 'MACPie'
copyright = '2021, Regents of the University of California'
author = 'Regents of the University of California'
release = __version__

# -- General configuration ---------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_tabs.tabs",
]
autodoc_default_options = {
    'member-order': 'bysource'
}
autodoc_typehints = "description"
intersphinx_mapping = {
    "networkx": ("https://networkx.org/documentation/stable/", None),
    "openpyxl": ("https://openpyxl.readthedocs.io/en/stable/", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable/", None),
    "tablib": ("https://tablib.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
    "extra_nav_links": {
        "Source Code": "https://github.com/UCSFMemoryAndAging/macpie",
        "PyPI Releases": "https://pypi.org/project/macpie/"
    }
}
