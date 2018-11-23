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

import base64

import pytest
from click.testing import CliRunner
from unittest.mock import patch, mock_open

from platform_resources.user_model import User, UserStatus
from commands.user.create import check_users_presence, generate_kubeconfig, create, UserState
from util.helm import delete_user, delete_helm_release
from util.k8s.kubectl import NamespaceStatus
from cli_text_consts import VERBOSE_RERUN_MSG, UserCreateCmdTexts as Texts

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
    # certificate-authority-data: {test_cacert_encoded}
    # BUG/TASK: CAN-261
    insecure-skip-tls-verify: true
  name: dls-cluster
contexts:
- context:
    cluster: dls-cluster
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
    mocker.patch(
        "util.k8s.kubectl.find_namespace",
        return_value=NamespaceStatus.NOT_EXISTS)
    mocker.patch(
        "util.k8s.kubectl.users_api.get_user_data", return_value=user_data)

    assert check_users_presence(test_username) == UserState.ACTIVE

    mocker.patch(
        "util.k8s.kubectl.find_namespace", return_value=NamespaceStatus.ACTIVE)
    assert check_users_presence(test_username) == UserState.ACTIVE


def test_check_users_presence_failure(mocker):
    mocker.patch(
        "util.k8s.kubectl.find_namespace",
        return_value=NamespaceStatus.NOT_EXISTS)
    mocker.patch(
        "util.k8s.kubectl.users_api.get_user_data", return_value=user_data)

    assert check_users_presence(
        test_username + "_wrong") == UserState.NOT_EXISTS


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

    fake_config_path = '/usr/ogorek/dlsctl_config'
    fake_config = mocker.patch('util.helm.Config')
    fake_config.return_value.config_path = fake_config_path

    delete_helm_release(test_username)

    esc_mock.call_count == 1


def test_delete_helm_release_failure(mocker):
    mocker.patch("util.helm.execute_system_command", return_value=("", 1, ""))
    fake_config_path = '/usr/ogorek/dlsctl_config'
    fake_config = mocker.patch('util.helm.Config')
    fake_config.return_value.config_path = fake_config_path
    with pytest.raises(RuntimeError):
        delete_helm_release(test_username)


def test_delete_user_success(mocker):
    dns_mock = mocker.patch("util.helm.delete_namespace")
    dhr_mock = mocker.patch("util.helm.delete_helm_release")

    fake_config_path = '/usr/ogorek/dlsctl_config'
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


def test_create_user_failure(mocker):  # noqa: F811
    cup_mock = mocker.patch(
        "commands.user.create.check_users_presence",
        return_value=UserState.ACTIVE)
    esc_mock = mocker.patch(
        "commands.user.create.execute_system_command", return_value=("", 0))
    gut_mock = mocker.patch(
        "commands.user.create.get_users_token",
        return_value=test_samba_password)
    vun_mock = mocker.patch("commands.user.create.validate_user_name")
    icu_mock = mocker.patch(
        "commands.user.create.is_current_user_administrator",
        return_value=True)

    runner = CliRunner()
    runner.invoke(create, [test_username])

    assert cup_mock.call_count == 1, "users presence wasn't checked"
    assert esc_mock.call_count == 0, "user was created"
    assert gut_mock.call_count == 0, "users password was taken"
    assert vun_mock.call_count == 1, "username wasn't validated"
    assert icu_mock.call_count == 1, "admin wasn't checked"


