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

import base64

import pytest
from click.testing import CliRunner
from unittest.mock import patch, mock_open

from platform_resources.user import User, UserStatus
from commands.user.create import generate_kubeconfig, create, UserState
from platform_resources.user_utils import check_users_presence
from util.helm import delete_user, delete_helm_release
from cli_text_consts import VERBOSE_RERUN_MSG, UserCreateCmdTexts as Texts
from util.k8s.k8s_info import NamespaceStatus

test_username = "test_username"
test_namespace = "test_namespace"
test_address = "test_address"
test_token = "test_token"
test_cacert = "test_cacert"
test_cacert_encoded = base64.b64encode(
    test_cacert.encode('utf-8')).decode('utf-8')
test_samba_password = "test_samba_password"

KUBECONFIG = f'''
current-context: user-context
apiVersion: v1
clusters:
- cluster:
    api-version: v1
    server: https://{test_address}
    certificate-authority-data: {test_cacert_encoded}
  name: nauta-cluster
contexts:
- context:
    cluster: nauta-cluster
    namespace: "{test_namespace}"
    user: "{test_username}"
  name: user-context
kind: Config
preferences:
  colors: true
users:
- name: "{test_username}"
  user:
    token: {test_token}
'''

user_data = User(
    name=test_username,
    uid="10001",
    state=UserStatus.CREATED,
    creation_timestamp="2019-01-01",
    experiment_runs=None)


def test_check_users_presence_success(mocker):
    mocker.patch("platform_resources.user_utils.find_namespace", return_value=NamespaceStatus.NOT_EXISTS)
    mocker.patch("platform_resources.user.User.get", return_value=user_data)

    assert check_users_presence(test_username) == UserState.ACTIVE

    mocker.patch("platform_resources.user_utils.find_namespace", return_value=NamespaceStatus.ACTIVE)
    assert check_users_presence(test_username) == UserState.ACTIVE


def test_check_users_presence_failure(mocker):
    mocker.patch("platform_resources.user_utils.find_namespace", return_value=NamespaceStatus.NOT_EXISTS)
    mocker.patch("platform_resources.user.User.get", return_value=user_data)

    assert check_users_presence(test_username + "_wrong") == UserState.NOT_EXISTS


def test_generate_kubeconfig():
    output = generate_kubeconfig(
        username=test_username,
        namespace=test_namespace,
        address=test_address,
        token=test_token,
        cacrt=test_cacert)

    assert output == KUBECONFIG


def test_delete_helm_release_success(mocker):
    esc_mock = mocker.patch("util.helm.execute_system_command")

    esc_mock.side_effect = [(f"release \"{test_username}\" deleted", 0,
                             f"release \"{test_username}\" deleted"),
                            (f"release: \"{test_username}\" not found", 0,
                             f"release: \"{test_username}\" not found")]

    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.helm.Config')
    fake_config.return_value.config_path = fake_config_path

    delete_helm_release(test_username)

    assert esc_mock.call_count == 1


def test_delete_helm_release_failure(mocker):
    mocker.patch("util.helm.execute_system_command", return_value=("", 1, ""))
    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.helm.Config')
    fake_config.return_value.config_path = fake_config_path
    with pytest.raises(RuntimeError):
        delete_helm_release(test_username)


def test_delete_user_success(mocker):
    dns_mock = mocker.patch("util.helm.delete_namespace")
    dhr_mock = mocker.patch("util.helm.delete_helm_release")

    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.helm.Config')
    fake_config.return_value.config_path = fake_config_path

    delete_user(test_username)

    assert dns_mock.call_count == 1
    assert dhr_mock.call_count == 1


def test_delete_user_failure(mocker):
    dns_mock = mocker.patch(
        "util.helm.delete_namespace", side_effect=RuntimeError)
    dhr_mock = mocker.patch("util.helm.delete_helm_release")

    with pytest.raises(RuntimeError):
        delete_user(test_username)

    assert dns_mock.call_count == 1
    assert dhr_mock.call_count == 0


class UserCreationMocks:
    def __init__(self, mocker):
        self.check_users_presence = mocker.patch(
            "commands.user.create.check_users_presence",
            return_value=UserState.ACTIVE)
        self.execute_system_command = mocker.patch(
            "commands.user.create.execute_system_command", return_value=("", 0))
        self.get_users_token = mocker.patch(
            "commands.user.create.get_users_token",
            return_value=test_samba_password)
        self.validate_user_name = mocker.patch("commands.user.create.validate_user_name")


@pytest.fixture()
def user_creation_mocks(mocker) -> UserCreationMocks:
    return UserCreationMocks(mocker)


def test_create_user_failure(user_creation_mocks: UserCreationMocks):  # noqa: F811
    runner = CliRunner()
    runner.invoke(create, [test_username])

    assert user_creation_mocks.check_users_presence.call_count == 1, "users presence wasn't checked"
    assert user_creation_mocks.execute_system_command.call_count == 0, "user was created"
    assert user_creation_mocks.get_users_token.call_count == 0, "users password was taken"
    assert user_creation_mocks.validate_user_name.call_count == 1, "username wasn't validated"


def test_create_user_terminating(user_creation_mocks: UserCreationMocks):  # noqa: F811
    user_creation_mocks.check_users_presence.return_value = UserState.TERMINATING
    runner = CliRunner()
    result = runner.invoke(create, [test_username])

    assert Texts.USER_BEING_REMOVED_ERROR_MSG.format(
        username=test_username) in result.output

    assert user_creation_mocks.check_users_presence.call_count == 1, "users presence wasn't checked"
    assert user_creation_mocks.execute_system_command.call_count == 0, "user was created"
    assert user_creation_mocks.get_users_token.call_count == 0, "users password was taken"
    assert user_creation_mocks.validate_user_name.call_count == 1, "username wasn't validated"


