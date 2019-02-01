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

from unittest.mock import ANY

import pytest

from util.cli_state import verify_cli_dependencies, verify_cli_config_path, verify_user_privileges
from cli_text_consts import CliStateTexts
from util.config import ConfigInitError
from util.exceptions import InvalidDependencyError


class CliStateMocks:
    def __init__(self, mocker):
        self.is_current_user_administrator = mocker.patch('util.cli_state.is_current_user_administrator',
                                                          return_value=True)
        self.get_kubectl_namespace = mocker.patch('util.cli_state.get_kubectl_current_context_namespace',
                                                  return_value='test-namespace')
        self.check_os = mocker.patch('util.cli_state.check_os')
        self.check_all_binary_dependencies = mocker.patch('util.cli_state.check_all_binary_dependencies')
        self.config = mocker.patch('util.cli_state.Config')
        self.handle_error = mocker.patch('util.cli_state.handle_error')


@pytest.fixture()
def cli_state_mocks(mocker) -> CliStateMocks:
    return CliStateMocks(mocker)


def test_verify_cli_dependencies(cli_state_mocks: CliStateMocks):
    verify_cli_dependencies()

    assert cli_state_mocks.check_os.call_count == 1
    assert cli_state_mocks.check_all_binary_dependencies.call_count == 1


def test_verify_cli_dependencies_namespace_error(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.return_value = False
    cli_state_mocks.get_kubectl_namespace.side_effect = RuntimeError
    with pytest.raises(SystemExit):
        verify_cli_dependencies()


def test_verify_cli_dependencies_dependency_error(cli_state_mocks: CliStateMocks):
    cli_state_mocks.check_all_binary_dependencies.side_effect = InvalidDependencyError
    verify_cli_dependencies()

    cli_state_mocks.handle_error.assert_called_with(ANY, CliStateTexts.INVALID_DEPENDENCY_ERROR_MSG,
                                                    CliStateTexts.INVALID_DEPENDENCY_ERROR_MSG,
                                                    add_verbosity_msg=ANY)


def test_verify_cli_config_path(cli_state_mocks: CliStateMocks):
    verify_cli_config_path()
    cli_state_mocks.config.assert_called_once()


def test_verify_cli_config_path_error(cli_state_mocks: CliStateMocks):
    cli_state_mocks.config.side_effect = ConfigInitError(message='')
    with pytest.raises(SystemExit):
        verify_cli_config_path()


def test_verify_user_privileges_admin_command_admin_user(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.return_value = True
    verify_user_privileges(admin_command=True, command_name='fake command')

    cli_state_mocks.is_current_user_administrator.assert_called_once()


def test_verify_user_privileges_admin_command_regular_user(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.return_value = False
    with pytest.raises(SystemExit):
        verify_user_privileges(admin_command=True, command_name='fake command')

    cli_state_mocks.is_current_user_administrator.assert_called_once()


def test_verify_user_privileges_regular_command_regular_user(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.return_value = False
    verify_user_privileges(admin_command=False, command_name='fake command')

    cli_state_mocks.is_current_user_administrator.assert_called_once()


def test_verify_user_privileges_regular_command_admin_user(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.return_value = True
    with pytest.raises(SystemExit):
        verify_user_privileges(admin_command=False, command_name='fake command')

    cli_state_mocks.is_current_user_administrator.assert_called_once()


def test_verify_user_privileges_error(cli_state_mocks: CliStateMocks):
    cli_state_mocks.is_current_user_administrator.side_effect = RuntimeError
    with pytest.raises(SystemExit):
        verify_user_privileges(admin_command=False, command_name='fake command')
