import dataclasses
import pathlib
import shutil

from typing import Any

import jinja2

import containers


DATA_DEFAULTS = {
    'debian': {
        'has_distutils': False,
        'has_pypy2': False,
    },
}


@dataclasses.dataclass
class Template:
    name: str
    data: dict[str, Any]

    def __post_init__(self) -> None:
        self.data = DATA_DEFAULTS.get(self.name, {}) | self.data

    @property
    def path(self) -> pathlib.Path:
        return containers.TEMPLATES_PATH / self.name

    def _render_template_file(self, file: pathlib.Path, outdir: pathlib.Path) -> Any:
        template = jinja2.Template(
            file.read_text(),
            trim_blocks=True,
            keep_trailing_newline=True,
        )
        data = template.render(self.data)
        outdir.joinpath(file.stem).write_text(data)

    def _render_dir(self, template: pathlib.Path, outdir: pathlib.Path) -> None:
        outdir.mkdir(exist_ok=True, parents=True)
        for path in template.iterdir():
            if path.is_file():
                if path.suffix == '.jinja':
                    self._render_template_file(path, outdir)
                else:
                    shutil.copy2(path, outdir / path.name)
            else:
                self._render_dir(path, outdir / path.name)

    def render(self, path: pathlib.Path) -> None:
        self._render_dir(self.path, path)
