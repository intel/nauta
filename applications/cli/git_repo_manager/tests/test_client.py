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

from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError
from requests_mock import Mocker

from git_repo_manager.client import GitRepoManagerClient

FAKE_USER = 'fake-user'


@pytest.fixture()
def git_repo_manager(mocker) -> GitRepoManagerClient:
    grm = GitRepoManagerClient(host='fake.host')
    mocker.patch.object(grm, '_get_admin_token', return_value='token fake')
    return grm


def test_get_user(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    get_user_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=200)
    response = git_repo_manager.get_user(FAKE_USER)

    assert response
    assert get_user_mock.call_count == 1


def test_get_user_not_found(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    get_user_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=404)
    response = git_repo_manager.get_user(FAKE_USER)

    assert not response
    assert get_user_mock.call_count == 1


def test_get_user_error(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    get_user_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=500)
    with pytest.raises(HTTPError):
        git_repo_manager.get_user(FAKE_USER)

    assert get_user_mock.call_count == 1


def test_create_user_exists(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=200)
    post_user_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users')
    response = git_repo_manager.create_user(username=FAKE_USER, email='fake@fake.com')

    assert response
    assert post_user_mock.call_count == 0


def test_create_user_new(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=404)
    post_user_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users')
    response = git_repo_manager.create_user(username=FAKE_USER, email='fake@fake.com')

    assert response
    assert post_user_mock.call_count == 1


def test_create_user_error(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=404)
    post_user_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users', status_code=500)
    with pytest.raises(HTTPError):
        git_repo_manager.create_user(username=FAKE_USER, email='fake@fake.com')

    assert post_user_mock.call_count == 1


def test_delete_user(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=200)
    delete_user_mock = requests_mock.delete(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}')
    response = git_repo_manager.delete_user(username=FAKE_USER)

    assert response
    assert delete_user_mock.call_count == 1


def test_delete_user_does_not_exist(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    requests_mock.get(f'{git_repo_manager.base_url}/api/v1/users/{FAKE_USER}', status_code=404)
    delete_user_mock = requests_mock.delete(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}')
    response = git_repo_manager.delete_user(username=FAKE_USER)

    assert response is None
    assert delete_user_mock.call_count == 0


def test_add_public_key_for_user(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    add_key_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}/keys')
    response = git_repo_manager.add_public_key_for_user(username=FAKE_USER, public_key='fake-key')

    assert response
    assert add_key_mock.call_count == 1


def test_add_public_key_for_user_error(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    add_key_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}/keys',
                                      status_code=422)
    with pytest.raises(HTTPError):
        git_repo_manager.add_public_key_for_user(username=FAKE_USER, public_key='fake-key')

    assert add_key_mock.call_count == 1


def test_get_repository(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=200)
    response = git_repo_manager.get_repository(username=FAKE_USER, repository_name=repo_name)

    assert response
    assert get_repo_mock.call_count == 1


def test_get_repository_not_found(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=404)
    response = git_repo_manager.get_repository(username=FAKE_USER, repository_name=repo_name)

    assert not response
    assert get_repo_mock.call_count == 1


def test_get_repository_error(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=500)
    with pytest.raises(HTTPError):
        git_repo_manager.get_repository(username=FAKE_USER, repository_name=repo_name)

    assert get_repo_mock.call_count == 1


def test_create_repository(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=404)
    post_repo_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}/repos')
    response = git_repo_manager.create_repository(username=FAKE_USER, repository_name=repo_name)

    assert response
    assert get_repo_mock.call_count == 1
    assert post_repo_mock.call_count == 1


def test_create_repository_exists(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=200)
    post_repo_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}/repos')
    response = git_repo_manager.create_repository(username=FAKE_USER, repository_name=repo_name)

    assert response
    assert get_repo_mock.call_count == 1
    assert post_repo_mock.call_count == 0


def test_create_repository_error(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=404)
    post_repo_mock = requests_mock.post(f'{git_repo_manager.base_url}/api/v1/admin/users/{FAKE_USER}/repos',
                                        status_code=422)
    with pytest.raises(HTTPError):
        git_repo_manager.create_repository(username=FAKE_USER, repository_name=repo_name)

    assert get_repo_mock.call_count == 1
    assert post_repo_mock.call_count == 1


