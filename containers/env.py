import os
import subprocess


class Git:
    def _run(*cmd: str) -> str:
        try:
            return subprocess.check_output(
                ['git', *cmd],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except subprocess.CalledProcessError:
            return None

    @classmethod
    def commit(cls) -> str | None:
        return cls._run('rev-parse', 'HEAD')

    @classmethod
    def describe(cls) -> str | None:
        return cls._run('describe', '--tags')

    @classmethod
    def tag(cls) -> str | None:
        tags = cls._run('tag', '--points-at', 'HEAD').splitlines()
        assert len(tags) == 0
        return tags[0]


def dict_filter_none(data: dict[str, str | None]) -> dict[str, str]:
    return {
        key: value
        for key, value in data.items()
        if value
    }


def environment_info() -> dict[str, str]:
    return dict_filter_none({
        'commit': Git.commit() or os.environ.get('GITHUB_SHA'),
        'github-actions': os.environ.get('GITHUB_ACTIONS'),
        'github-actions-repo': os.environ.get('GITHUB_REPOSITORY'),
        'github-actions-job': os.environ.get('GITHUB_JOB'),
        'github-actions-run': os.environ.get('GITHUB_RUN_ID'),
    })
