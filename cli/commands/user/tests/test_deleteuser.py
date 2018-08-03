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

from click.testing import CliRunner

from commands.user import delete
from util.k8s.kubectl import UserState

TEST_USERNAME = "testusername"


def test_deleteuser_success(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    mocker.patch("click.confirm", return_value=True)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert icu_mock.call_count == 1

    assert f"User {TEST_USERNAME} has been deleted." in result.output


def test_deleteuser_missing_user(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", return_value=UserState.NOT_EXISTS)
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1

    assert f"User {TEST_USERNAME} doesn't exists." in result.output
    assert result.exit_code == 1


def test_deleteuser_checking_user_errors(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=RuntimeError)
    deu_mock = mocker.patch("commands.user.delete.delete_user")

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1

    assert "Problems during verifying users presence." in result.output
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

    assert "User hasn't been deleted due to technical reasons." in result.output
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
    mocker.patch("click.confirm", return_value=False)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME])

    assert cup_mock.call_count == 1
    assert deu_mock.call_count == 0
    assert icu_mock.call_count == 1

    assert "Operation of deleting of a user was aborted." in result.output


def test_deleteuser_purge_success(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", return_value=True)

    mocker.patch("click.confirm", return_value=True)

    CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert icu_mock.call_count == 1


def test_deleteuser_purge_failure(mocker):
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", side_effect=RuntimeError)
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)

    mocker.patch("click.confirm", return_value=True)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 2
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert "Some artifacts belonging to a user weren't removed." in result.output
    assert icu_mock.call_count == 1


def test_deleteuser_not_admin(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=False)

    result = CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert "Only administrators can delete users." in result.output
    assert icu_mock.call_count == 1


def test_deleteuser_purge_success_wait_for_deletion(mocker):
    icu_mock = mocker.patch("commands.user.delete.is_current_user_administrator", return_value=True)
    cup_mock = mocker.patch("commands.user.delete.check_users_presence", side_effect=[True, True, True, True, False])
    deu_mock = mocker.patch("commands.user.delete.delete_user")
    prg_mock = mocker.patch("commands.user.delete.purge_user", return_value=True)

    mocker.patch("click.confirm", return_value=True)

    CliRunner().invoke(delete.delete, [TEST_USERNAME, "-p"])

    assert cup_mock.call_count == 5
    assert deu_mock.call_count == 1
    assert prg_mock.call_count == 1
    assert icu_mock.call_count == 1
