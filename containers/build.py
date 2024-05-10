import argparse
import itertools
import pathlib

from collections.abc import Iterator

import containers
import containers.concurrent
import containers.env
import containers.ops


class Builder:
    def __init__(
        self,
        images: containers.ImagesContainer,
        repos: list[containers.Repo],
        srcdir: pathlib.Path,
        logdir: pathlib.Path,
    ) -> None:
        self._images = images
        self._repos = repos
        self._srcdir = srcdir
        self._logdir = logdir
        self._env_info = containers.env.environment_info()

    def _docker_client(self, image: containers.Image) -> containers.ops.DockerClient:
        logfile = self._logdir / f'{image.name}-{image.version}.log'
        runner = containers.ops.logging_subprocess_runner(logfile)
        return containers.ops.DockerClient(runner)

    def _repo_tags(self, image: containers.Image) -> list[str]:
        return list(itertools.chain.from_iterable([
            repo.tags(image.tags) for repo in self._repos
        ]))

    def generate_sources(self) -> None:
        for image in self._images:
            image.template.render(self._srcdir / image.id)

    def build(self) -> Iterator[bool, containers.concurrent.Task[containers.Image]]:
        yield from containers.concurrent.run_tasks([
            containers.concurrent.Task(
                userdata=image,
                fn=self._docker_client(image).build,
                args=(
                    self._srcdir / image.id,
                    image.tags + self._repo_tags(image),
                    self._env_info,
                ),
            )
            for image in self._images
        ])

    def push(self) -> Iterator[bool, containers.concurrent.Task[tuple[containers.Image, containers.Repo]]]:
        yield from containers.concurrent.run_tasks([
            containers.concurrent.Task(
                userdata=tag,
                fn=self._docker_client(image).push,
                args=(tag,),
            )
            for repo in self._repos
            for image in self._images
            for tag in repo.tags(image.tags)
        ])


def main() -> None:
    config = containers.Config.from_config_file(containers.ENVIRONMENTS_TOML_PATH)

    parser = argparse.ArgumentParser()
    images_group = parser.add_mutually_exclusive_group()
    images_group.add_argument(
        '--images',
        nargs='*',
        choices=config.images.ids,
        default=config.images.ids,
    )
    images_group.add_argument('--rolling', action='store_true')
    parser.add_argument('--push', action='store_true')
    images_group.add_argument(
        '--build-path',
        type=pathlib.Path,
        default=containers.BUILD_PATH,
    )
    args = parser.parse_args()

    if args.rolling:
        target_images = config.images.filter(match=containers.RollingImage)
    else:
        target_images = config.images[args.images]

    srcdir = args.build_path / 'src'
    logdir = args.build_path / 'logs'
    builder = Builder(target_images, config.repos, srcdir, logdir)

    print('Generating sources...')
    builder.generate_sources()

    print('Building images...')
    for successful, task in builder.build():
        image = task.userdata
        if successful:
            print(f'- built {image.id}')
        else:
            print(f'- failed to build {image.id}')

    if args.push:
        print('Pushing images...')
        for successful, task in builder.push():
            tag = task.userdata
            if successful:
                print(f'- pushed {tag}')
            else:
                print(f'- failed to push {tag}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
