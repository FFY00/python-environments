import os
import pathlib
import shutil
import subprocess

from collections.abc import Callable, Collection, Mapping


SubprocessRunnerType = Callable[[str, ...], bytes]


def logging_subprocess_runner(logfile: pathlib.Path) -> SubprocessRunnerType:
    logfile.parent.mkdir(exist_ok=True, parents=True)

    def _log(cmd: list[str], output: bytes) -> None:
        if not logfile:
            return
        with logfile.open('ab') as f:
            cmd_str = ' '.join(cmd)
            f.write(f'$ {cmd_str}\n'.encode())
            f.write(output)
            if not output.endswith(b'\n'):
                f.write(b'\n')

    def run(cmd: str) -> bytes:
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
            raise
        finally:
            _log(cmd, output)
        return output

    return run


class DockerClient:
    def __init__(self, runner: SubprocessRunnerType = subprocess.check_output) -> None:
        self._runner = runner
        self._client = (
            os.environ.get('DOCKER', 'docker')
            or shutil.which('docker')
            or shutil.which('podman')
        )

    def _run(self, *args: str) -> str:
        return self._runner([self._client, *args])

    def build(self, path: pathlib.Path, tags: Collection[str], labels: Mapping[str, str]) -> None:
        self._run(
            'buildx',
            'build',
            os.fspath(path),
            *[f'--tag={tag}' for tag in tags],
            *[f'--label={name}={value}' for name, value in labels.items()],
        )

    def push(self, name: str) -> None:
        self._run('push', name)
