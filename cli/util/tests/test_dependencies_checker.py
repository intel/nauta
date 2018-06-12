#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

from unittest.mock import MagicMock

import pytest

from util.dependencies_checker import _is_version_valid, LooseVersion, _parse_installed_version, check_dependency,\
    DependencySpec, check_all_binary_dependencies, DEPENDENCY_MAP, InvalidDependencyError

TEST_VERSION_OUTPUT = 'Client: &version.Version{SemVer:"v2.9.1",' \
                  ' GitCommit:"20adb27c7c5868466912eebdf6664e7390ebe710", GitTreeState:"clean"}'
TEST_VERSION = LooseVersion('v2.9.1')


@pytest.mark.parametrize('installed_version,expected_version', [(LooseVersion('v0.0.2'), LooseVersion('v0.0.1')),
                                                                (LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
                                                                (LooseVersion('12.0.2-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid(installed_version, expected_version):
    assert _is_version_valid(installed_version=installed_version, expected_version=expected_version,
                             match_exact_version=False)


@pytest.mark.parametrize('installed_version,expected_version', [(LooseVersion('v0.0.2'), LooseVersion('v0.0.3')),
                                                                (LooseVersion('v0.0.1'), LooseVersion('v1.0.0')),
                                                                (LooseVersion('12.0.0-ce'), LooseVersion('12.0.2-ce'))])
def test_is_version_valid_wrong_versions(installed_version, expected_version):
    assert not _is_version_valid(installed_version=installed_version, expected_version=expected_version,
                                 match_exact_version=False)


@pytest.mark.parametrize('installed_version,expected_version', [(LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
                                                                (LooseVersion('v0.0.1'), LooseVersion('v0.0.1')),
                                                                (LooseVersion('12.0.0-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid_strict(installed_version, expected_version):
    assert _is_version_valid(installed_version=installed_version, expected_version=expected_version,
                             match_exact_version=True)


@pytest.mark.parametrize('installed_version,expected_version', [(LooseVersion('v0.0.2'), LooseVersion('v0.0.1')),
                                                                (LooseVersion('v0.0.1'), LooseVersion('v0.0.2')),
                                                                (LooseVersion('12.0.1-ce'), LooseVersion('12.0.0-ce'))])
def test_is_version_valid_strict_wrong_versions(installed_version, expected_version):
    assert not _is_version_valid(installed_version=installed_version, expected_version=expected_version,
                                 match_exact_version=True)


def test_parse_installed_version():
    assert _parse_installed_version(version_output=TEST_VERSION_OUTPUT, version_field='SemVer') == TEST_VERSION


def test_parse_installed_version_failure():
    with pytest.raises(ValueError):
        _parse_installed_version(version_output='version: 0.0.1', version_field='SemVer')


def test_check_dependency():
    test_version = '0.0.1'
    version_command_mock = MagicMock()
    version_command_mock.return_value = test_version, 0
    test_dependency = DependencySpec(expected_version=test_version, version_command=version_command_mock,
                                     version_command_args=[], version_field=None, match_exact_version=False)

    assert check_dependency(test_dependency) == (True, LooseVersion(test_version))


def test_check_dependency_parse():
    test_version = LooseVersion('0.0.1')
    test_version_output = 'version:"0.0.1"'
    version_command_mock = MagicMock()
    version_command_mock.return_value = test_version_output, 0
    test_dependency = DependencySpec(expected_version=test_version, version_command=version_command_mock,
                                     version_command_args=[], version_field='version', match_exact_version=False)

    assert check_dependency(test_dependency) == (True, test_version)


def test_check_all_binary_dependencies(mocker):
    check_dependency_mock = mocker.patch('util.dependencies_checker.check_dependency')
    check_dependency_mock.return_value = True, LooseVersion('0.0.0')

    check_all_binary_dependencies()

    assert check_dependency_mock.call_count == len(DEPENDENCY_MAP), 'Not all dependencies were checked.'


def test_check_all_binary_dependencies_invalid_version(mocker):
    check_dependency_mock = mocker.patch('util.dependencies_checker.check_dependency')
    check_dependency_mock.return_value = False, LooseVersion('0.0.0')

    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies()


def test_check_all_binary_dependencies_parsing_error(mocker):
    check_dependency_mock = mocker.patch('util.dependencies_checker.check_dependency')
    check_dependency_mock.side_effect = ValueError

    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies()


def test_check_all_binary_dependencies_version_check_error(mocker):
    check_dependency_mock = mocker.patch('util.dependencies_checker.check_dependency')
    check_dependency_mock.side_effect = RuntimeError

    with pytest.raises(InvalidDependencyError):
        check_all_binary_dependencies()
