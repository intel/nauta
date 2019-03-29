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

import os
from unittest.mock import patch

import pytest

from util import system
from util.config import NCTL_CONFIG_DIR_NAME, NCTL_CONFIG_ENV_NAME, Config, ConfigInitError

APP_DIR_PATH = '/my/App'
APP_BINARY_PATH = os.path.join(APP_DIR_PATH, 'binary')
USER_HOME_PATH = '/User/Fake/home'
USER_CUSTOM_PATH = '/custom/path'
FAKE_PATH = '/fake/path'


def test_validate_config_path_for_existing_config_file(mocker):
    os_path_mock = mocker.patch('os.path.isdir')
    os_path_mock.return_value = False

    result = Config.validate_config_path(FAKE_PATH)

    assert not result


def test_validate_config_path_for_existing_config_dir_with_invalid_data(mocker):
    os_path_mock = mocker.patch('os.path.isdir')
    os_path_mock.return_value = True
    os_listdir_mock = mocker.patch('os.listdir')
    os_listdir_mock.return_value = ['not_nctl_dir', 'not_nctl_file']

    result = Config.validate_config_path(FAKE_PATH)

    assert not result


def test_validate_config_path_for_existing_config_dir_with_valid_data(mocker):
    os_path_mock = mocker.patch('os.path.isdir')
    os_path_mock.return_value = True
    os_listdir_mock = mocker.patch('os.listdir')
    os_listdir_mock.return_value = ['draft.exe', 'helm.exe'] if system.get_current_os() == system.OS.WINDOWS \
        else ['draft', 'helm']

    result = Config.validate_config_path(FAKE_PATH)

    assert result


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
def test_validate_config_path_success_with_app_dir(os_env_get, exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [False, True]
    os_env_get.return_value = ""

    result = Config.get_config_path()

    assert result == os.path.join(APP_DIR_PATH, NCTL_CONFIG_DIR_NAME)
    assert exists_mock.call_count == 2


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
def test_validate_config_path_success_with_user_local_dir(os_env_get, exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.return_value = True
    os_env_get.return_value = ""

    result = Config.get_config_path()

    assert result == os.path.join(USER_HOME_PATH, NCTL_CONFIG_DIR_NAME)
    assert exists_mock.call_count == 1


@patch('os.environ', {NCTL_CONFIG_ENV_NAME: USER_CUSTOM_PATH})
@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_success_with_env(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.return_value = True

    result = Config.get_config_path()

    assert result == USER_CUSTOM_PATH
    assert exists_mock.call_count == 1


@patch('os.environ', {NCTL_CONFIG_ENV_NAME: USER_CUSTOM_PATH})
@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_error_with_env_not_exist_dir(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.return_value = False

    with pytest.raises(ConfigInitError):
        Config.get_config_path()

    assert exists_mock.call_count == 1


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
def test_validate_config_path_error(os_env_get, exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [False, False]
    os_env_get.return_value = ""

    with pytest.raises(ConfigInitError):
        Config.get_config_path()

    assert exists_mock.call_count == 2
