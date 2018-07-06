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

from http import HTTPStatus
import json
import sys
from time import sleep
from typing import Optional

import click
import requests

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.launcher import launch_app
from util.aliascmd import AliasCmd, AliasGroup
from util.exceptions import LaunchError, ProxyClosingError
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.app_names import DLS4EAppNames
from util.k8s.k8s_info import get_kubectl_current_context_namespace

logger = initialize_logger('commands.launch')

HELP = "Command for launching web user-interface or tensorboard"
HELP_P = "Port on which service will be exposed locally."

FORWARDED_URL = 'http://localhost:{}'


# noinspection PyUnusedLocal
@click.command(cls=AliasCmd, alias='ui', short_help='Subcommand for launching webUI with credentials')
@common_options()
@pass_state
@click.option('--no-launch', is_flag=True, help='Run command without a web browser starting, '
                                                'only proxy tunnel is created')
@click.option('-p', '--port', type=click.IntRange(1024, 65535), help=HELP_P)
def webui(state: State, no_launch: bool, port: int):
    """
    Subcommand for launching webUI with credentials
    """
    launch_app_with_proxy(DLS4EAppNames.INGRESS, no_launch, port)


# noinspection PyUnusedLocal
@click.command(cls=AliasCmd, alias='tb', short_help='Subcommand for launching tensorboard with credentials')
@common_options()
@pass_state
@click.option('-n', '--no-launch', is_flag=True, help='Run command without a web browser starting, '
                                                      'only proxy tunnel is created')
@click.option('-p', '--port', type=click.IntRange(1024, 65535), help=HELP_P)
@click.argument("experiment_name", type=str, required=True)
def tensorboard(state: State, no_launch: bool, port: Optional[int], experiment_name: str):
    """
    Subcommand for launching tensorboard with credentials

    """
    current_namespace = get_kubectl_current_context_namespace()

    with K8sProxy(dls4e_app_name=DLS4EAppNames.TENSORBOARD_SERVICE, app_name='tensorboard-service',
                  namespace=current_namespace, port=port) as proxy:
        # noinspection PyBroadException
        try:
            response = requests.post('http://127.0.0.1:' + str(proxy.tunnel_port) + "/create/" + experiment_name)
        except Exception:
            logger.exception('failed sending request to tensorboard-service!')
            click.echo('Error during requesting new tensorboard instance.')
            sys.exit(1)

        expected_status_code_from_tensorboard_service = (HTTPStatus.OK, HTTPStatus.CONFLICT)
        if response.status_code not in expected_status_code_from_tensorboard_service:
            logger.error(f'bad status code returned from tensorboard-service - got: {response.status_code} , '
                         f'expected one of: {expected_status_code_from_tensorboard_service}')
            click.echo('Error during requesting new tensorboard instance.')
            sys.exit(1)

    response_body = json.loads(response.content.decode('utf-8'))
    tensorboard_id = response_body['id']

    if response.status_code == HTTPStatus.OK:
        # TODO: remove sleep after implementing Tensorboard instance's status polling from tensorboard-service
        sleep(10)

    launch_app_with_proxy(k8s_app_name=DLS4EAppNames.TENSORBOARD, no_launch=no_launch, namespace=current_namespace,
                          app_name="tensorboard-"+tensorboard_id)


@click.group(short_help=HELP, cls=AliasGroup, alias='l')
def launch():
    pass


def launch_app_with_proxy(k8s_app_name: DLS4EAppNames, no_launch: bool, port: int = None, namespace: str = None,
                          app_name: str = None):
    # noinspection PyBroadException
    try:
        launch_app(k8s_app_name=k8s_app_name, no_launch=no_launch, port=port, namespace=namespace, app_name=app_name)
    except LaunchError as exe:
        logger.exception(exe.message)
        click.echo(exe.message)
        sys.exit(1)
    except ProxyClosingError:
        click.echo('K8s proxy hasn\'t been closed properly. '
                   'Check whether it still exists, if yes - close it manually.')
    except Exception:
        err_message = "Other exception during setting up a K8s proxy."
        logger.exception(err_message)
        click.echo(err_message)
        sys.exit(1)


launch.add_command(webui)
launch.add_command(tensorboard)
