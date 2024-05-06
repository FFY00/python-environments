from __future__ import annotations

import dataclasses
import datetime
import functools
import operator
import sys

from typing import Iterator, Type

import containers


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@dataclasses.dataclass
class Image:
    name: str
    version: str
    template: containers.Template

    def __post_init__(self) -> None:
        self.template.data |= {
            'image': self.name,
            'version': self.version,
        }

    @property
    def id(self) -> str:
        return f'{self.name}:{self.version}'

    @property
    def tags(self) -> list[str]:
        return [
            # upstream tag
            f'{self.name}:{self.version}',
            # source-versioned tag
            f'{self.name}:{self.version}-pc{containers.__version__}',
        ]


@dataclasses.dataclass
class RollingImage(Image):
    version: str = dataclasses.field(
        default=datetime.datetime.now().strftime('%Y%m%d.%H%M'),
        init=False,
    )

    @property
    def tags(self) -> list[str]:
        return super().tags + [f'{self.name}:latest']


class ImagesContainer:
    def __init__(self, images: list[Image]) -> None:
        self._images = {
            image.id: image
            for image in images
        }

    def __getitem__(self, image_id: str | list[str]) -> Image:
        if isinstance(image_id, str):
            return self._images[image_id]
        return [self._images[entry] for entry in image_id]

    def __iter__(self) -> Iterator[Image]:
        return iter(sorted(self._images.values(), key=operator.attrgetter('id')))

    @property
    def ids(self) -> list[str]:
        return list(self._images.keys())

    @functools.singledispatch
    def filter(
        self,
        match: Type[Image] | None = None,
        ignore: Type[Image] | None = None,
    ) -> Self:
        return self.__class__([
            image for image in self
            if (
                (not match or isinstance(image, match))
                and (not ignore or not isinstance(image, ignore))
            )
        ])
