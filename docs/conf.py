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
    'sphinx.ext.intersphinx',
    'local_project_info',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}

html_theme = 'sphinx_material'
html_title = project

html_theme_options = {
    'repo_url': 'https://github.com/FFY00/python-environments/',
    'repo_name': 'python-environments',
    'color_primary': 'light-green',
    'color_accent': 'light-green',
    'master_doc': False,
    'nav_title': 'Python Environments',
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
