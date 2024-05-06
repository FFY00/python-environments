"""Collection of description files for common Python environments."""

import sys


# We do this so that the python -m python_environments.generate works on older versions.
if sys.version_info >= (3, 9):  # project.requires-python
    from python_environments._init import get, ImageData

    __all__ = ['get', 'ImageData']
