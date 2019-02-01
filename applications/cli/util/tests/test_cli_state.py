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
