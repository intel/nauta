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

from commands.user import list_users
from platform_resources.user_model import User, UserStatus


TEST_USERS = [User(name='test-dev', uid=1, state=UserStatus.DEFINED,
                   creation_timestamp='2018-05-17T12:49:04Z',
                   experiment_runs=[]),
              User(name='test-user', uid=100,
                   state=UserStatus.DEFINED, creation_timestamp='2018-05-17T11:42:22Z',
                   experiment_runs=[])]


def test_list_users_success(mocker):
    api_list_users_mock = mocker.patch("commands.user.list_users.users_api.list_users")
    api_list_users_mock.return_value = TEST_USERS

    runner = CliRunner()
    runner.invoke(list_users.list_users, [])

    assert api_list_users_mock.call_count == 1, "Users were not retrieved"


def test_list_users_failure(mocker):
    api_list_users_mock = mocker.patch("commands.user.list_users.users_api.list_users")
    api_list_users_mock.side_effect = RuntimeError

    sys_exit_mock = mocker.patch("sys.exit")

    runner = CliRunner()

    runner.invoke(list_users.list_users, [])

    assert api_list_users_mock.call_count == 1, "Users retrieval was not called"
    assert sys_exit_mock.called_once_with(1)
