"""Collection of description files for common Python environments."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import warnings

from typing import Any
from collections.abc import Iterator, Mapping


if sys.version_info >= (3, 11):
    from importlib.resources.abc import Traversable
else:
    from importlib.abc import Traversable


def _generate_data() -> Traversable:
    """This helper generates the data when running the module from source."""
    srcdir = pathlib.Path(__file__).parent.parent
    generation_script = srcdir / 'generate-data.py'
    datadir = srcdir / '.data'

    if not datadir.exists():
        warnings.warn(f'Running from source and no data found in {os.fspath(datadir)}, generating it.')
        datadir.mkdir()
        try:
            subprocess.check_call([sys.executable, os.fspath(generation_script), os.fspath(datadir)])
        except Exception:
            shutil.rmtree(datadir)
            raise

    return datadir


def _is_running_from_source() -> bool:
    # The data submodule is not present in the source — it is created by Meson
    # when it generates the data — so when we are running the module from source
    # (instead of the installed package), it is missing.
    try:
        import python_environments.data  # type: ignore[import-not-found]  # noqa: F401
    except ModuleNotFoundError:
        return True
    return False


def _get_data_dir() -> Traversable:
    if _is_running_from_source():
        return _generate_data()

    # Delay the import, so that importing the main package does not error out
    # on older unsupported Python versions. While the main module itself is only
    # meant to run on newer Python versions, we ship a script in
    # python_environments.generate to introspect the Python environment and
    # generate the description data. This script is expected to run on older
    # Python versions, its version compatibility is kept on a best-effort basis.
    import importlib.resources

    return importlib.resources.files('python_environments.data')


def _read_data() -> Mapping[str, Mapping[str, Any]]:
    data_dir = _get_data_dir()
    return {
        file.name.removesuffix('.json'): json.loads(file.read_text())
        for file in data_dir.iterdir()
        if file.is_file()
    }


class ImageData(Mapping):  # XXX: Cannot inherit from Protocol and Mapping
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(image={self.image!r}, manifest={self.manifest!r})'

    @property
    def image(self) -> str:
        """Image name, including the version (eg. ``debian:10``)."""
        raise NotImplementedError

    @property
    def manifest(self) -> str:
        """Manifest of the container from where this data was gathered."""
        raise NotImplementedError


class _ImageData(ImageData):
    def __init__(self, image: str, manifest: str, data: Mapping[str, Any]) -> None:
        self._image = image
        self._manifest = manifest
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    @property
    def image(self) -> str:
        return self._image

    @property
    def manifest(self) -> str:
        return self._manifest


_DATA: dict[str, Mapping[str, Any]] = {}


def get(name: str) -> ImageData:
    """Get the bundled data for the specified image.

    :param name: Image name, including the version (eg. ``debian:10``).
    """
    global _DATA
    if not _DATA:
        _DATA |= _read_data()

    return _ImageData(name, _DATA[name]['metadata']['manifest'], _DATA[name]['data'])
