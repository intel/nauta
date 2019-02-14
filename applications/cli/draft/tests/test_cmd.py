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

import pytest

from cli_text_consts import DraftCmdTexts
import draft
from draft.cmd import create, up
import util.helm


@pytest.fixture
def cmd_mock(mocker):
    # 'create' mock
    mocker.patch('draft.cmd.Config', return_value=mocker.MagicMock(get_config_path=lambda: '/home/user/config'))
    mocker.patch('os.path.isdir', return_value=True)
    mocker.patch('draft.cmd.copytree_content')
    mocker.patch('os.makedirs')

    # 'up' mock
    fake_pack_to_be_installed = 'my-pack'
    docker_client_mock = mocker.MagicMock()
    mocker.patch('docker.from_env', new=lambda: docker_client_mock)
    mocker.patch('os.listdir', return_value=[fake_pack_to_be_installed])
    mocker.patch('util.helm.install_helm_chart')

    return docker_client_mock


# noinspection PyUnresolvedReferences,PyUnusedLocal
def test_create(cmd_mock):
    output, exit_code = create('/home/fake_dir', 'fake_pack')

    assert output == ""
    assert exit_code == 0
    assert draft.cmd.copytree_content.call_count == 2


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_create_no_pack(mocker, cmd_mock):
    mocker.patch('os.path.isdir', return_value=False)

    output, exit_code = create('/home/fake_dir', 'fake_pack')

    assert output == DraftCmdTexts.PACK_NOT_EXISTS
    assert exit_code == 1
    assert draft.cmd.copytree_content.call_count == 0


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_create_other_error(mocker, cmd_mock):
    mocker.patch('draft.cmd.copytree_content', side_effect=PermissionError)

    output, exit_code = create('/home/fake_dir', 'fake_pack')

    assert output == DraftCmdTexts.DEPLOYMENT_NOT_CREATED
    assert exit_code == 100
    assert draft.cmd.copytree_content.call_count == 1


# noinspection PyUnusedLocal
def test_up(mocker, cmd_mock):
    output, exit_code = up('my-run', local_registry_port=12345, working_directory='/home/user/config', namespace='user')

    assert output == ""
    assert exit_code == 0
    assert cmd_mock.images.build.call_count == 1
    assert cmd_mock.images.push.call_count == 1
    # noinspection PyUnresolvedReferences
    assert '/home/user/config/charts/my-pack' in util.helm.install_helm_chart.call_args[0]


# noinspection PyUnusedLocal
def test_up_build_error(mocker, cmd_mock):
    docker_client_mock = mocker.MagicMock()
    docker_client_mock.images.build = lambda: RuntimeError
    mocker.patch('docker.from_env', new=lambda: docker_client_mock)

    output, exit_code = up('my-run', local_registry_port=12345, working_directory='/home/user/config', namespace='user')

    assert output == DraftCmdTexts.DOCKER_IMAGE_NOT_BUILT
    assert exit_code == 100
    assert docker_client_mock.images.push.call_count == 0


# noinspection PyUnusedLocal
def test_up_push_error(mocker, cmd_mock):
    docker_client_mock = mocker.MagicMock()
    docker_client_mock.images.push = lambda: RuntimeError
    mocker.patch('docker.from_env', new=lambda: docker_client_mock)

    output, exit_code = up('my-run', local_registry_port=12345, working_directory='/home/user/config', namespace='user')

    assert output == DraftCmdTexts.DOCKER_IMAGE_NOT_SENT
    assert exit_code == 101


# noinspection PyUnusedLocal
def test_up_helm_install_error(mocker, cmd_mock):
    mocker.patch('util.helm.install_helm_chart', side_effect=RuntimeError)

    output, exit_code = up('my-run', local_registry_port=12345, working_directory='/home/user/config', namespace='user')

    assert output == DraftCmdTexts.APP_NOT_RELEASED
    assert exit_code == 102
