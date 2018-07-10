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

import os
import base64
import sys
import getpass

import click

from util.config import Config
from util.logger import initialize_logger
from util.system import execute_system_command
from util.k8s.k8s_info import get_users_token, is_current_user_administrator, get_kubectl_host
from util.config import DLS4EConfigMap
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.helm import delete_user
from util.k8s.kubectl import check_users_presence
from platform_resources.users import validate_user_name, is_user_created


log = initialize_logger(__name__)

HELP = "Command used to create a new user on the platform. Can only be " \
       "run by a platform administrator."

ADD_USER_CHART_NAME = "dls4e-user"

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
  name: dls-cluster
contexts:
- context:
    cluster: dls-cluster
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

ADD_USER_ERROR_DESCRIPTION = "User has not been created. To get more information about causes " \
                             "of this problem - run command with -v option."
REMOVE_USER_ERROR_DESCRIPTION = "Partially created user has not been removed successfully - " \
                                "please remove the user manually."

DEFAULT_FILENAME = "{}.config"


@click.command(short_help=HELP, cls=AliasCmd, alias='c')
@click.argument('username', required=False)
@click.option("-l", "--list_only", is_flag=True)
@click.option("-f", "--filename")
@common_options()
@pass_state
def create(state: State, username: str, list_only: bool, filename: str):
    """
    Adds a new user with a name given as a parameter.

    :param username: name of a new user
    """
    try:
        try:
            username = username if username else getpass.getuser()
            validate_user_name(username)
        except ValueError as exe:
            log.exception("Error detected while validating user name.")
            click.echo(exe)
            sys.exit(1)

        if not is_current_user_administrator():
            click.echo("Only administrators can create new users.")
            sys.exit(1)

        if check_users_presence(username):
            click.echo("User already exists.")
            sys.exit(1)
    except Exception:
        error_msg = "Problems detected while verifying user with given user name."
        log.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)

    try:
        chart_location = os.path.join(Config().config_path, ADD_USER_CHART_NAME)

        dls4e_config_map = DLS4EConfigMap()

        tiller_location = dls4e_config_map.image_tiller
        tensorboard_service_location = dls4e_config_map.image_tensorboard_service

        add_user_command = ["helm", "install", "--wait", "--namespace", username, "--name", username,
                            chart_location, "--set", "global.dls4e=dls4enterprise", "--set",
                            f"username={username}", "--set", "TillerImage={}".format(tiller_location),
                            "--set", f"TensorboardServiceImage={tensorboard_service_location}"]

        output, err_code = execute_system_command(add_user_command)

        if err_code:
            click.echo(ADD_USER_ERROR_DESCRIPTION)
            log.error(output)
            if not delete_user(username):
                click.echo(REMOVE_USER_ERROR_DESCRIPTION)
            sys.exit(1)

        try:
            users_password = get_users_token(username)
        except Exception:
            error_msg = "The app encountered problems while gathering user's password."
            log.exception(error_msg)
            click.echo(error_msg)
            users_password = ""

    except Exception:
        log.exception("Error detected while adding of a user.")
        click.echo(ADD_USER_ERROR_DESCRIPTION)
        if not delete_user(username):
            click.echo(REMOVE_USER_ERROR_DESCRIPTION)
        sys.exit(1)

    if is_user_created(username, 90):
        click.echo(f"User {username} has been added successfully.")
    else:
        # if during 90 seconds a user hasn't been created - app displays information about it
        # but don't step processing the command - config file generated here my be useful later
        # when user has been created
        click.echo(f"User {username} is still not ready.")

    try:
        kubeconfig = generate_kubeconfig(username, username, get_kubectl_host(with_port=True),
                                         users_password, "")
    except Exception:
        error_msg = "Problems during creation of the file with user's configuration."
        log.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)

    if list_only:
        click.echo("Please use the following kubectl config to connect to this user.")
        click.echo("----------------------------------------------------------------")
        click.echo(kubeconfig)
    else:
        if not filename:
            filename = DEFAULT_FILENAME.format(username)
        try:
            with open(filename, "w") as file:
                file.write(kubeconfig)

            click.echo(f"Configuration has been saved to the {filename} file.")
        except Exception:
            error_msg = "File with configuration wasn't saved."
            log.exception(error_msg)
            click.echo(error_msg)
            click.echo("Content of the generated config file is as follows. Please copy it to a file manually.")
            click.echo(kubeconfig)
            sys.exit(1)


def generate_kubeconfig(username: str, namespace: str, address: str, token: str, cacrt: str) -> str:
    return KUBECONFIG_TEMPLATE.format(address=address,
                                      cert_data=base64.b64encode(cacrt.encode('utf-8')).decode('utf-8'),
                                      context_namespace=namespace,
                                      context_username=username,
                                      username=username,
                                      token=token)
