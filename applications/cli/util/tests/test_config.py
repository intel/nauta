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

import os
from unittest.mock import patch, mock_open, ANY

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


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
@patch('os.path.join')
@patch('os.path.isfile', return_value=False)
def test_get_local_registry_port_no_file(*args):
    assert Config().local_registry_port is None


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
@patch('os.path.join')
@patch('os.path.isfile', return_value=True)
@patch('builtins.open')
@patch('yaml.load', return_value=None)
def test_get_local_registry_port_empty_yaml(*args):
    assert Config().local_registry_port is None


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
@patch('os.path.join')
@patch('os.path.isfile', return_value=True)
@patch('util.config.open', mock_open(), create=True)
@patch('yaml.load', return_value={'local_registry_port': 1234})
def test_get_local_registry_port(*args):
    assert Config().local_registry_port == 1234


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
@patch('os.environ.get')
@patch('os.path.join')
@patch('os.path.isfile', return_value=True)
@patch('util.config.open', mock_open(), create=True)
@patch('yaml.load', return_value={'local_registry_port': 4321})
@patch('yaml.dump')
def test_set_local_registry_port(dump_mock, *args):
    Config().local_registry_port = 1234
    dump_mock.assert_called_with({'local_registry_port': 1234}, ANY, default_flow_style=False)