def test_create_user_incorrect_name(user_creation_mocks: UserCreationMocks):  # noqa: F811
    error_msg = 'error'
    user_creation_mocks.validate_user_name.side_effect = ValueError(error_msg)

    runner = CliRunner()
    result = runner.invoke(create, [test_username])

    assert error_msg in result.output
    assert user_creation_mocks.validate_user_name.call_count == 1, "username wasn't validated"


class CreateUserMock():
    def __init__(self, mocker):
        self.check_users_presence = mocker.patch("commands.user.create.check_users_presence", return_value=False)
        self.execute_system_command = mocker.patch("commands.user.create.execute_system_command",
                                                   return_value=("", 0, ""))
        self.get_users_token = mocker.patch("commands.user.create.get_users_token", return_value=test_samba_password)
        self.get_certificate = mocker.patch("commands.user.create.get_certificate", return_value="")
        self.get_user = mocker.patch("platform_resources.user.User.get", return_value=user_data)
        self.k8s_proxy = mocker.patch("commands.user.create.K8sProxy")
        self.k8s_proxy.return_value.__enter__.return_value.tunnel_port = 12345
        self.add_to_git_repo_manager = mocker.patch("commands.user.create.GitRepoManagerClient.add_nauta_user",
                                                    return_value=user_data)
        self.validate_user_name = mocker.patch("commands.user.create.validate_user_name")
        self.path_join = mocker.patch("os.path.join", return_value="folder")

        self.is_user_created = mocker.patch('commands.user.create.is_user_created', return_value=True)

        config_class_mock = mocker.patch('commands.user.create.Config')
        self.config_instance = config_class_mock.return_value
        self.config_instance.config_path = "test"

        config_map_class_mock = mocker.patch("commands.user.create.NAUTAConfigMap")
        self.config_map = config_map_class_mock.return_value
        self.config_map.tiller_location = "image_tiller"

        self.get_kubectl_host = mocker.patch("commands.user.create.get_kubectl_host")
        self.get_kubectl_host.return_value = "localhost"


@pytest.fixture
def prepare_mocks(mocker) -> CreateUserMock:
    return CreateUserMock(mocker)


def check_asserts(prepare_mocks: CreateUserMock,
                  cup_count=1,
                  esc_count=1,
                  gut_count=1,
                  vun_count=1,
                  opj_count=1,
                  gkh_count=1):
    assert prepare_mocks.check_users_presence.call_count == cup_count, "User presence wasn't verified."
    assert prepare_mocks.execute_system_command.call_count == esc_count, "User wasn't created."
    assert prepare_mocks.get_users_token.call_count == gut_count, "Token wasn't taken."
    assert prepare_mocks.validate_user_name.call_count == vun_count, "User wasn't validated."
    assert prepare_mocks.path_join.call_count == opj_count, "Folder wasn't generated."
    assert prepare_mocks.get_kubectl_host.call_count == gkh_count, "Kubectl host wasn't taken"


def test_create_user_success(prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username], catch_exceptions=False)

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output

    check_asserts(prepare_mocks)


def test_create_user_with_empty_username(prepare_mocks: CreateUserMock):  # noqa: F811
    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [], catch_exceptions=False)

    assert 'Missing argument "USERNAME"' in result.output


def test_create_user_with_non_empty_username(prepare_mocks: CreateUserMock):  # noqa: F811
    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output
    check_asserts(prepare_mocks)


def test_create_user_success_display_config(prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username, "-lo"])

    assert Texts.LIST_ONLY_HEADER in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_filename(prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()
    filename = "test-filename"
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username, "--filename", filename])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=filename) in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_error_saving_file(prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()
    filename = "test-filename"
    m = mock_open()
    with patch("builtins.open", m) as mocked_file:
        mocked_file.return_value.__enter__.side_effect = RuntimeError()
        result = runner.invoke(create, [test_username, "--filename", filename])

    assert Texts.CONFIG_SAVE_FAIL_INSTRUCTIONS_MSG in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_error_creating_file(mocker, prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()

    gkc_mock = mocker.patch(
        "commands.user.create.generate_kubeconfig", side_effect=RuntimeError)
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_CREATION_ERROR_MSG + " " + VERBOSE_RERUN_MSG in result.output
    assert gkc_mock.call_count == 1
    check_asserts(prepare_mocks)


def test_create_user_with_defined_status_only(prepare_mocks: CreateUserMock):  # noqa: F811
    prepare_mocks.is_user_created.return_value = False
    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output
    assert Texts.USER_NOT_READY_ERROR_MSG.format(
        username=test_username) in result.output

    check_asserts(prepare_mocks)


def test_create_user_with_l_and_f(prepare_mocks: CreateUserMock):  # noqa: F811

    runner = CliRunner()

    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create,
                               [test_username, "-lo", "-fl", "test-filename"])

    assert Texts.F_L_OPTIONS_EXCLUSION_ERROR_MSG in result.output
    assert result.exit_code == 1
    check_asserts(
        prepare_mocks,
        cup_count=0,
        esc_count=0,
        gut_count=0,
        vun_count=0,
        opj_count=0,
        gkh_count=0)
