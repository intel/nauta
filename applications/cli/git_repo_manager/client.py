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
import http
import re
import string
from typing import Tuple, Optional
import random
import uuid

import requests

from Crypto.PublicKey import RSA
from kubernetes.client import V1Secret, V1ObjectMeta

from util.k8s.k8s_info import get_secret, update_secret, create_secret
from util.config import NAUTA_NAMESPACE
from util.logger import initialize_logger


ADMIN_SECRET_NAME = 'nauta-gitea-admin-secret'

logger = initialize_logger(__name__)
_encoding = 'utf-8'  # Encoding used for bytes <-> str conversions


class GitRepoManagerClient:
    def __init__(self, host: str, namespace: str = NAUTA_NAMESPACE, port: int = None):
        self.namespace = namespace
        self.base_url = f'http://{host}:{port}' if port else f'http://{host}'
        self._token = None
        self._session = None
        self.timeout = 60


    @property
    def session(self) -> requests.Session:
        if not self._session:
            self._session = requests.Session()
            self._token = self._get_admin_token()
            self._session.trust_env = False  # Ignore proxy related variables - we assume that repo manager is on localhost
            self._session.headers = {'Authorization': self._token}
        return self._session


    def get_user(self, username: str) -> Optional[requests.Response]:
        try:
            get_user_response = self.session.get(f'{self.base_url}/api/v1/users/{username}', timeout=self.timeout)
            _log_and_raise_response(get_user_response)
            return get_user_response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == http.HTTPStatus.NOT_FOUND:
                return None
            logger.exception(f'Failed to list git repo manager users')
            raise
        except Exception:
            logger.exception(f'Failed to list git repo manager users')
            raise

    def create_user(self, username: str, email: str, password: str = None) -> requests.Response:
        """
        Creates a new user in Git Repo Manager in idempotent manner.
        :param username: user's name
        :param email: user's email (doesn't need to be a real email)
        :param password: user's password, if not passed, a random password will be generated
        :return: a requests.Response object
        """
        try:
            existing_user = self.get_user(username=username)
            if existing_user:
                logger.debug(f'User {username} already exists in git repo manager.')
                return existing_user
            
            if not password:
                password = ''.join(random.choice(string.ascii_letters) for _ in range(8))

            user_data = {'email': email,
                         'username': username,
                         'password': password}
            create_user_response = self.session.post(f'{self.base_url}/api/v1/admin/users',
                                                     json=user_data, timeout=self.timeout)
            _log_and_raise_response(create_user_response)
            return create_user_response
        except Exception:
            logger.exception(f'Failed to create git repo manager user {username}')
            raise

    def delete_user(self, username: str) -> Optional[requests.Response]:
        """
        Delete user from Git Repo Manager in idempotent manner.
        :param username: user's name
        :return: a requests.Response object or None, if user was not deleted
        """
        try:
            user = self.get_user(username=username)
            if not user:
                logger.debug(f'User {username} does not exists in git repo manager.')
                return None

            delete_user_response = self.session.delete(f'{self.base_url}/api/v1/admin/users/{username}',
                                                       timeout=self.timeout)
            _log_and_raise_response(delete_user_response)
            return delete_user_response
        except Exception:
            logger.exception(f'Failed to delete git repo manager user {username}')
            raise

    def add_public_key_for_user(self, username: str, public_key: str) -> requests.Response:
        try:
            # Generate unique random name for key in order to avoid conflicts with previously added keys
            key_name = str(uuid.uuid4())

            add_key_response = self.session.post(f'{self.base_url}/api/v1/admin/users/{username}/keys',
                                                 json={'key': public_key, 'title': key_name}, timeout=self.timeout)
            _log_and_raise_response(add_key_response)
            return add_key_response
        except Exception:
            logger.exception(f'Failed to add public key {public_key} to user {username}')
            raise

    def get_repository(self, username: str, repository_name: str) -> Optional[requests.Response]:
        try:
            get_repository_name_response = self.session.get(f'{self.base_url}/api/v1'
                                                            f'/repos/{username}/{repository_name}')
            _log_and_raise_response(get_repository_name_response)
            return get_repository_name_response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == http.HTTPStatus.NOT_FOUND:
                return None
            logger.exception(f'Failed to create git repo {repository_name} for user {username}')
            raise
        except Exception:
            logger.exception(f'Failed to create git repo {repository_name} for user {username}')
            raise

    def create_repository(self, username: str, repository_name: str) -> requests.Response:
        try:
            existing_repository = self.get_repository(username=username, repository_name=repository_name)
            if existing_repository:
                logger.debug(f'Repository {repository_name} of user {username} already exists in git repo manager.')
                return existing_repository

            create_repository_response = self.session.post(f'{self.base_url}/api/v1/admin/users/{username}/repos',
                                                           json={'name': repository_name}, timeout=self.timeout)
            _log_and_raise_response(create_repository_response)
            return create_repository_response
        except Exception:
            logger.exception(f'Failed to create git repo {repository_name} for user {username}')
            raise

    def delete_repository(self, username: str, repository_name: str) -> Optional[requests.Response]:
        try:
            repository = self.get_repository(username=username, repository_name=repository_name)
            if not repository:
                logger.debug(f'Repository {repository_name} of user {username} does not exists in git repo manager.')
                return None

            delete_repository_response = self.session.delete(f'{self.base_url}/api/v1'
                                                             f'/repos/{username}/{repository_name}',
                                                             timeout=self.timeout)
            _log_and_raise_response(delete_repository_response)
            return delete_repository_response
        except Exception:
            logger.exception(f'Failed to delete git repo {repository_name} of user {username}.')
            raise

    def add_nauta_user(self, username: str, repository_name='experiments'):
        try:
            private_key, public_key = self._generate_ssh_key()
        except Exception:
            logger.exception(f'Failed to generate SSH key for user {username}.')
            raise

        try:
            # Email notifications are not enabled in git repo manager,
            # so .invalid domain is set in order to avoid potential conflicts or email leaks.
            # See https://tools.ietf.org/html/rfc6761#section-6.4
            self.create_user(username=username, email=f'{username}@nauta.invalid')
            self.add_public_key_for_user(username=username, public_key=public_key)
            self.create_repository(username=username, repository_name=repository_name)
        except Exception:
            logger.exception(f'Failed to add user {username} to git repo manager.')
            raise

        try:
            self._save_private_ssh_key_in_k8s_secret(private_key=private_key, namespace=username)
        except Exception:
            logger.exception(f'Failed to save private key of user {username} in k8s secret.')
            raise

    def delete_nauta_user(self, username: str, repository_name='experiments'):
        try:
            self.delete_repository(username=username, repository_name=repository_name)
            self.delete_user(username=username)
        except Exception:
            logger.exception(f'Failed to delete user {username} in git repo manager.')
            raise

    def _get_admin_credentials_from_secret(self, admin_secret: V1Secret) -> Tuple[str, str]:
        admin_username = bytes(admin_secret.data['name'], encoding=_encoding)
        admin_password = bytes(admin_secret.data['password'], encoding=_encoding)
        admin_username = base64.decodebytes(admin_username).decode(_encoding)
        admin_password = base64.decodebytes(admin_password).decode(_encoding)
        return admin_username, admin_password

    def _create_admin_token(self, admin_secret: V1Secret) -> str:
        admin_username, admin_password = self._get_admin_credentials_from_secret(admin_secret)
        try:
            create_token_response = requests.post(f'{self.base_url}/api/v1/users/{admin_username}/tokens',
                                                  auth=(admin_username, admin_password),
                                                  json={'Name': admin_username}, timeout=self.timeout)
            _log_and_raise_response(create_token_response)
            token = create_token_response.json()['sha1']
            return token
        except requests.exceptions.HTTPError:
            logger.exception('Failed to create git repo manager admin token.')
            raise

    def _save_admin_token(self, admin_secret: V1Secret, token: str, user_namespace: str) -> V1Secret:
        admin_secret.data['token'] = token
        return update_secret(namespace=user_namespace, secret=admin_secret)

    def _get_admin_token(self, admin_secret_name: str = ADMIN_SECRET_NAME) -> str:
        git_repo_manager_admin_secret = get_secret(namespace=self.namespace, secret_name=admin_secret_name)
        admin_token = git_repo_manager_admin_secret.data.get('token')
        if not admin_token:
            admin_token = self._create_admin_token(admin_secret=git_repo_manager_admin_secret)
            self._save_admin_token(admin_secret=git_repo_manager_admin_secret, token=admin_token,
                                   user_namespace=self.namespace)
        return f'token {admin_token}'

    def _generate_ssh_key(self, key_bits=4096) -> Tuple[str, str]:
        key = RSA.generate(key_bits)
        private_key = key.export_key().decode(_encoding)
        public_key = key.publickey().export_key(format='OpenSSH').decode(_encoding)
        return private_key, public_key

    def _save_private_ssh_key_in_k8s_secret(self, private_key: str, namespace: str):
        base64_private_key = base64.encodebytes(bytes(private_key, encoding=_encoding)).decode(_encoding)
        private_key_secret = V1Secret(data={'private_key': base64_private_key},
                                      metadata=V1ObjectMeta(name='git-secret'))
        create_secret(namespace=namespace, secret_body=private_key_secret)


def _log_and_raise_response(response: requests.Response):
    logger.debug(f'Request: {response.request.method} {response.url}')
    # Filter passwords from logs
    filtered_request_body = re.sub(r'"password": "\w+"', 'password: "*****"',
                                   response.request.body.decode(_encoding)) if response.request.body else ''
    logger.debug(f'Request body: {filtered_request_body}')
    logger.debug(f'Request response: {response.status_code} {response.content}')
    response.raise_for_status()
