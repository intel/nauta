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

from git_repo_manager.utils import get_fake_ssh_path, upload_experiment_to_git_repo_manager, \
    create_gitignore_file_for_experiments, compute_hash_of_k8s_env_address, delete_exp_tag_from_git_repo_manager


def test_get_fake_ssh_path(mocker, tmpdir):
    fake_secret = MagicMock()
    fake_key = 'private ssh key'
    fake_username = 'fake-user'
    fake_hash = 'a12b34c'
    fake_secret.data = {'private_key': base64.encodebytes(str.encode(fake_key)).decode(encoding='utf-8')}
    get_secret_mock = mocker.patch('git_repo_manager.utils.get_secret', return_value=fake_secret)
    env_hash_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value=fake_hash)
    config_dir = tmpdir.mkdir('config')
    private_key_file = config_dir.join(f'.ssh-key-{fake_username}-{fake_hash}')
    fake_ssh_file = config_dir.join(f'ssh-{fake_username}-{fake_hash}')
    get_fake_ssh_path(config_dir=config_dir, username=fake_username)

    get_secret_mock.assert_called_with(namespace=fake_username, secret_name='git-secret')
    assert env_hash_mock.call_count == 1
    assert private_key_file.read() == fake_key
    assert "ssh -i" in fake_ssh_file.read()


def test_get_fake_ssh_path_exists(mocker, tmpdir):
    fake_secret = MagicMock()
    fake_key = 'private ssh key'
    fake_username = 'fake-user'
    fake_hash = 'a12b34c'
    fake_secret.data = {'private_key': base64.encodebytes(str.encode(fake_key)).decode(encoding='utf-8')}

    get_secret_mock = mocker.patch('git_repo_manager.utils.get_secret', return_value=fake_secret)
    env_hash_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value=fake_hash)
    config_dir = tmpdir.mkdir('config')
    private_key_file = config_dir.join(f'.ssh-key-{fake_username}-{fake_hash}')
    private_key_file.write(fake_key)
    fake_ssh = f'ssh -i key_file -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $*'
    fake_ssh_file = config_dir.join(f'ssh-{fake_username}-{fake_hash}')
    fake_ssh_file.write(fake_ssh)

    get_fake_ssh_path(config_dir=config_dir, username=fake_username)

    assert get_secret_mock.call_count == 0
    assert env_hash_mock.call_count == 1
    assert private_key_file.read() == fake_key
    assert fake_ssh_file.read() == fake_ssh


@pytest.fixture()
def git_client_mock(mocker):
    external_cli_mock = mocker.patch('git_repo_manager.utils.ExternalCliClient')
    git_command_mock = MagicMock()
    git_command_mock.branch.return_value = '', 0, ''
    git_command_mock._make_command.return_value = lambda: ('', 0, '')  # Mock manually created commands
    external_cli_mock.return_value = git_command_mock
    return git_command_mock


def test_upload_experiment_to_git_repo_manager(mocker, tmpdir, git_client_mock):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_fake_ssh_path',
                                             return_value='/fake-config/ssh')
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')
    fake_hash = 'a12b34c'
    env_hash_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value=fake_hash)

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir(experiment_name)

    upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, experiment_name=experiment_name,
                                          run_name=experiment_name, username='fake-user')

    assert env_hash_mock.call_count == 1
    assert config_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert proxy_mock.call_count == 1

    # Assert clone bare repo & pull flow
    assert git_client_mock.remote.call_count == 1

    assert git_client_mock.clone.call_count == 1

    assert git_client_mock.config.call_count == 3
    assert git_client_mock.checkout.call_count == 1
    assert git_client_mock.pull.call_count == 0
    assert git_client_mock.add.call_count == 1
    assert git_client_mock.commit.call_count == 1
    assert git_client_mock.tag.call_count == 1
    assert git_client_mock.push.call_count == 2


