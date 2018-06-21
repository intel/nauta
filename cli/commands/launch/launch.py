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

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.app_names import DLS4EAppNames
from util.launcher import launch_app
from util.aliascmd import AliasCmd, AliasGroup
from util.exceptions import LaunchError, ProxyClosingError

logger = initialize_logger('commands.launch')

HELP = "Command for launching web user-interface or tensorboard"
HELP_P = "Port on which service will be exposed locally."

FORWARDED_URL = 'http://localhost:{}'


@click.command(cls=AliasCmd, alias='ui')
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


@click.command(cls=AliasCmd, alias='tb')
@common_options()
@pass_state
@click.option('-n', '--no-launch', is_flag=True, help='Run command without a web browser starting, '
                                                      'only proxy tunnel is created')
def tensorboard(state: State, no_launch: bool):
    """
    Subcommand for launching tensorboard with credentials

    """
    launch_app_with_proxy(DLS4EAppNames.TENSORBOARD, no_launch, None)


@click.group(short_help=HELP, cls=AliasGroup, alias='l')
def launch():
    pass


def launch_app_with_proxy(app_name: DLS4EAppNames, no_launch: bool, port: int):
    try:
        launch_app(app_name, no_launch, port)
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
