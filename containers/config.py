from __future__ import annotations

import dataclasses
import pathlib
import sys
import warnings

from typing import Any, Literal, TypedDict

import containers


if sys.version_info >= (3, 11):
    import tomllib

    from typing import Required, Self
else:
    import tomli as tomllib

    from typing_extensions import Required, Self


class RepoDict(TypedDict):
    base: str


class StaticVersionDict(TypedDict):
    type: Literal['static']
    value: str


class RollingVersionDict(TypedDict):
    type: Literal['rolling']


# XXX: Using total+Required insted of NotRequired because
#      'from __future__ import annotations' breaks TypedDict.__required_keys__
#      See https://github.com/python/cpython/issues/97727
class TemplateDict(TypedDict, total=False):
    name: Required[str]
    data: dict[str, Any]


class ImageDict(TypedDict):
    name: str
    version: str | StaticVersionDict | RollingVersionDict
    template: TemplateDict


class ConfigDict(TypedDict):
    repos: list[RepoDict]
    images: list[TemplateDict]


@dataclasses.dataclass
class Config:
    repos: list[containers.Repo]
    images: containers.ImagesContainer[containers.Image]

    @classmethod
    def _build_template(cls, data: dict[str, Any]) -> containers.Template:
        template_data = data.get('data', {})
        return containers.Template(
            name=data['name'],
            data={
                key.replace('-', '_'): value
                for key, value in template_data.items()
            },
        )

    @classmethod
    def _build_image(cls, data: dict[str, Any]) -> containers.Image:
        if isinstance(data['version'], str):
            version = { 'type': 'static', 'value': data['version'] }
        else:
            version = data['version']

        template = cls._build_template(data['template'])

        if version['type'] == 'static':
            return containers.Image(
                name=data['name'],
                version=version['value'],
                template=template,
            )
        elif version['type'] == 'rolling':
            return containers.RollingImage(name=data['name'], template=template)

    @classmethod
    def from_config_file(cls, file: pathlib.Path) -> Self:
        with file.open('rb') as f:
            data = tomllib.load(f)

        try:
            import typing_validation
            import typing_validation.validation
        except ModuleNotFoundError as e:
            if e.name != 'typing_validation':
                raise
            warnings.warn('the typing_validation package is not available, skiping environments.toml validation')
        else:
            try:
                typing_validation.validate(data, ConfigDict)
            except typing_validation.validation.UnsupportedTypeError as e:
                warnings.warn(f'got UnsupportedTypeError during environments.toml validation: {e}')

        return cls(
            repos=[containers.Repo(entry['base']) for entry in data['repos']],
            images=containers.ImagesContainer([
                cls._build_image(image_config) for image_config in data['images']
            ]),
        )
