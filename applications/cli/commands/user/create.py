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

import sys
import os
import base64
from sys import exit

import click

from util.config import Config
from util.logger import initialize_logger
from util.spinner import spinner
from util.system import execute_system_command, handle_error
from util.k8s.k8s_info import get_users_token, get_kubectl_host
from util.config import NAUTAConfigMap
from util.cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.helm import delete_user
from util.k8s.kubectl import check_users_presence, UserState
from platform_resources.users import validate_user_name, is_user_created
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
    # certificate-authority-data: {cert_data}
    # BUG/TASK: CAN-261
    insecure-skip-tls-verify: true
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
            sys.exit(1)

        try:
            users_password = get_users_token(username)
        except Exception:
            handle_error(logger, Texts.PASSWORD_GATHER_ERROR_MSG, Texts.PASSWORD_GATHER_ERROR_MSG,
                         add_verbosity_msg=state.verbosity == 0)
            users_password = ""

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
        # but don't step processing the command - config file generated here my be useful later
        # when user has been created
        click.echo(Texts.USER_NOT_READY_ERROR_MSG.format(username=username))

    try:
        kubeconfig = generate_kubeconfig(username, username, get_kubectl_host(),
                                         users_password, "")
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
