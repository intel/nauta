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
import hashlib
import os

from retry import retry

from util.app_names import NAUTAAppNames
from util.config import Config
from util.k8s.k8s_info import get_secret, get_kubectl_host
from util.k8s.k8s_proxy_context_manager import TcpK8sProxy
from util.logger import initialize_logger
from util.system import ExternalCliClient

logger = initialize_logger(__name__)
_encoding = 'utf-8'  # Encoding used for bytes <-> str conversions


def compute_hash_of_k8s_env_address():
    nauta_hostname = get_kubectl_host()
    nauta_hostname_hash = hashlib.md5(nauta_hostname.encode('utf-8')).hexdigest()  # nosec
    return nauta_hostname_hash


def get_git_private_key_path(config_dir: str, username: str) -> str:
    k8s_secret_name = 'git-secret'
    key_path = os.path.join(config_dir, f'.ssh-key-{username}-{compute_hash_of_k8s_env_address()}')
    # If private key is already saved in config, return it
    if not os.path.isfile(key_path):
        # If not, get key from k8s secret, save it with proper permissions
        private_key_secret = get_secret(namespace=username, secret_name=k8s_secret_name)
        private_key = bytes(private_key_secret.data['private_key'], encoding=_encoding)
        private_key = base64.decodebytes(private_key).decode(_encoding)
        with open(key_path, mode='w', encoding=_encoding) as private_key_file:
            private_key_file.write(private_key)
        os.chmod(key_path, 0o600)

    return key_path


def create_gitignore_file_for_experiments(git_workdir):
    """
    Creates a gitignore file that excludes helm charts from git work tree.
    :param git_workdir: path to experiments workdir
    """
    with open(f'{git_workdir}/.gitignore', mode='w', encoding='utf-8') as gitignore_file:
        gitignore_file.write('charts/*')


@retry(tries=5, delay=1)
def upload_experiment_to_git_repo_manager(username: str, experiment_name: str, experiments_workdir: str, run_name: str):
    git_repo_dir = f'.nauta-git-{username}-{compute_hash_of_k8s_env_address()}'
    git_work_dir = os.path.join(experiments_workdir, run_name)

    try:
        create_gitignore_file_for_experiments(git_work_dir)
        private_key_path = get_git_private_key_path(username=username, config_dir=Config().config_path)
        git_env = {'GIT_SSH_COMMAND': f'ssh -o StrictHostKeyChecking=no -i "{private_key_path}"',
                   'GIT_DIR': os.path.join(experiments_workdir, git_repo_dir),
                   'GIT_WORK_TREE': git_work_dir,
                   'GIT_TERMINAL_PROMPT': '0',
                   'SSH_AUTH_SOCK': '',  # Unset SSH_AUTH_SOCK to prevent issues when multiple users are using same nctl
                   }
        env = {**os.environ, **git_env}  # Add git_env defined above to currently set environment variables
        if 'LD_LIBRARY_PATH' in env:
            # do not copy LD_LIBRARY_PATH to git exec env - it points to libraries packed by PyInstaller
            # and they can be incompatible with system's git (e.g. libssl)
            del env['LD_LIBRARY_PATH']
        logger.debug(f'Git client env: {env}')
        git = ExternalCliClient(executable='git', env=env, cwd=experiments_workdir, timeout=60)
        # ls-remote command must be created manually due to hyphen
        git.ls_remote = git._make_command(name='ls-remote')  #type: ignore
        with TcpK8sProxy(NAUTAAppNames.GIT_REPO_MANAGER_SSH) as proxy:
            if not os.path.isdir(f'{experiments_workdir}/{git_repo_dir}'):
                git.clone(f'ssh://git@localhost:{proxy.tunnel_port}/{username}/experiments.git', git_repo_dir,
                          bare=True)
            git.remote('set-url', 'origin', f'ssh://git@localhost:{proxy.tunnel_port}/{username}/experiments.git')
            _initialize_git_client_config(git, username=username)
            git.add('.')
            git.commit(message=f'experiment: {experiment_name}', allow_empty=True)
            remote_branches, _, _ = git.ls_remote()
            local_branches, _, _ = git.branch()
            if 'master' in local_branches:
                git.checkout('master')
            else:
                git.checkout('-b', 'master')
            if 'master' in remote_branches:
                try:
                    git.pull('--rebase', '--strategy=recursive', '--strategy-option=theirs')
                except Exception:
                    git.rebase('--abort')
                    raise
            git.push('--set-upstream', 'origin', 'master')
            git.tag(experiment_name)
            git.push('--tags')
    except Exception:
        logger.exception(f'Failed to upload experiment {experiment_name} to git repo manager.')
        try:
            git_env = {'GIT_DIR': os.path.join(experiments_workdir, git_repo_dir),
                       'GIT_WORK_TREE': git_work_dir,
                       'GIT_TERMINAL_PROMPT': '0',
                       'SSH_AUTH_SOCK': '',
                       }
            env = {**os.environ, **git_env}  # Add git_env defined above to currently set environment variables
            git = ExternalCliClient(executable='git', env=env, cwd=experiments_workdir, timeout=60)
            git.reset('--hard', 'master', _cwd=experiments_workdir)
        except Exception:
            logger.exception(f'Failed to rollback {experiment_name} experiment upload to git repo manager.')
        raise


