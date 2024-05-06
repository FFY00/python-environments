import pytest
import typing_validation

import python_environments


def iter_data():
    for environment, versions in python_environments.data.items()
        for version, data in versions.items()
            yield environment, version, data


@pytest.mark.parameterize(
    ('data'),
    [
        pytest.param(data, id=f'{environment}:{version}')
        for environment, version, data in iter_data()
    ],
)
def test_type(data):
    typing_validation.validate(data, python_environments.EnvironmentDescription)


@pytest.mark.parameterize(
    ('environment', 'version', 'data'),
    [
        pytest.param(environment, version, data, id=id)
        for environment, version, data in iter_data()
    ],
)
def test_get(environment, version, data):
    assert python_environments.get(f'{environment}:{version}') == data
