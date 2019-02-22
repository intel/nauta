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

import pytest

from licensing import license_acceptance_manager


def test_save_license_accepted_with_valid_config(mocker):
    mocker.patch.object(license_acceptance_manager.Config, 'validate_config_path', new=lambda x: True)
    sys_exit_mock = mocker.patch("sys.exit")
    open_mock = mocker.patch('builtins.open')
    mocker.patch.object(license_acceptance_manager.Config, 'get_config_path', new=lambda: "/fake/path")

    license_acceptance_manager.save_license_accepted()

    assert open_mock.call_count == 1
    assert sys_exit_mock.call_count == 0


def test_save_license_accepted_with_invalid_config(mocker):
    mocker.patch.object(license_acceptance_manager.Config, 'validate_config_path', new=lambda x: False)
    sys_exit_mock = mocker.patch("sys.exit")
    open_mock = mocker.patch('builtins.open')
    mocker.patch.object(license_acceptance_manager.Config, 'get_config_path', new=lambda: "/fake/path")

    license_acceptance_manager.save_license_accepted()

    assert open_mock.call_count == 0
    sys_exit_mock.assert_called_once_with(1)


@pytest.mark.parametrize(['path_isfile_return_value', 'license_accepted_expected_value'],
                         [(True, True),
                          (False, False)])
def test_is_license_already_accepted(mocker, path_isfile_return_value: bool, license_accepted_expected_value: bool):
    mocker.patch.object(license_acceptance_manager.Config, 'get_config_path', new=lambda: "/fake/path")
    mocker.patch('os.path.isfile', new=lambda *args: path_isfile_return_value)

    license_accepted = license_acceptance_manager.is_license_already_accepted()

    assert license_accepted == license_accepted_expected_value


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize(['click_confirm_return_value', 'expected_license_accepted'],
                         [
                             (True, True),
                             (False, False)
                         ])
def test_check_license_acceptance(mocker, click_confirm_return_value: bool, expected_license_accepted: bool):
    mocker.patch.object(license_acceptance_manager, 'is_license_already_accepted', new=lambda: False)
    mocker.spy(license_acceptance_manager, 'is_license_already_accepted')
    mocker.patch.object(license_acceptance_manager, 'save_license_accepted')
    mocker.patch('click.confirm', new=lambda *args, **kwargs: click_confirm_return_value)

    license_accepted = license_acceptance_manager.check_license_acceptance()

    assert license_accepted == expected_license_accepted
    assert license_acceptance_manager.is_license_already_accepted.call_count == 1
    assert license_acceptance_manager.save_license_accepted.call_count == 1 if expected_license_accepted else True


# noinspection PyUnresolvedReferences
def test_check_license_acceptance_already_accepted(mocker):
    mocker.patch.object(license_acceptance_manager, 'is_license_already_accepted', new=lambda: True)
    mocker.spy(license_acceptance_manager, 'is_license_already_accepted')
    license_accepted = license_acceptance_manager.check_license_acceptance()

    assert license_accepted
    assert license_acceptance_manager.is_license_already_accepted.call_count == 1