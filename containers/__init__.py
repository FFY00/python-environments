import pathlib
import sys


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


ROOT = pathlib.Path(__file__).parent.parent

sys.path.insert(0, ROOT)


import containers.env  # noqa: E402

from containers.config import Config  # noqa: E402
from containers.image import Image, RollingImage, ImagesContainer  # noqa: E402
from containers.repo import Repo  # noqa: E402
from containers.template import Template  # noqa: E402


with ROOT.joinpath('pyproject.toml').open('rb') as f:
    _pyproject_data = tomllib.load(f)

__version__ = _pyproject_data['project']['version']
if commit := containers.env.get_commit():
    __version__ += f'-{commit[:6]}'


BUILD_PATH = ROOT / 'containers' / 'out'
TEMPLATES_PATH = ROOT / 'containers' / 'templates'
PYTHON_PATH = ROOT / 'python'
ENVIRONMENTS_TOML_PATH = ROOT / 'environments.toml'


__all__ = [
    'ROOT',
    'BUILD_PATH',
    'TEMPLATES_PATH',
    'ENVIRONMENTS_TOML_PATH',
    # Re-exports
    'Config',
    'Image',
    'RollingImage',
    'ImagesContainer',
    'Repo',
    'Template',
]