def test_delete_repository(requests_mock: Mocker, git_repo_manager: GitRepoManagerClient):
    repo_name = 'fake_repo'
    get_repo_mock = requests_mock.get(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}',
                                      status_code=200)
    delete_repo_mock = requests_mock.delete(f'{git_repo_manager.base_url}/api/v1/repos/{FAKE_USER}/{repo_name}')
    response = git_repo_manager.delete_repository(username=FAKE_USER, repository_name=repo_name)

    assert response
    assert get_repo_mock.call_count == 1
    assert delete_repo_mock.call_count == 1


def test_token_saved(mocker):
    fake_token = 'fake_token'
    secret_mock = MagicMock()
    secret_mock.data = {'token': fake_token}
    get_secret_mock = mocker.patch('git_repo_manager.client.get_secret', return_value=secret_mock)
    create_token_mock = mocker.patch('git_repo_manager.client.GitRepoManagerClient._create_admin_token')
    save_token_mock = mocker.patch('git_repo_manager.client.GitRepoManagerClient._save_admin_token')
    grm = GitRepoManagerClient(host='fake.host')

    assert grm.session is not None
    assert grm._token == f'token {fake_token}'
    assert get_secret_mock.call_count == 1
    assert create_token_mock.call_count == 0
    assert save_token_mock.call_count == 0


def test_token_create(mocker):
    fake_token = 'fake_token'
    secret_mock = MagicMock()
    secret_mock.data = {}
    get_secret_mock = mocker.patch('git_repo_manager.client.get_secret', return_value=secret_mock)
    create_token_mock = mocker.patch('git_repo_manager.client.GitRepoManagerClient._create_admin_token',
                                     return_value=fake_token)
    save_token_mock = mocker.patch('git_repo_manager.client.GitRepoManagerClient._save_admin_token')
    grm = GitRepoManagerClient(host='fake.host')

    assert grm.session is not None
    assert grm._token == f'token {fake_token}'
    assert get_secret_mock.call_count == 1
    assert create_token_mock.call_count == 1
    assert save_token_mock.call_count == 1


def test_add_nauta_user(mocker, git_repo_manager: GitRepoManagerClient):
    generate_key = mocker.patch.object(git_repo_manager, '_generate_ssh_key',
                                       return_value=('private-key', 'public-key'))
    create_user = mocker.patch.object(git_repo_manager, 'create_user')
    add_key = mocker.patch.object(git_repo_manager, 'add_public_key_for_user')
    create_repo = mocker.patch.object(git_repo_manager, 'create_repository')
    create_secret = mocker.patch('git_repo_manager.client.create_secret')

    git_repo_manager.add_nauta_user(username='test-user')

    assert generate_key.call_count == 1
    assert create_user.call_count == 1
    assert add_key.call_count == 1
    assert create_repo.call_count == 1
    assert create_secret.call_count == 1


def test_add_nauta_user_failure(mocker, git_repo_manager: GitRepoManagerClient):
    generate_key = mocker.patch.object(git_repo_manager, '_generate_ssh_key',
                                       return_value=('private-key', 'public-key'))
    create_user = mocker.patch.object(git_repo_manager, 'create_user', side_effect=RuntimeError)
    add_key = mocker.patch.object(git_repo_manager, 'add_public_key_for_user')
    create_repo = mocker.patch.object(git_repo_manager, 'create_repository')
    create_secret = mocker.patch('git_repo_manager.client.create_secret')

    with pytest.raises(RuntimeError):
        git_repo_manager.add_nauta_user(username='test-user')

    assert generate_key.call_count == 1
    assert create_user.call_count == 1
    assert add_key.call_count == 0
    assert create_repo.call_count == 0
    assert create_secret.call_count == 0


def test_delete_nauta_user(mocker, git_repo_manager: GitRepoManagerClient):
    delete_user = mocker.patch.object(git_repo_manager, 'delete_user')
    delete_repo = mocker.patch.object(git_repo_manager, 'delete_repository')

    git_repo_manager.delete_nauta_user(username='test-user')

    assert delete_user.call_count == 1
    assert delete_repo.call_count == 1


def test_delete_nauta_user_failure(mocker, git_repo_manager: GitRepoManagerClient):
    delete_user = mocker.patch.object(git_repo_manager, 'delete_user', side_effect=RuntimeError)
    delete_repo = mocker.patch.object(git_repo_manager, 'delete_repository')

    with pytest.raises(RuntimeError):
        git_repo_manager.delete_nauta_user(username='test-user')

    assert delete_user.call_count == 1
    assert delete_repo.call_count == 1
