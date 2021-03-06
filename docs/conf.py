# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'lwsspy.gcmt3d'
copyright = '2021, Lucas Sawade'
author = 'Lucas Sawade'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.autosummary",
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx.ext.napoleon',
]

source_suffix = {
    '.rst': "restructuredtext",
    '.md': 'markdown',
    # '.txt': 'markdown',
}


numpydoc_show_class_members = False

# generate autosummary even if no references
autosummary_generate = True
autosummary_imported_members = True

html_static_path = ['_static']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "LWSSPY - GCMT3D"
html_logo = "chapters/figures/logo.png"
html_favicon = "chapters/figures/favicon.ico"

html_theme = 'pydata_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {
    "repository_url": "https://github.com/lwsspy/lwsspy.gcmt3d",
}

html_context = {
    "github_user": 'lwsspy',
    "github_repo": 'lwsspy.gcmt3d',
    "github_version": "master",
    "doc_path": "docs",
}

html_theme_options = {
    "external_links": [
        {"url": "http://www.globalcmt.org", "name": "Global CMT"}
    ],
    "github_url": "https://github.com/lwsspy/lwsspy.gcmt3d",
    "use_edit_page_button": True,
    "use_edit_page_button": True,
    "navigation_depth": 2,
}
