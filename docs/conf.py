import os
import sys

import containers


sys.path.insert(0, os.fspath(containers.ROOT / 'docs' / 'extensions'))
sys.path.insert(0, os.fspath(containers.PYTHON_PATH))


project = 'python-environments'
copyright = '2024, Filipe Laíns'
author = 'Filipe Laíns'

version = release = containers.__version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_toolbox.collapse',
    'local_project_info',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}

html_theme = 'sphinx_material'
html_title = project

html_static_path = ['_static']
html_css_files = [
    'css/datadetails-style.css',
    'css/fix-pre-overflow.css',
    'css/fix-table-layout.css',
    'css/highlight-margin.css',
]

html_theme_options = {
    'repo_url': 'https://github.com/FFY00/python-environments/',
    'repo_name': 'python-environments',
    'color_primary': 'light-green',
    'color_accent': 'light-green',
    'master_doc': False,
    'nav_title': 'Python Environments',
    # The theme mistakenly sets this value to "Contents" (with the quote) in
    # theme.conf, where the quotes are interpreted as part of the string. Set
    # it again here, but without quotes, so that the value is correct.
    'localtoc_label_text': 'Contents',
}

html_sidebars = {
    '**': [
        'logo-text.html',
        'globaltoc.html',
        'localtoc.html',
        'searchbox.html',
    ]
}

html_show_sourcelink = False
