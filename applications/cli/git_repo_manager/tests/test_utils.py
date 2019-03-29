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
from unittest.mock import MagicMock

from git_repo_manager.utils import get_git_private_key_path, upload_experiment_to_git_repo_manager, \
    create_gitignore_file_for_experiments


def test_get_git_private_key_path(mocker, tmpdir):
    fake_secret = MagicMock()
    fake_key = 'private ssh key'
    fake_username = 'fake-user'
    fake_secret.data = {'private_key': base64.encodebytes(str.encode(fake_key)).decode(encoding='utf-8')}
    get_secret_mock = mocker.patch('git_repo_manager.utils.get_secret', return_value=fake_secret)
    config_dir = tmpdir.mkdir('config')
    private_key_file = config_dir.join(f'.{fake_username}-ssh-key')

    get_git_private_key_path(config_dir=config_dir, username=fake_username)

    get_secret_mock.assert_called_with(namespace=fake_username, secret_name='git-secret')
    assert private_key_file.read() == fake_key


def test_get_git_private_key_path_exists(mocker, tmpdir):
    fake_secret = MagicMock()
    fake_key = 'private ssh key'
    fake_username = 'fake-user'
    fake_secret.data = {'private_key': base64.encodebytes(str.encode(fake_key)).decode(encoding='utf-8')}
    get_secret_mock = mocker.patch('git_repo_manager.utils.get_secret', return_value=fake_secret)
    config_dir = tmpdir.mkdir('config')
    private_key_file = config_dir.join(f'.{fake_username}-ssh-key')
    private_key_file.write(fake_key)

    get_git_private_key_path(config_dir=config_dir, username=fake_username)

    assert get_secret_mock.call_count == 0
    assert private_key_file.read() == fake_key


def test_upload_experiment_to_git_repo_manager(mocker, tmpdir):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_git_private_key_path',
                                             return_value='/fake-config/.fake-user-ssh-key')
    external_cli_mock = mocker.patch('git_repo_manager.utils.ExternalCliClient')
    git_command_mock = MagicMock()
    git_command_mock.branch.return_value = '', 0, ''
    external_cli_mock.return_value = git_command_mock
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir(experiment_name)

    upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, experiment_name=experiment_name,
                                          run_name=experiment_name, username='fake-user')

    assert config_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert proxy_mock.call_count == 1

    # Assert clone bare repo & pull flow
    assert git_command_mock.remote.call_count == 1

    assert git_command_mock.clone.call_count == 1

    assert git_command_mock.config.call_count == 2
    assert git_command_mock.checkout.call_count == 1
    assert git_command_mock.pull.call_count == 0
    assert git_command_mock.add.call_count == 1
    assert git_command_mock.commit.call_count == 1
    assert git_command_mock.tag.call_count == 1
    assert git_command_mock.push.call_count == 2


def test_upload_experiment_to_git_repo_manager_already_cloned(mocker, tmpdir):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_git_private_key_path',
                                             return_value='/fake-config/.fake-user-ssh-key')
    external_cli_mock = mocker.patch('git_repo_manager.utils.ExternalCliClient')
    git_command_mock = MagicMock()
    git_command_mock.branch.return_value = '', 0, ''
    external_cli_mock.return_value = git_command_mock
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir('.nauta-git-fake-user')
    experiments_workdir.mkdir(experiment_name)

    upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, experiment_name=experiment_name,
                                          run_name=experiment_name, username='fake-user')

    assert config_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert proxy_mock.call_count == 1

    assert git_command_mock.remote.call_count == 1

    assert git_command_mock.clone.call_count == 0

    assert git_command_mock.config.call_count == 2
    assert git_command_mock.checkout.call_count == 1
    assert git_command_mock.pull.call_count == 0
    assert git_command_mock.add.call_count == 1
    assert git_command_mock.commit.call_count == 1
    assert git_command_mock.tag.call_count == 1
    assert git_command_mock.push.call_count == 2


def test_upload_experiment_to_git_repo_manager_error(mocker, tmpdir):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_git_private_key_path',
                                             return_value='/fake-config/.fake-user-ssh-key')
    external_cli_mock = mocker.patch('git_repo_manager.utils.ExternalCliClient')
    git_command_mock = MagicMock()
    git_command_mock.branch.return_value = '', 0, ''
    external_cli_mock.return_value = git_command_mock
    git_command_mock.push.side_effect = RuntimeError
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir('.nauta-git-fake-user')
    experiments_workdir.mkdir(experiment_name)

    with pytest.raises(RuntimeError):
        upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, run_name=experiment_name,
                                              experiment_name=experiment_name, username='fake-user')

    assert config_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert proxy_mock.call_count == 1

    # Check if rollback was called
    assert git_command_mock.reset.call_count == 1


def test_create_gitignore_file_for_experiments(tmpdir):
    experiments_workdir = tmpdir.mkdir('experiments')
    gitignore_file = experiments_workdir.join('.gitignore')

    create_gitignore_file_for_experiments(experiments_workdir)

    assert gitignore_file.read() == 'charts/*'
