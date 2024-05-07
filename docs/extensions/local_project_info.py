import itertools
import pprint
import types

from typing import Any

import docutils.nodes as dn
import docutils.parsers.rst
import sphinx.addnodes
import sphinx.application
import sphinx.util.typing
import sphinx_toolbox.collapse

import containers
import python_environments


config = containers.Config.from_config_file(containers.ENVIRONMENTS_TOML_PATH)
# TODO: Figure out repo selection instead of harcoding.
repo = config.repos[0]
# TODO: Figure out how rolling images should be supported.
non_rolling_images = config.images.filter(ignore=containers.RollingImage)


class ImageList(docutils.parsers.rst.Directive):
    def _list_item(self, image: containers.Image) -> dn.list_item:
        repo_image_name = f'{repo.base}/{image.name}'
        if not isinstance(image, containers.RollingImage):
            repo_image_name += f':{image.version}'
        return dn.list_item('', dn.literal(text=repo_image_name))

    def run(self) -> list[dn.Node]:
        list_node = dn.bullet_list('', *[
            self._list_item(image)
            for image in config.images
        ])
        return [list_node]


class ImageData(docutils.parsers.rst.Directive):
    def _row(self, items: tuple[dn.Node | list[dn.Node], ...]) -> dn.row:
        return dn.row('', *[
            dn.entry('', *item) if isinstance(item, list) else dn.entry('', item)
            for item in items
        ])

    def _table(
        self,
        header: tuple[dn.Node | list[dn.Node], ...],
        items: list[tuple[dn.Node | list[dn.Node], ...]],
    ) -> dn.table:
        header_row = self._row(header)
        rows = [self._row(item) for item in items]

        num_columns = len(header)
        tgroup = dn.tgroup(cols=num_columns)
        tgroup += [dn.colspec()] * num_columns  # FIXME: colwidth
        tgroup += [
            dn.thead('', header_row),
            dn.tbody('', *rows),
        ]
        return dn.table('', tgroup)

    def _list_table(self, items: list[tuple[dn.Node | list[dn.Node], ...]]) -> dn.table:
        rows = [self._row(item) for item in items]

        num_columns = len(items[0])
        tgroup = dn.tgroup(cols=num_columns)
        tgroup += [dn.colspec()] * num_columns
        tgroup += dn.tbody('', *rows),
        return dn.table('', tgroup)

    def _dict_table(self, data: dict[str, Any]) -> dn.table:
        return self._table(
            header=(dn.paragraph(text='Name'), dn.paragraph(text='Value')),
            items=[
                (dn.literal_block(text=key), self._display_data(value))
                for key, value in data.items()
            ],
        )

    def _display_data(self, data: object) -> list[dn.Node]:
        if isinstance(data, types.SimpleNamespace):
            print(f'namespace {data=} {vars(data)=}')
            data = vars(data)
        if isinstance(data, dict):
            table = self._dict_table(data)
            if len(data) <= 8:
                return table
            return sphinx_toolbox.collapse.CollapseNode('', 'Data', table, classes=['datadetails'])
        if isinstance(data, str):
            if not data:
                return dn.paragraph('', '', dn.emphasis(text='(empty)'))
            text = data
        else:
            text = pprint.pformat(data, compact=True, width=85)
        return dn.literal_block(text=text, classes=['code', 'python'])

    def _xref(self, key: str) -> sphinx.addnodes.pending_xref:
        reftype = 'func' if '(' in key else 'data'
        xref = sphinx.addnodes.pending_xref(
            '',
            dn.literal(text=key, classes=['xref', 'py', f'py-{reftype}']),
            refdomain='py',
            reftarget=key.split('(')[0],
            reftype=reftype,
        )
        return dn.paragraph('', '', xref)

    def _section(self, image: containers.Image) -> list[dn.Node]:
        data = python_environments.get(image.id)

        info_table = self._list_table([
            [dn.Text('Manifest'), dn.literal_block(text=data.manifest)],
        ])

        data_table = self._table(
            header=(dn.paragraph(text='Name'), dn.paragraph(text='Value')),
            items=[
                (self._xref(key), self._display_data(data[key]))
                for key in sorted(data)  # build the list in sorted order
            ],
        )
        # Workarround for sphinx-material striping the table classes.
        data_table_div = dn.compound('', data_table, classes=['datatable'])

        section = dn.section(ids=[f'{image.name}-{image.version}'], classes=['image-section'])
        section += [
            dn.title('', '', dn.literal(text=image.id)),
            info_table,
            data_table_div,
        ]
        return [section]

    def run(self) -> list[dn.Node]:
        nodes = list(itertools.chain.from_iterable((
            self._section(image)
            for image in non_rolling_images
        )))
        return nodes


class InfoVersion(docutils.parsers.rst.Directive):
    has_content = True

    def run(self) -> list[dn.Node]:
        data = dn.Text(containers.__version__)
        for style in ' '.join(self.content).split():
            if style == 'emphasis':
                node_type = dn.emphasis
            elif style == 'strong':
                node_type = dn.strong
            else:
                raise ValueError(f'Unknown style: {style}')
            data = node_type('', '', data)
        return [data]


def setup(app: sphinx.application.Sphinx) -> sphinx.util.typing.ExtensionMetadata:
    app.add_directive('imagelist', ImageList)
    app.add_directive('imagedata', ImageData)
    app.add_directive('imageinfo-version', InfoVersion)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