def delete_exp_tag_from_git_repo_manager(username: str, experiment_name: str, experiments_workdir: str):
    git_repo_dir = f'.nauta-git-{username}-{compute_hash_of_k8s_env_address()}'

    try:
        private_key_path = get_git_private_key_path(username=username, config_dir=Config().config_path)
        git_env = {'GIT_SSH_COMMAND': f'ssh -o StrictHostKeyChecking=no -i "{private_key_path}"',
                   'GIT_DIR': os.path.join(experiments_workdir, git_repo_dir),
                   'GIT_TERMINAL_PROMPT': '0',
                   'SSH_AUTH_SOCK': '',  # Unset SSH_AUTH_SOCK to prevent issues when multiple users are using same nctl
                   }
        env = {**os.environ, **git_env}  # Add git_env defined above to currently set environment variables
        if 'LD_LIBRARY_PATH' in env:
            # do not copy LD_LIBRARY_PATH to git exec env - it points to libraries packed by PyInstaller
            # and they can be incompatible with system's git (e.g. libssl)
            del env['LD_LIBRARY_PATH']
        logger.debug(f'Git client env: {env}')
        git = ExternalCliClient(executable='git', env=env, cwd=experiments_workdir, timeout=60)
        with TcpK8sProxy(NAUTAAppNames.GIT_REPO_MANAGER_SSH) as proxy:
            if not os.path.isdir(f'{experiments_workdir}/{git_repo_dir}'):
                if not os.path.isdir(experiments_workdir):
                    os.makedirs(experiments_workdir, 0o755)
                git.clone(f'ssh://git@localhost:{proxy.tunnel_port}/{username}/experiments.git', git_repo_dir,
                          bare=True)
            git.remote('set-url', 'origin', f'ssh://git@localhost:{proxy.tunnel_port}/{username}/experiments.git')
            _initialize_git_client_config(git, username=username)
            git.fetch()
            output, _, _ = git.tag('-l', experiment_name)
            if output:
                git.tag('-d', experiment_name)
                git.push('origin', f':refs/tags/{experiment_name}')
    except Exception:
        logger.exception(f'Failed to delete tag {experiment_name} from git repo manager.')
        raise


def _initialize_git_client_config(git: ExternalCliClient, username: str):
    git.config('--local', 'user.email', f'{username}@nauta.invalid')
    git.config('--local', 'user.name', f'{username}')
    git.config('--local', 'credential.helper', 'store')  # Use store helper for repos cloned by nctl
