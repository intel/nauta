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
from time import sleep
from typing import Optional, List
from http import HTTPStatus

import click

from cli_state import common_options, pass_state, State
from tensorboard.client import TensorboardServiceClient, TensorboardStatus, build_tensorboard_run_list
from util.aliascmd import AliasCmd, AliasGroup
from util.app_names import DLS4EAppNames
from util.exceptions import LaunchError, ProxyClosingError
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.launcher import launch_app
from util.logger import initialize_logger


logger = initialize_logger('commands.launch')

HELP = "Command for launching web user-interface or tensorboard."
HELP_P = "Port on which service will be exposed locally."

FORWARDED_URL = 'http://localhost:{}'


# noinspection PyUnusedLocal
@click.command(cls=AliasCmd, alias='ui', short_help='Subcommand for launching webUI with credentials')
@common_options()
@pass_state
@click.option('-n', '--no-launch', is_flag=True, help='Run command without a web browser starting, '
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
@click.option('-tscp', '--tensorboard-service-client-port', type=click.IntRange(1024, 65535),
              help="Local port on which tensorboard service client will be started.")
@click.option('-p', '--port', type=click.IntRange(1024, 65535), help=HELP_P)
@click.argument("experiment_name", type=str, required=True, nargs=-1)
def tensorboard(state: State, no_launch: bool, tensorboard_service_client_port: Optional[int], port: Optional[int],
                experiment_name: List[str]):
    """
    Subcommand for launching tensorboard with credentials

    """
    current_namespace = get_kubectl_current_context_namespace()

    with K8sProxy(dls4e_app_name=DLS4EAppNames.TENSORBOARD_SERVICE, app_name='tensorboard-service',
                  namespace=current_namespace, port=tensorboard_service_client_port) as proxy:

        tensorboard_service_client = TensorboardServiceClient(address=f'http://127.0.0.1:{proxy.tunnel_port}')

        requested_runs = build_tensorboard_run_list(exp_list=experiment_name, current_namespace=current_namespace)

        # noinspection PyBroadException
        try:
            tb = tensorboard_service_client.create_tensorboard(requested_runs)
            if tb.invalid_runs:
                list_of_invalid_runs = ', '.join([f'{item.get("owner")}/{item.get("name")}'
                                                  for item in tb.invalid_runs])
                click.echo('There is no data for the following experiments : {}'.format(list_of_invalid_runs))
                click.echo('Tensorboard will present information from the rest of given experiments.')
        except Exception as exe:
            err_message = 'failed to create tensorboard!'
            if hasattr(exe, 'error_code') and exe.error_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                err_message = str(exe)
            click.echo(err_message)
            logger.exception(err_message)
            sys.exit(1)

        click.echo('Please wait for Tensorboard to run...')
        for i in range(10):
            tb = tensorboard_service_client.get_tensorboard(tb.id)
            if tb.status == TensorboardStatus.RUNNING:
                launch_app_with_proxy(k8s_app_name=DLS4EAppNames.TENSORBOARD, no_launch=no_launch,
                                      namespace=current_namespace, port=port,
                                      app_name=f"tensorboard-{tb.id}")
                return
            logger.warning(f'Tensorboard instance: {tb.id} still in {tb.status.value} status, waiting for RUNNING...')
            sleep(5)

        click.echo('Tensorboard failed to run - timeout.')
        sys.exit(2)


@click.group(short_help=HELP, help=HELP, cls=AliasGroup, alias='l',
             subcommand_metavar="COMMAND [OPTIONS] [ARGS]...")
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
        err_message = "Other exception during launching web application."
        logger.exception(err_message)
        click.echo(err_message)
        sys.exit(1)


launch.add_command(webui)
launch.add_command(tensorboard)
