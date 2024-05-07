import argparse
import json
import os
import pathlib
import sys

import docker


sys.path.insert(0, os.fspath(pathlib.Path(__file__).parent.parent))


import containers
import containers.concurrent



SOURCE_MOUNT = docker.types.Mount(
    target='/source',
    source=os.fspath(containers.ROOT),
    type='bind',
    read_only=True,
)


def generate_image_data(tag: str, out: pathlib.Path) -> None:
    out.parent.mkdir(exist_ok=True, parents=True)
    docker_client = docker.from_env()
    raw_introspection_data = docker_client.containers.run(
        image=tag,
        command=['/usr/bin/python3', '-m', 'python_environments.generate'],
        environment={'PYTHONPATH': '/source/python'},
        mounts=[SOURCE_MOUNT],
    )
    data = {
        'metadata': {
            'manifest': docker_client.images.get(tag).id,
        },
        'data': json.loads(raw_introspection_data.decode()),
    }
    with out.open('w') as f:
        json.dump(data, fp=f, sort_keys=True, indent=4)


def main() -> None:
    config = containers.Config.from_config_file(containers.ENVIRONMENTS_TOML_PATH)

    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=pathlib.Path, default=containers.PYTHON_PATH / '.data')
    parser.add_argument('--list-files', action='store_true')
    args = parser.parse_args()

    # TODO: Figure out how rolling images should be supported.
    target_images = config.images.filter(ignore=containers.RollingImage)

    if args.list_files:
        print(' '.join([f'{image.id}.json' for image in target_images]))
        return

    tasks = [
        containers.concurrent.Task(
            userdata=image,
            fn=generate_image_data,
            args=(image.id, args.outdir / f'{image.id}.json'),
        )
        for image in target_images
    ]

    print('Generating image data...')
    for successful, task in containers.concurrent.run_tasks(tasks):
        image = task.userdata
        if successful:
            print(f'- generated data for {image.id}')
        else:
            print(f'- failed to generate data for {image.id}')


if __name__ == '__main__':
    main()
