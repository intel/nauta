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
from unittest.mock import patch

import pytest

from commands.verify import verify
from util.config import DLS_CTL_CONFIG_DIR_NAME, DLS_CTL_CONFIG_ENV_NAME

APP_DIR_PATH = '/my/App'
APP_BINARY_PATH = os.path.join(APP_DIR_PATH, 'binary')
USER_HOME_PATH = '/User/Fake/home'
USER_CUSTOM_PATH = '/custom/path'


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_success_with_app_dir(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [False, True]

    result = verify.validate_config_path()

    assert result == os.path.join(APP_DIR_PATH, DLS_CTL_CONFIG_DIR_NAME)
    assert exists_mock.call_count == 2


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_success_with_user_local_dir(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [True]

    result = verify.validate_config_path()

    assert result == os.path.join(USER_HOME_PATH, DLS_CTL_CONFIG_DIR_NAME)
    assert exists_mock.call_count == 1


@patch('os.environ', {DLS_CTL_CONFIG_ENV_NAME: USER_CUSTOM_PATH})
@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_success_with_env(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [True]

    result = verify.validate_config_path()

    assert result == USER_CUSTOM_PATH
    assert exists_mock.call_count == 1


@patch('os.environ', {DLS_CTL_CONFIG_ENV_NAME: USER_CUSTOM_PATH})
@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_error_with_env_not_exist_dir(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [False]

    with pytest.raises(SystemExit):
        verify.validate_config_path()

    assert exists_mock.call_count == 1


@patch('sys.executable', APP_BINARY_PATH)
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_validate_config_path_error(exists_mock, expanduser_mock):
    expanduser_mock.return_value = USER_HOME_PATH
    exists_mock.side_effect = [False, False]

    with pytest.raises(SystemExit):
        verify.validate_config_path()

    assert exists_mock.call_count == 2
