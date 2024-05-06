import docutils.nodes as dn
import docutils.parsers.rst
import sphinx.addnodes
import sphinx.application
import sphinx.util.typing

import containers


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


def setup(app: sphinx.application.Sphinx) -> sphinx.util.typing.ExtensionMetadata:
    app.add_directive('imagelist', ImageList)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
