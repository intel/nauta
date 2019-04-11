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

from http import HTTPStatus

from click.testing import CliRunner
import requests

from commands.user.upgrade import upgrade
from platform_resources.user import User

fake_response = requests.Response()
fake_response.status_code = HTTPStatus.OK

GET_USER_RESPONSES = {
    'aaa': fake_response,
    'bbb': None
}


def test_user_upgrade(mocker):
    mocker.patch('platform_resources.user.User.list').return_value = [User(name='aaa', uid=0),
                                                                      User(name='bbb', uid=1)]
    mocker.patch('commands.user.upgrade.K8sProxy')
    grm_client_mock = mocker.MagicMock()
    grm_client_mock.get_user = lambda x: GET_USER_RESPONSES[x]
    mocker.patch('commands.user.upgrade.GitRepoManagerClient').return_value = grm_client_mock

    runner = CliRunner()
    cli_result = runner.invoke(upgrade)

    assert cli_result.exit_code == 0


def test_user_upgrade_failure(mocker):
    mocker.patch('platform_resources.user.User.list').side_effect = RuntimeError

    runner = CliRunner()
    cli_result = runner.invoke(upgrade)

    assert cli_result.exit_code == 1
