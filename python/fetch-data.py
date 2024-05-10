import argparse
import itertools
import os
import pathlib
import shutil
import sys
import zipfile
import time

import github
import requests


sys.path.insert(0, os.fspath(pathlib.Path(__file__).parent.parent))


import containers.env


class GithubClient:
    def __init__(self, repo: str, token: str) -> None:
        self._token = token
        self._client = github.Github(auth=github.Auth.Token(token))
        self._repo = self._client.get_repo('FFY00/python-environments')

    def find_artifact(
        self,
        run_name: str,
        artifact_name: str,
        commit: str,
        timeout: int | None = None,
    ) -> github.Artifact.Artifact | None:
        for run in self._repo.get_workflow_runs(head_sha=commit):
            if run.name == run_name:
                break

        if timeout is None:
            tries = range(1)
        elif timeout == 0:
            tries = itertools.count()  # infinite
        else:
            tries = range(timeout)

        for i in tries:
            if i != 0:
                time.sleep(1)
            for artifact in run.get_artifacts():
                if artifact.name == artifact_name:
                    return artifact
        return None

    def download_artifact(self, artifact: github.Artifact.Artifact, path: pathlib.Path) -> None:
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self._token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        with requests.get(artifact.archive_download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with path.open('wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=pathlib.Path, default=containers.PYTHON_PATH / '.data')
    parser.add_argument('--commit', default=None)
    parser.add_argument('--timeout', type=int, default=None)
    args = parser.parse_args()

    commit = args.commit or containers.env.get_commit()
    if not commit:
        print('Must specify a commit.')
        sys.exit(1)

    github_client = GithubClient(
        repo='FFY00/python-environments',
        token=os.environ.get('GITHUB_TOKEN'),
    )

    workdir = args.outdir / '.fetch-data'
    shutil.rmtree(workdir, ignore_errors=True)
    workdir_data = workdir / 'data'
    workdir_data.mkdir(exist_ok=True, parents=True)

    if args.timeout:
        print(f'Waiting for for artifact (timout={args.timeout}s)...')
    else:
        print('Looking for artifact...')
    artifact = github_client.find_artifact('build', 'image-data', commit, args.timeout)

    if not artifact:
        print(f'Could not find artifact for commit {commit}.')
        sys.exit(1)
    print(f'Found artifact: {artifact}')

    github_client.download_artifact(artifact, workdir / 'image-data.zip')

    with zipfile.ZipFile(workdir / 'image-data.zip') as z:
        z.extractall(workdir_data)
    with zipfile.ZipFile(workdir_data / 'image-data.zip') as z:
        z.extractall(workdir)

    shutil.rmtree(workdir)


if __name__ == '__main__':
    main()
