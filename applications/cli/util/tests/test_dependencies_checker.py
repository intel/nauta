#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest.mock import MagicMock, call

import pytest
import yaml

from util.dependencies_checker import _is_version_valid, LooseVersion, \
    _parse_installed_version, check_dependency, \
    DependencySpec, check_all_binary_dependencies, get_local_dependency_map, \
    NAMESPACE_PLACEHOLDER, check_os, SUPPORTED_OS_MAP, \
    get_dependency_versions_file_path, save_dependency_versions, \
    load_dependency_versions, DEPENDENCY_VERSIONS_FILE_SUFFIX, get_remote_dependency_map
from util.exceptions import InvalidDependencyError, InvalidOsError, InvalidOsVersionError
from cli_text_consts import UtilDependenciesCheckerTexts as Texts


TEST_VERSION_OUTPUT = 'Client: &version.Version{SemVer:"v2.11.0",' \
                      ' GitCommit:"", GitTreeState:"clean"}'
TEST_SHORT_VERSION_OUTPUT = 'Client Version: v2.11.0\nServer Version: v2.11.0\n'
TEST_VERSION = LooseVersion('v2.11.0')


@pytest.mark.parametrize(
    'installed_version,expected_version',
    [(LooseVersion('v0.0.2'), LooseVersion('v0.0.1')),
     (LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
     (LooseVersion('12.0.2-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid(installed_version, expected_version):
    assert _is_version_valid(
        installed_version=installed_version,
        expected_version=expected_version,
        match_exact_version=False)


@pytest.mark.parametrize(
    'installed_version,expected_version',
    [(LooseVersion('v0.0.2'), LooseVersion('v0.0.3')),
     (LooseVersion('v0.0.1'), LooseVersion('v1.0.0')),
     (LooseVersion('12.0.0-ce'), LooseVersion('12.0.2-ce'))])
def test_is_version_valid_wrong_versions(installed_version, expected_version):
    assert not _is_version_valid(
        installed_version=installed_version,
        expected_version=expected_version,
        match_exact_version=False)


@pytest.mark.parametrize(
    'installed_version,expected_version',
    [(LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
     (LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
     (LooseVersion('12.0.0-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid_strict(installed_version, expected_version):
    assert _is_version_valid(
        installed_version=installed_version,
        expected_version=expected_version,
        match_exact_version=True)


@pytest.mark.parametrize(
    'installed_version,expected_version',
    [(LooseVersion('v0.0.2'), LooseVersion('v0.0.1')),
     (LooseVersion('v0.0.1'), LooseVersion('v0.0.2')),
     (LooseVersion('12.0.1-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid_strict_wrong_versions(installed_version,
                                                expected_version):
    assert not _is_version_valid(
        installed_version=installed_version,
        expected_version=expected_version,
        match_exact_version=True)


def test_parse_installed_version():
    assert _parse_installed_version(
        version_output=TEST_VERSION_OUTPUT,
        version_field='SemVer:') == TEST_VERSION


def test_parse_installed_version_without_quotes():
    assert _parse_installed_version(
        version_output=TEST_SHORT_VERSION_OUTPUT,
        version_field='Server Version:') == TEST_VERSION


def test_parse_installed_version_failure():
    with pytest.raises(ValueError):
        _parse_installed_version(
            version_output='version: 0.0.1', version_field='SemVer:')


def test_check_dependency():
    test_dependency_name = 'test-dep'
    test_version = '0.0.1'
    version_command_mock = MagicMock()
    version_command_mock.return_value = test_version, 0, test_version
    test_dependency = DependencySpec(
        expected_version=test_version,
        version_command=version_command_mock,
        version_command_args=[],
        version_field=None,
        match_exact_version=False)

    assert check_dependency(test_dependency_name,
                            test_dependency) == (True,
                                                 LooseVersion(test_version))


def test_check_dependency_namespace():
    test_dependency_name = 'test-dep'
    test_namespace = 'test-namespace'
    test_version = '0.0.1'
    version_command_mock = MagicMock()
    version_command_mock.return_value = test_version, 0, test_version
    test_dependency = DependencySpec(
        expected_version=test_version,
        version_command=version_command_mock,
        version_command_args=[NAMESPACE_PLACEHOLDER],
        version_field=None,
        match_exact_version=False)

    valid_dep, installed_version = check_dependency(
        test_dependency_name, test_dependency, namespace=test_namespace)
    assert (valid_dep, installed_version) == (True, LooseVersion(test_version))
    version_command_mock.assert_called_with([test_namespace])


def test_check_dependency_parse():
    test_dependency_name = 'test-dep'
    test_version = LooseVersion('0.0.1')
    test_version_output = 'version:"0.0.1"'
    version_command_mock = MagicMock()
    version_command_mock.return_value = test_version_output, 0, test_version_output
    test_dependency = DependencySpec(
        expected_version=test_version,
        version_command=version_command_mock,
        version_command_args=[],
        version_field='version:',
        match_exact_version=False)

    assert check_dependency(test_dependency_name,
                            test_dependency) == (True, test_version)


def test_check_all_binary_dependencies(mocker):
    check_dependency_mock = mocker.patch(
        'util.dependencies_checker.check_dependency')
    check_dependency_mock.return_value = True, LooseVersion('0.0.0')
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    load_dependency_versions_mock = mocker.patch(
        'util.dependencies_checker.load_dependency_versions',
        return_value=None)
    save_dependency_versions_mock = mocker.patch(
        'util.dependencies_checker.save_dependency_versions',
        return_value=None)

    check_all_binary_dependencies(namespace='fake')

    assert load_dependency_versions_mock.call_count == 1, 'Saved dependency versions were not loaded.'
    assert save_dependency_versions_mock.call_count == 1, 'Dependency versions were not saved.'
    assert check_dependency_mock.call_count == len(
        get_local_dependency_map()) + len(get_remote_dependency_map()), 'Not all dependencies were checked.'


def test_check_all_binary_dependencies_saved_versions(mocker):
    fake_namespace = 'fake'
    fake_version = LooseVersion('0.0.0')
    check_dependency_mock = mocker.patch(
        'util.dependencies_checker.check_dependency')
    check_dependency_mock.return_value = True, fake_version
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    saved_versions = {
        dependency_name: fake_version
        for dependency_name in get_local_dependency_map().keys()
    }

    load_dependency_versions_mock = mocker.patch(
        'util.dependencies_checker.load_dependency_versions',
        return_value=saved_versions)
    save_dependency_versions_mock = mocker.patch(
        'util.dependencies_checker.save_dependency_versions',
        return_value=None)

    check_all_binary_dependencies(namespace=fake_namespace)

    assert load_dependency_versions_mock.call_count == 1, 'Saved dependency versions were not loaded.'
    assert save_dependency_versions_mock.call_count == 0, 'Saved dependencies versions were overwritten.'
    assert check_dependency_mock.call_count == len(
        get_local_dependency_map()) + len(get_remote_dependency_map()), 'Not all dependencies were checked.'
    expected_check_dependency_calls = [
        call(
            dependency_name=dependency_name,
            dependency_spec=dependency_spec,
            namespace=fake_namespace,
            saved_versions=saved_versions)
        for dependency_name, dependency_spec in get_local_dependency_map().items()
    ]
    check_dependency_mock.assert_has_calls(
        expected_check_dependency_calls, any_order=True)


def test_check_all_binary_dependencies_invalid_version(mocker):
    check_dependency_mock = mocker.patch(
        'util.dependencies_checker.check_dependency')
    check_dependency_mock.return_value = False, LooseVersion('0.0.0')
    mocker.patch(
        'util.dependencies_checker.load_dependency_versions',
        return_value=None)
    mocker.patch(
        'util.dependencies_checker.save_dependency_versions',
        return_value=None)
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies(namespace='fake')


def test_check_all_binary_dependencies_parsing_error(mocker):
    check_dependency_mock = mocker.patch(
        'util.dependencies_checker.check_dependency')
    check_dependency_mock.side_effect = ValueError
    mocker.patch(
        'util.dependencies_checker.load_dependency_versions',
        return_value=None)
    mocker.patch(
        'util.dependencies_checker.save_dependency_versions',
        return_value=None)
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path
    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies(namespace='fake')


def test_check_all_binary_dependencies_version_check_error(mocker):
    check_dependency_mock = mocker.patch(
        'util.dependencies_checker.check_dependency')
    check_dependency_mock.side_effect = RuntimeError
    mocker.patch(
        'util.dependencies_checker.load_dependency_versions',
        return_value=None)
    mocker.patch(
        'util.dependencies_checker.save_dependency_versions',
        return_value=None)
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies(namespace='fake')


def test_check_os_unknown(mocker):
    get_os_version_mock = mocker.patch(
        'util.dependencies_checker.get_os_version')
    get_os_version_mock.return_value = ("", LooseVersion("0"))

    with pytest.raises(InvalidOsError) as os_error:
        check_os()

    assert Texts.UNKNOWN_OS_ERROR_MSG == str(os_error.value)


def test_check_os_get_os_version_fail(mocker):
    get_os_version_mock = mocker.patch(
        'util.dependencies_checker.get_os_version')
    get_os_version_mock.side_effect = FileNotFoundError()

    with pytest.raises(InvalidOsError) as os_error:
        check_os()

    assert Texts.GET_OS_VERSION_ERROR_MSG == str(os_error.value)


def test_check_os_not_supported(mocker):
    get_os_version_mock = mocker.patch(
        'util.dependencies_checker.get_os_version')
    get_os_version_mock.return_value = ("not_supported_system",
                                        LooseVersion("9.3"))

    with pytest.raises(InvalidOsError) as os_error:
        check_os()

    assert Texts.UNSUPPORTED_OS_ERROR_MSG.format(os_name="not_supported_system", os_version="9.3") \
        == str(os_error.value)


def test_check_os_version_not_supported(mocker):
    get_os_version_mock = mocker.patch(
        'util.dependencies_checker.get_os_version')
    get_os_version_mock.return_value = ("ubuntu", LooseVersion("14.04"))

    with pytest.raises(InvalidOsVersionError) as os_error:
        check_os()

    assert Texts.INVALID_OS_VERSION_ERROR_MSG.format(
        os_name="ubuntu", os_version="14.04") == str(os_error.value)


def test_check_os_version_supported(mocker):
    get_os_version_mock = mocker.patch(
        'util.dependencies_checker.get_os_version')
    get_os_version_mock.return_value = (list(SUPPORTED_OS_MAP.keys())[0],
                                        SUPPORTED_OS_MAP[list(
                                            SUPPORTED_OS_MAP.keys())[0]])

    try:
        check_os()
    except InvalidOsError:
        pytest.fail("check_os failed with supported OS.")


def test_get_dependency_version_file_path(mocker):
    fake_nctl_version = '1.0.0-alpha'
    fake_config_path = '/usr/ogorek/nctl_config'
    mocker.patch('util.dependencies_checker.VERSION', fake_nctl_version)
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    path = get_dependency_versions_file_path()
    assert path in {
        f'{fake_config_path}/{fake_nctl_version}{DEPENDENCY_VERSIONS_FILE_SUFFIX}',
        f'{fake_config_path}\\{fake_nctl_version}{DEPENDENCY_VERSIONS_FILE_SUFFIX}'
    }  # Windows


def test_save_dependency_versions(mocker, tmpdir):
    fake_config_dir = tmpdir.mkdir("/nctl_config")
    fake_dependency_versions_file_path = f'{fake_config_dir}1.0.0.saved-versions.yaml'
    mocker.patch(
        'util.dependencies_checker.get_dependency_versions_file_path',
        return_value=fake_dependency_versions_file_path)
    fake_dependency_versions = {
        'bla': '1.0.0',
        'ble': '0.0.1-alpha'
    }
    save_dependency_versions(fake_dependency_versions)

    with open(
            fake_dependency_versions_file_path, mode='r',
            encoding='utf-8') as dep_versions_file:
        assert yaml.safe_load(dep_versions_file) == fake_dependency_versions


def test_load_dependency_versions(mocker, tmpdir):
    fake_dependency_versions = {
        'bla': '1.0.0',
        'ble': '0.0.1-alpha'
    }
    fake_dependency_versions_file = tmpdir.mkdir("/nctl_config").join(
        "1.0.0.saved-versions.yaml")
    fake_dependency_versions_file.write(yaml.safe_dump(fake_dependency_versions))

    mocker.patch(
        'util.dependencies_checker.get_dependency_versions_file_path',
        return_value=fake_dependency_versions_file)

    assert fake_dependency_versions == load_dependency_versions()
