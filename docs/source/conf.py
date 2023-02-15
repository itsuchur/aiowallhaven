# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'aiowallhaven'
copyright = '2022, Dmitrii Efimov, Roman Berezkin'
author = 'Dmitrii Efimov, Roman Berezkin'
release = '0.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import aiowallhaven
print(dir(aiowallhaven))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme"
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'titles_only': False
}

# There are no static assets yet
# html_static_path = ['_static']

# --- https://github.com/readthedocs/readthedocs.org/issues/2569 -----------------
root_doc = 'index'