def test_create_user_terminating(mocker):  # noqa: F811
    cup_mock = mocker.patch(
        "commands.user.create.check_users_presence",
        return_value=UserState.TERMINATING)
    esc_mock = mocker.patch(
        "commands.user.create.execute_system_command", return_value=("", 0))
    gut_mock = mocker.patch(
        "commands.user.create.get_users_token",
        return_value=test_samba_password)
    vun_mock = mocker.patch("commands.user.create.validate_user_name")
    icu_mock = mocker.patch(
        "commands.user.create.is_current_user_administrator",
        return_value=True)

    runner = CliRunner()
    result = runner.invoke(create, [test_username])

    assert Texts.USER_BEING_REMOVED_ERROR_MSG.format(
        username=test_username) in result.output

    assert cup_mock.call_count == 1, "users presence wasn't checked"
    assert esc_mock.call_count == 0, "user was created"
    assert gut_mock.call_count == 0, "users password was taken"
    assert vun_mock.call_count == 1, "username wasn't validated"
    assert icu_mock.call_count == 1, "admin wasn't checked"


def test_create_user_not_admin(mocker):  # noqa: F811
    cup_mock = mocker.patch(
        "commands.user.create.check_users_presence", return_value=False)
    vun_mock = mocker.patch("commands.user.create.validate_user_name")
    icu_mock = mocker.patch(
        "commands.user.create.is_current_user_administrator",
        return_value=False)

    runner = CliRunner()
    result = runner.invoke(create, [test_username])

    assert Texts.USER_NOT_ADMIN_ERROR_MSG in result.output

    assert cup_mock.call_count == 0, "users presence wasn't checked"
    assert vun_mock.call_count == 1, "username wasn't validated"
    assert icu_mock.call_count == 1, "admin wasn't checked"


def test_create_user_incorrect_name(mocker):  # noqa: F811
    vun_mock = mocker.patch(
        "commands.user.create.validate_user_name",
        side_effect=ValueError("error"))
    icu_mock = mocker.patch(
        "commands.user.create.is_current_user_administrator",
        return_value=False)

    runner = CliRunner()
    result = runner.invoke(create, [test_username])

    assert "error" in result.output

    assert vun_mock.call_count == 1, "username wasn't validated"
    assert icu_mock.call_count == 0, "admin wasn't checked"


class CreateUserMock():
    def __init__(self, cup: None, esc: None, gut: None, vun: None, icu: None,
                 opj: None, ccl: None, cnm: None, gkh: None, iuc: None):
        self.cup = cup
        self.esc = esc
        self.gut = gut
        self.vun = vun
        self.icu = icu
        self.opj = opj
        self.ccl = ccl
        self.cnm = cnm
        self.gkh = gkh
        self.iuc = iuc


@pytest.fixture
def prepare_mocks(mocker) -> CreateUserMock:
    cup_mock = mocker.patch(
        "commands.user.create.check_users_presence", return_value=False)
    esc_mock = mocker.patch(
        "commands.user.create.execute_system_command",
        return_value=("", 0, ""))
    gut_mock = mocker.patch(
        "commands.user.create.get_users_token",
        return_value=test_samba_password)
    vun_mock = mocker.patch("commands.user.create.validate_user_name")
    icu_mock = mocker.patch(
        "commands.user.create.is_current_user_administrator",
        return_value=True)
    opj_mock = mocker.patch("os.path.join", return_value="folder")
    iuc_mock = mocker.patch(
        "commands.user.create.is_user_created", return_value=True)
    config_class_mock = mocker.patch('commands.user.create.Config')
    config_instance_mock = config_class_mock.return_value
    config_instance_mock.config_path = "test"
    config_map_class_mock = mocker.patch("commands.user.create.DLS4EConfigMap")
    config_map_instance = config_map_class_mock.return_value
    config_map_instance.tiller_location = "image_tiller"

    gkh_mock = mocker.patch("commands.user.create.get_kubectl_host")
    gkh_mock.return_value = "localhost"

    return CreateUserMock(
        cup=cup_mock,
        esc=esc_mock,
        gut=gut_mock,
        vun=vun_mock,
        icu=icu_mock,
        opj=opj_mock,
        ccl=config_instance_mock,
        cnm=config_map_instance,
        gkh=gkh_mock,
        iuc=iuc_mock)


