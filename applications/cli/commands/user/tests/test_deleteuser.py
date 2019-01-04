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

from click.testing import CliRunner

from commands.user import delete
from util.k8s.kubectl import UserState
from cli_text_consts import UserDeleteCmdTexts as Texts


TEST_USERNAME = "testusername"


def test_deleteuser_success(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    gcm_mock = mocker.patch("commands.user.delete.get_config_map_data")
    pcm_mock = mocker.patch("commands.user.delete.patch_config_map_data")
    gcm_mock.return_value = {}

    mocker.patch("click.confirm", return_value=True)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert icu_mock.call_count == 1
    assert gcm_mock.call_count == 1
    assert pcm_mock.call_count == 1

    assert Texts.DELETE_SUCCESS_MSG.format(username=TEST_USERNAME) in result.output


def test_deleteuser_missing_user(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", return_value=UserState.NOT_EXISTS)
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1

    assert Texts.USER_NOT_EXISTS_ERROR_MSG.format(username=TEST_USERNAME) in result.output
    assert result.exit_code == 1


def test_deleteuser_checking_user_errors(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=RuntimeError)
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1

    assert Texts.USER_PRESENCE_VERIFICATION_ERROR_MSG in result.output
    assert result.exit_code == 1


def test_deleteuser_deleting_user_errors(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", return_value=True)
    deu_mock = mocker.patch("commands.user.delete.delete_user", side_effect=RuntimeError)
    mocker.patch("click.confirm", return_value=True)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 1
    assert icu_mock.call_count == 1

    assert Texts.OTHER_ERROR_USER_MSG in result.output
    assert result.exit_code == 1


def test_deleteuser_missing_argument(mocker):
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", return_value=True)
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    result = CliRunner().invoke(delete.delete, [])

    assert cup_mock.call_count == 0
    assert deu_mock.call_count == 0

    assert "Missing argument" in result.output
    assert result.exit_code == 2


def test_deleteuser_answer_n(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", return_value=True)
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    gcm_mock = mocker.patch("commands.user.delete.get_config_map_data")
    pcm_mock = mocker.patch("commands.user.delete.patch_config_map_data")

    mocker.patch("click.confirm", return_value=False)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1
    assert gcm_mock.call_count == 0
    assert pcm_mock.call_count == 0

    assert Texts.DELETE_ABORT_MSG in result.output


def test_deleteuser_purge_success(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", return_value=True)
    gcm_mock = mocker.patch("commands.user.delete.get_config_map_data")
    pcm_mock = mocker.patch("commands.user.delete.patch_config_map_data")
    gcm_mock.return_value = {}

    mocker.patch("click.confirm", return_value=True)

    CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert icu_mock.call_count == 1
    assert gcm_mock.call_count == 1
    assert pcm_mock.call_count == 1


def test_deleteuser_purge_failure(mocker):
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", side_effect=RuntimeError)
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    gcm_mock = mocker.patch("commands.user.delete.get_config_map_data")
    pcm_mock = mocker.patch("commands.user.delete.patch_config_map_data")
    gcm_mock.return_value = {}

    mocker.patch("click.confirm", return_value=True)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert Texts.PURGE_ERROR_MSG in result.output
    assert icu_mock.call_count == 1
    assert gcm_mock.call_count == 1
    assert pcm_mock.call_count == 1


def test_deleteuser_not_admin(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=False)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert Texts.USER_NOT_ADMIN_ERROR_MSG in result.output
    assert icu_mock.call_count == 1


def test_deleteuser_purge_success_wait_for_deletion(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, True, True, True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", return_value=True)
    gcm_mock = mocker.patch("commands.user.delete.get_config_map_data")
    pcm_mock = mocker.patch("commands.user.delete.patch_config_map_data")
    gcm_mock.return_value = {}

    mocker.patch("click.confirm", return_value=True)

    CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 5
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert icu_mock.call_count == 1
    assert gcm_mock.call_count == 4
    assert pcm_mock.call_count == 1