def test_upload_experiment_to_git_repo_manager_already_cloned(mocker, tmpdir, git_client_mock):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_fake_ssh_path',
                                             return_value='/fake-config/ssh')
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')
    fake_hash = 'a12b34c'
    env_hash_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value=fake_hash)

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir(f'.nauta-git-fake-user-{fake_hash}')
    experiments_workdir.mkdir(experiment_name)


    upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, experiment_name=experiment_name,
                                          run_name=experiment_name, username='fake-user')

    assert env_hash_mock.call_count == 1
    assert config_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert proxy_mock.call_count == 1

    assert git_client_mock.remote.call_count == 1

    assert git_client_mock.clone.call_count == 0

    assert git_client_mock.config.call_count == 3
    assert git_client_mock.checkout.call_count == 1
    assert git_client_mock.pull.call_count == 0
    assert git_client_mock.add.call_count == 1
    assert git_client_mock.commit.call_count == 1
    assert git_client_mock.tag.call_count == 1
    assert git_client_mock.push.call_count == 2


def test_upload_experiment_to_git_repo_manager_error(mocker, tmpdir, git_client_mock):
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_fake_ssh_path',
                                             return_value='/fake-config/ssh')
    git_client_mock.push.side_effect = RuntimeError
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    config_mock = mocker.patch('git_repo_manager.utils.Config')
    fake_hash = 'a12b34c'
    env_hash_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value=fake_hash)

    experiment_name = 'fake-experiment'
    experiments_workdir = tmpdir.mkdir(f'experiments')
    experiments_workdir.mkdir(f'.nauta-git-fake-user-{fake_hash}')
    experiments_workdir.mkdir(experiment_name)

    with pytest.raises(RuntimeError):
        upload_experiment_to_git_repo_manager(experiments_workdir=experiments_workdir, run_name=experiment_name,
                                              experiment_name=experiment_name, username='fake-user')

    # function is retried 5 times
    assert env_hash_mock.call_count == 5
    assert config_mock.call_count == 5
    assert get_private_key_path_mock.call_count == 5
    assert proxy_mock.call_count == 5

    # Check if rollback was called
    assert git_client_mock.reset.call_count == 5


def test_create_gitignore_file_for_experiments(tmpdir):
    experiments_workdir = tmpdir.mkdir('experiments')
    gitignore_file = experiments_workdir.join('.gitignore')

    create_gitignore_file_for_experiments(experiments_workdir)

    assert gitignore_file.read() == 'charts/*'


def test_compute_hash_of_k8s_env_address(mocker):
    mocker.patch('git_repo_manager.utils.get_kubectl_host', return_value='http://some.host:1234')
    assert compute_hash_of_k8s_env_address() == 'cc1a4a407dab8411a13897809514c945'


def test_delete_exp_tag_from_git_repo_manager_experiments_dir_not_exist(mocker):
    config_mock = mocker.patch('git_repo_manager.utils.Config')
    compute_hash_of_k8s_env_address_mock = mocker.patch('git_repo_manager.utils.compute_hash_of_k8s_env_address', return_value='some_hash')
    get_private_key_path_mock = mocker.patch('git_repo_manager.utils.get_fake_ssh_path')
    external_cli_mock = mocker.patch('git_repo_manager.utils.ExternalCliClient')
    git_command_mock = MagicMock()
    git_command_mock.tag.return_value = '', 0, ''
    external_cli_mock.return_value = git_command_mock
    proxy_mock = mocker.patch('git_repo_manager.utils.TcpK8sProxy')
    os_path_is_dir_mock = mocker.patch('os.path.isdir', return_value=False)
    os_makedirs_mock = mocker.patch('os.makedirs')

    delete_exp_tag_from_git_repo_manager(username='user', experiment_name='exp-1', experiments_workdir='workdir')

    assert config_mock.call_count == 1
    assert compute_hash_of_k8s_env_address_mock.call_count == 1
    assert get_private_key_path_mock.call_count == 1
    assert external_cli_mock.call_count == 1
    assert proxy_mock.call_count == 1
    assert os_path_is_dir_mock.call_count == 2
    assert os_makedirs_mock.call_count == 1