def check_asserts(prepare_mocks: CreateUserMock,
                  cup_count=1,
                  esc_count=1,
                  gut_count=1,
                  vun_count=1,
                  icu_count=1,
                  opj_count=1,
                  gkh_count=1,
                  iuc_count=1):
    assert prepare_mocks.cup.call_count == cup_count, "User presence wasn't verified."
    assert prepare_mocks.esc.call_count == esc_count, "User wasn't created."
    assert prepare_mocks.gut.call_count == gut_count, "Token wasn't taken."
    assert prepare_mocks.vun.call_count == vun_count, "User wasn't validated."
    assert prepare_mocks.icu.call_count == icu_count, "Users wasn't checked as an admin."
    assert prepare_mocks.opj.call_count == opj_count, "Folder wasn't generated."
    assert prepare_mocks.gkh.call_count == gkh_count, "Kubectl host wasn't taken"
    assert prepare_mocks.iuc.call_count == iuc_count, "User's state wasn't checked"


def test_create_user_success(mocker, prepare_mocks):  # noqa: F811

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output

    check_asserts(prepare_mocks)


def test_create_user_with_empty_username(mocker, prepare_mocks):  # noqa: F811
    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [])

    assert 'Missing argument "USERNAME"' in result.output
    check_asserts(
        prepare_mocks,
        cup_count=0,
        esc_count=0,
        gut_count=0,
        vun_count=0,
        icu_count=0,
        opj_count=0,
        gkh_count=0,
        iuc_count=0)


def test_create_user_with_non_empty_username(mocker,
                                             prepare_mocks):  # noqa: F811
    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output
    check_asserts(prepare_mocks)


def test_create_user_success_display_config(mocker,
                                            prepare_mocks):  # noqa: F811

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username, "-l"])

    assert Texts.LIST_ONLY_HEADER in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_filename(mocker,
                                           prepare_mocks):  # noqa: F811

    runner = CliRunner()
    filename = "test-filename"
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username, "-f", filename])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=filename) in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_error_saving_file(
        mocker, prepare_mocks):  # noqa: F811

    runner = CliRunner()
    filename = "test-filename"
    m = mock_open()
    with patch("builtins.open", m) as mocked_file:
        mocked_file.return_value.__enter__.side_effect = RuntimeError()
        result = runner.invoke(create, [test_username, "-f", filename])

    assert Texts.CONFIG_SAVE_FAIL_INSTRUCTIONS_MSG in result.output

    check_asserts(prepare_mocks)


def test_create_user_success_with_error_creating_file(
        mocker, prepare_mocks):  # noqa: F811

    runner = CliRunner()

    gkc_mock = mocker.patch(
        "commands.user.create.generate_kubeconfig", side_effect=RuntimeError)
    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_CREATION_ERROR_MSG + " " + VERBOSE_RERUN_MSG in result.output
    assert gkc_mock.call_count == 1
    check_asserts(prepare_mocks)


def test_create_user_with_defined_status_only(mocker,
                                              prepare_mocks):  # noqa: F811
    runner = CliRunner()
    m = mock_open()
    prepare_mocks.iuc.return_value = False
    with patch("builtins.open", m):
        result = runner.invoke(create, [test_username])

    assert Texts.CONFIG_SAVE_SUCCESS_MSG.format(
        filename=test_username + ".config") in result.output
    assert Texts.USER_NOT_READY_ERROR_MSG.format(
        username=test_username) in result.output

    check_asserts(prepare_mocks)


def test_create_user_with_l_and_f(mocker, prepare_mocks):  # noqa: F811

    runner = CliRunner()

    m = mock_open()
    with patch("builtins.open", m):
        result = runner.invoke(create,
                               [test_username, "-l", "-f", "test-filename"])

    assert Texts.F_L_OPTIONS_EXCLUSION_ERROR_MSG in result.output
    assert result.exit_code == 1
    check_asserts(
        prepare_mocks,
        cup_count=0,
        esc_count=0,
        gut_count=0,
        vun_count=0,
        icu_count=0,
        opj_count=0,
        gkh_count=0,
        iuc_count=0)
