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

import webbrowser
import sys

import click

from util.system import get_current_os, OS
from util import socat
from util.k8s.kubectl import start_port_forwarding
from util.network import wait_for_connection
from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.app_names import DLS4EAppNames

logger = initialize_logger('commands.launch')

HELP = "Command for launching web user-interface or tensorboard"

FORWARDED_URL = 'http://localhost:{}'


def launch_app(k8s_app_name: DLS4EAppNames, no_launch: bool):
    try:
        process, tunneled_port, container_port = start_port_forwarding(k8s_app_name)
    except Exception:
        logger.exception('Error during creation of a proxy for a {}'.format(k8s_app_name))
        click.echo('Error during creation of a proxy for a {}'.format(k8s_app_name))
        sys.exit(1)

    url = FORWARDED_URL.format(container_port)

    # run socat if on Windows or Mac OS
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyBroadException
        try:
            socat.start(container_port)
        except Exception:
            logger.exception("Error during creation of a proxy for a local docker-host tunnel")
            click.echo("Error during creation of a local docker-host tunnel.")

            try:
                process.kill()
            except Exception:
                logger.exception("Error during closing of a proxy for a {}.".format(k8s_app_name))
                click.echo("Docker proxy hasn't been closed properly. "
                           "Check whether it still exists, if yes - close it manually.")

            sys.exit(1)

    if not no_launch:
        click.echo('Browser will start in few seconds. Please wait... ')
        wait_for_connection(url)
        webbrowser.open_new(url)
    else:
        click.echo('Go to {}'.format(url))

    input('Proxy connection created.\nPress ENTER key to close a port forwarding process...')
    # close port forwarding
    # noinspection PyBroadException
    try:
        process.kill()
    except Exception:
        click.echo('Docker proxy hasn\'t been closed properly. '
                   'Check whether it still exists, if yes - close it manually.')

    # terminate socat if on Windows or Mac OS
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyBroadException
        try:
            socat.stop()
        except Exception:
            logger.exception("Error during closing of a proxy for a local docker-host tunnel")
            click.echo("Local Docker-host tunnel hasn't been closed properly. "
                       "Check whether it still exists, if yes - close it manually.")


@click.command()
@common_options
@pass_state
@click.option('--no-launch', is_flag=True, help='Run command without a web browser starting, '
                                                'only proxy tunnel is created')
def webui(state: State, no_launch: bool):
    """
    Subcommand for launching webUI with credentials
    """
    launch_app(DLS4EAppNames.WEB_GUI, no_launch)


@click.command()
@common_options
@pass_state
@click.option('--no-launch', is_flag=True, help='Run command without a web browser starting, '
                                                'only proxy tunnel is created')
def tensorboard(state: State, no_launch: bool):
    """
    Subcommand for launching tensorboard with credentials

    """
    launch_app(DLS4EAppNames.TENSORBOARD, no_launch)


@click.group(help=HELP)
def launch():
    pass


launch.add_command(webui)
launch.add_command(tensorboard)
