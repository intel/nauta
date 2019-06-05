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

import sys
import os
import base64
from sys import exit

import click

from git_repo_manager.client import GitRepoManagerClient
from util.app_names import NAUTAAppNames
from util.config import Config
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.logger import initialize_logger
from util.spinner import spinner
from util.system import execute_system_command, handle_error
from util.k8s.k8s_info import get_users_token, get_kubectl_host, get_certificate
from util.config import NAUTAConfigMap
from util.cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.helm import delete_user
from util.k8s.kubectl import UserState
from platform_resources.user_utils import validate_user_name, is_user_created, check_users_presence
from cli_text_consts import UserCreateCmdTexts as Texts

logger = initialize_logger(__name__)

ADD_USER_CHART_NAME = "nauta-user"

KUBECONFIG_TEMPLATE = '''
current-context: user-context
apiVersion: v1
clusters:
- cluster:
    api-version: v1
    server: https://{address}
    certificate-authority-data: {cert_data}
  name: nauta-cluster
contexts:
- context:
    cluster: nauta-cluster
    namespace: "{context_namespace}"
    user: "{context_username}"
  name: user-context
kind: Config
preferences:
  colors: true
users:
- name: "{username}"
  user:
    token: {token}
'''

DEFAULT_FILENAME = "{}.config"


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='c', options_metavar='[options]')
@click.argument('username', required=True)
@click.option("-l", "--list-only", is_flag=True, help=Texts.HELP_L)
@click.option("-f", "--filename", help=Texts.HELP_F)
@common_options(admin_command=True)
@pass_state
def create(state: State, username: str, list_only: bool, filename: str):
    """
    Adds a new user with a name given as a parameter.

    :param username: name of a new user
    """

    if list_only and filename:
        handle_error(user_msg=Texts.F_L_OPTIONS_EXCLUSION_ERROR_MSG)
        exit(1)

    try:
        try:
            validate_user_name(username)
        except ValueError as exe:
            handle_error(logger, Texts.NAME_VALIDATION_ERROR_MSG.format(username=username), str(exe),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)

        user_state = check_users_presence(username)

        if user_state == UserState.ACTIVE:
            handle_error(logger, Texts.USER_ALREADY_EXISTS_ERROR_MSG.format(username=username),
                         Texts.USER_ALREADY_EXISTS_ERROR_MSG.format(username=username))
            exit(1)

        if user_state == UserState.TERMINATING:
            handle_error(logger, Texts.USER_BEING_REMOVED_ERROR_MSG.format(username=username),
                         Texts.USER_BEING_REMOVED_ERROR_MSG.format(username=username))
            exit(1)

    except Exception:
        handle_error(logger, Texts.USER_VERIFICATION_ERROR_MSG.format(username=username),
                     Texts.USER_VERIFICATION_ERROR_MSG.format(username=username),
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        with spinner(text=Texts.CREATING_USER_PROGRESS_MSG.format(username=username)):
            chart_location = os.path.join(Config().config_path, ADD_USER_CHART_NAME)

            nauta_config_map = NAUTAConfigMap()

            tiller_location = nauta_config_map.image_tiller
            tensorboard_service_location = nauta_config_map.image_tensorboard_service

            add_user_command = ["helm", "install", "--wait", "--namespace", username, "--name", username,
                                chart_location, "--set", "global.nauta=nauta", "--set",
                                f"username={username}", "--set", "TillerImage={}".format(tiller_location),
                                "--set", f"TensorboardServiceImage={tensorboard_service_location}"]
            env = os.environ.copy()
            env['PATH'] = Config().config_path + os.pathsep + env['PATH']
            _, err_code, log_output = execute_system_command(' '.join(add_user_command), env=env, shell=True)

            if err_code:
                handle_error(logger, log_output, Texts.USER_ADD_ERROR_MSG, add_verbosity_msg=state.verbosity == 0)

                if not delete_user(username):
                    handle_error(user_msg=Texts.REMOVE_USER_ERROR_MSG.format(username=username))
                raise RuntimeError(Texts.USER_ADD_ERROR_MSG)

            try:
                users_password = get_users_token(username)
            except Exception:
                handle_error(logger, Texts.PASSWORD_GATHER_ERROR_MSG, Texts.PASSWORD_GATHER_ERROR_MSG,
                             add_verbosity_msg=state.verbosity == 0)
                users_password = ""

            try:
                cert = get_certificate(username)
            except Exception:
                handle_error(logger, Texts.CERT_GATHER_ERROR_MSG, Texts.CERT_GATHER_ERROR_MSG,
                             add_verbosity_msg=state.verbosity == 0)
                cert = ""

            try:
                with K8sProxy(NAUTAAppNames.GIT_REPO_MANAGER, number_of_retries_wait_for_readiness=60) as proxy:
                    grm_client = GitRepoManagerClient(host='127.0.0.1', port=proxy.tunnel_port)
                    grm_client.add_nauta_user(username=username)
            except Exception:
                handle_error(logger, Texts.GIT_REPO_MANAGER_ERROR_MSG, Texts.GIT_REPO_MANAGER_ERROR_MSG,
                             add_verbosity_msg=state.verbosity == 0)
                raise

    except Exception:
        handle_error(logger, Texts.USER_ADD_ERROR_MSG.format(username=username),
                     Texts.USER_ADD_ERROR_MSG.format(username=username),
                     add_verbosity_msg=state.verbosity == 0)
        if not delete_user(username):
            handle_error(user_msg=Texts.REMOVE_USER_ERROR_MSG.format(username=username))
        sys.exit(1)

    if is_user_created(username, 90):
        click.echo(Texts.USER_CREATION_SUCCESS_MSG.format(username=username))
    else:
        # if during 90 seconds a user hasn't been created - app displays information about it
        # but doesn't stop processing the command - config file generated here may be useful later
        # when user has been created
        click.echo(Texts.USER_NOT_READY_ERROR_MSG.format(username=username))

    try:
        kubeconfig = generate_kubeconfig(username, username, get_kubectl_host(),
                                         users_password, cert)
    except Exception:
        handle_error(logger, Texts.CONFIG_CREATION_ERROR_MSG, Texts.CONFIG_CREATION_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    if list_only:
        click.echo(Texts.LIST_ONLY_HEADER)
        click.echo(kubeconfig)
    else:
        if not filename:
            filename = DEFAULT_FILENAME.format(username)
        try:
            with open(filename, "w") as file:
                file.write(kubeconfig)

            click.echo(Texts.CONFIG_SAVE_SUCCESS_MSG.format(filename=filename))
        except Exception:
            handle_error(logger, Texts.CONFIG_SAVE_FAIL_MSG, Texts.CONFIG_SAVE_FAIL_MSG,
                         add_verbosity_msg=state.verbosity == 0)
            click.echo(Texts.CONFIG_SAVE_FAIL_INSTRUCTIONS_MSG)
            click.echo(kubeconfig)
            sys.exit(1)


def generate_kubeconfig(username: str, namespace: str, address: str, token: str, cacrt: str) -> str:
    return KUBECONFIG_TEMPLATE.format(address=address,
                                      cert_data=base64.b64encode(cacrt.encode('utf-8')).decode('utf-8'),
                                      context_namespace=namespace,
                                      context_username=username,
                                      username=username,
                                      token=token)
