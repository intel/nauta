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

from commands.user import list_users
from platform_resources.user import User, UserStatus


TEST_USERS = [User(name='test-dev', uid=1, state=UserStatus.DEFINED,
                   creation_timestamp='2018-05-17T12:49:04Z',
                   experiment_runs=[]),
              User(name='test-user', uid=100,
                   state=UserStatus.DEFINED, creation_timestamp='2018-05-17T11:42:22Z',
                   experiment_runs=[])]


def test_list_users_success(mocker):
    api_list_users_mock = mocker.patch("commands.user.list_users.User.list")
    api_list_users_mock.return_value = TEST_USERS

    runner = CliRunner()
    runner.invoke(list_users.list_users, [])

    assert api_list_users_mock.call_count == 1, "Users were not retrieved"


def test_list_users_failure(mocker):
    api_list_users_mock = mocker.patch("commands.user.list_users.User.list")
    api_list_users_mock.side_effect = RuntimeError

    sys_exit_mock = mocker.patch("sys.exit")

    runner = CliRunner()

    runner.invoke(list_users.list_users, [])

    assert api_list_users_mock.call_count == 1, "Users retrieval was not called"
    assert sys_exit_mock.called_once_with(1)


def test_list_users_only_one(mocker):
    api_list_users_mock = mocker.patch("commands.user.list_users.User.list")
    api_list_users_mock.return_value = TEST_USERS

    runner = CliRunner()
    result = runner.invoke(list_users.list_users, ["-c", "1"])

    assert "test-user" in result.output
    assert "test-dev" not in result.output

    assert api_list_users_mock.call_count == 1, "Users were not retrieved"
