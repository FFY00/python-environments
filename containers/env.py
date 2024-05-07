import os
import subprocess


def dict_filter_none(data: dict[str, str | None]) -> dict[str, str]:
    return {
        key: value
        for key, value in data.items()
        if value
    }


def get_commit() -> str | None:
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except subprocess.CalledProcessError:
        return None


def environment_info() -> dict[str, str]:
    return dict_filter_none({
        'commit': get_commit() or os.environ.get('GITHUB_SHA'),
        'github-actions': os.environ.get('GITHUB_ACTIONS'),
        'github-actions-repo': os.environ.get('GITHUB_REPOSITORY'),
        'github-actions-job': os.environ.get('GITHUB_JOB'),
        'github-actions-run': os.environ.get('GITHUB_RUN_ID'),
    })
