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

import click

from util.config import Config, Fields
from util.logger import initialize_logger
from util.system import execute_system_command
from util.k8s.k8s_info import get_users_token
from util.config import DLS4EConfigMap, DLS4EConfigMapFields
from cli_state import common_options, pass_state, State
from util.k8s.kubectl import check_users_presence
from util.helm import delete_user

log = initialize_logger(__name__)

HELP = "Command used to create a new user on the platform. Can be only " \
       "run by a platform administrator."

ADD_USER_CHART_NAME = "dls4e-user"

KUBECONFIG_TEMPLATE = '''
current-context: user-context
apiVersion: v1
clusters:
- cluster:
    api-version: v1
    server: https://{address}:8443
    # certificate-authority-data: {cert_data}
    # BUG/TASK: CAN-261
    insecure-skip-tls-verify: true
  name: dls-cluster
contexts:
- context:
    cluster: dls-cluster
    namespace: {context_namespace}
    user: {context_username}
  name: user-context
kind: Config
preferences:
  colors: true
users:
- name: {username}
  user:
    token: {token}
'''


@click.argument('username')
@click.command(help=HELP)
@common_options
@pass_state
def create(state: State, username: str):
    """
    Adds a new user with a name given as a parameter.

    :param username: name of a new user
    """
    try:
        if check_users_presence(username):
            click.echo("User already exists.")
            sys.exit(1)
    except Exception:
        click.echo("Problems during verifying users presence.")
        sys.exit(1)

    try:
        chart_location = os.path.join(Config.get(Fields.CONFIG_PATH), ADD_USER_CHART_NAME)

        tiller_location = DLS4EConfigMap.get(DLS4EConfigMapFields.IMAGE_TILLER)

        add_user_command = ["helm", "install", "--namespace", username, "--name", username, chart_location,
                            "--set", "global.dls4e=dls4enterprise", "--set", f"username={username}",
                            "--set", "TillerImage={}".format(tiller_location)]

        output, err_code = execute_system_command(add_user_command)

        if err_code:
            click.echo("User hasn't been created. To get more information about causes "
                       "of a problem - run command with -v option.")
            log.error(output)
            sys.exit(1)

        try:
            users_password = get_users_token(username)
        except Exception:
            click.echo("The app encountered problems when gathering user's password.")
            users_password = ""

    except Exception:
        log.exception("Error during adding of a user.")
        click.echo("User hasn't been created. To get more information about causes "
                   "of a problem - run command with -v option.")
        if not delete_user(username):
            click.echo("User hasn't been removed - please remove the user manually.")
        sys.exit(1)

    click.echo(f"User {username} has been added successfully.")
    click.echo("Please use the following kubectl config to connect to this user.")
    click.echo("----------------------------------------------------------------")
    click.echo(generate_kubeconfig(username, username, DLS4EConfigMap.get(DLS4EConfigMapFields.EXTERNAL_IP),
                                   users_password, ""))


def generate_kubeconfig(username: str, namespace: str, address: str, token: str, cacrt: str) -> str:
    return KUBECONFIG_TEMPLATE.format(address=address,
                                      cert_data=base64.b64encode(cacrt.encode('utf-8')).decode('utf-8'),
                                      context_namespace=namespace,
                                      context_username=username,
                                      username=username,
                                      token=token)
