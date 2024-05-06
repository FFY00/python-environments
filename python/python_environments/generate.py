"""Generation of introespection data for the current environment.

Usage
-----

.. code-block:: shell

    $ python -m python_environments.generate
"""

import argparse
import contextlib
import importlib
import importlib.abc
import json
import sys
import sysconfig
import zipimport
import warnings
import types


if False:  # TYPE_CHECKING
    from typing import Any, Iterator, Type  # noqa: F401


_REPORT_DATA = {
    'sys': [
        'api_version',
        'base_exec_prefix',
        'base_prefix',
        'byteorder',
        'builtin_module_names',
        'copyright',
        'dllhandle',
        'dont_write_bytecode',
        'executable',
        'flags',
        'float_info',
        'float_repr_style',
        'getunicodeinternedsize()',
        'getandroidapilevel()',
        'getdefaultencoding()',
        'getdlopenflags()',
        'getfilesystemencoding()',
        'getfilesystemencodeerrors()',
        'get_int_max_str_digits()',
        'getrecursionlimit()',
        'getswitchinterval()',
        'getwindowsversion()',
        'hash_info',
        'hexversion',
        'implementation',
        'int_info',
        'maxsize',
        'maxunicode',
        'meta_path',
        'path',
        'path_hooks',
        'path_importer_cache',
        'platform',
        'platlibdir',
        'pycache_prefix',
        'stdlib_module_names',
        'thread_info',
        'tracebacklimit',
        'version',
        'version_info',
        'warnoptions',
        'winver',
        '_emscripten_info',
    ],
    'sysconfig': [
        'get_config_vars()',
        'get_scheme_names()',
        'get_default_scheme()',
        'get_path_names()',
        'get_python_version()',
        'get_platform()',
        'is_python_build()',
        'get_config_h_filename()',
        'get_makefile_filename()',
        '_get_preferred_schemes()',
    ]
}

_PLATFORM_SPECIFIC_DATA = {
    'android': [
        'sys.getandroidapilevel()',
    ],
    'emscripten': [
        'sys._emscripten_info',
    ],
    'win32': [
        'sys.dllhandle',
        'sys.getwindowsversion()',
        'sys.winver',
    ],
}

_OPTIONAL_DATA = [
    'sys.tracebacklimit',
]


class LookupWarning(Warning):
    def __init__(self, key, exc):  # type: (str, Exception) -> None
        super().__init__(f'failed to lookup {key}: {exc}')


def _is_expected_missing(item):  # type: (str) -> bool
    # TODO: versionadded
    for platform, items in _PLATFORM_SPECIFIC_DATA.items():
        if platform != sys.platform and item in items:
            return True
    return item in _OPTIONAL_DATA


@contextlib.contextmanager
def _log_exceptions(item):  # type: (str) -> Iterator[None]
    try:
        yield
    except Exception as e:
        if not _is_expected_missing(item):
            warnings.warn(LookupWarning(key=item, exc=e))


def _lookup_item(module, item):  # type: (object, str) -> Any
    if item.endswith('()'):
        function_name = item[:-len('()')]
        function = getattr(module, function_name)
        return function()
    return getattr(module, item)


# TODO: Type return dictionary.
def introspect():  # type: () -> dict[str, dict[str, Any]]
    """Introspect the current environment.

    :returns: Environment data.
    """

    data = {}

    # data from list
    for module_name, items in _REPORT_DATA.items():
        module = importlib.import_module(module_name)
        for item_name in items:
            item_fullname = f'{module_name}.{item_name}'
            with _log_exceptions(item_fullname):
                value = _lookup_item(module, item_name)
            data[item_fullname] = value

    # custom data
    for scheme in sysconfig.get_scheme_names():
        item = f"sysconfig.get_paths('{scheme}')"
        with _log_exceptions(item):
            data[item] = sysconfig.get_paths(scheme)
    for key in ('prefix', 'home', 'user'):
        item = f"sysconfig.get_preferred_scheme('{key}')"
        with _log_exceptions(item):
            data[item] = sysconfig.get_preferred_scheme(key)

    return data


class _Encoder(json.JSONEncoder):
    def _is_subclass_or_instance(self, o, cls):  # type: (object, Type[Any]) -> bool
        with contextlib.suppress(TypeError):
            return issubclass(o, cls)
        return isinstance(o, cls)

    def default(self, o):  # type: (object) -> str:
        if isinstance(o, (set, frozenset)):
            return list(o)
        if isinstance(o, types.SimpleNamespace):
            return vars(o)

        if self._is_subclass_or_instance(o, (
            importlib.abc.MetaPathFinder,
            importlib.abc.PathEntryFinder,
            importlib.abc.Loader,
            zipimport.zipimporter,
            types.FunctionType,
        )):
            return repr(o)

        try:
            super().default(o)
        except TypeError:
            warnings.warn(f'failed to encode {o}, using repr instead')
            return repr(o)


def _main():  # type: () -> None
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-to-file', required=False)
    args = parser.parse_args()

    data = introspect()
    json_data = _Encoder(sort_keys=True, indent=4).encode(data)

    if args.write_to_file:
        with open(args.write_to_file, 'w') as f:
            print(json_data, file=f)
    else:
        print(json_data)


if __name__ == '__main__':
    _main()
