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

import click
import sys
from tabulate import tabulate
from typing import Tuple

import commands.common as common
import draft.cmd as cmd
from util.logger import initialize_logger
from packs.tf_training import update_configuration
from util.k8s.kubectl import start_port_forwarding
from cli_state import common_options, pass_state, State
from util.system import get_current_os, OS
from util import socat

log = initialize_logger('commands.submit')

HELP = "Command used to submitting training scripts for a single node tensorflow training."
HELP_SFL = "Name of a folder with additional files used by a script - other .py files, data etc. " \
           "If not given - its content won't be copied into an image."
HELP_T = "Name of a template used for a training. List of available templates might be obtained by" \
         " issuing dlsctl template_list command."


@click.command(help=HELP)
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=HELP_SFL)
@click.option("-t", "--template", help=HELP_T, default="tf-training")
@click.argument("script_parameters", nargs=-1)
@common_options
@pass_state
def submit(state: State, script_location: str, script_folder_location: str,
           template: str, script_parameters: Tuple[str, ...]):
    log.debug("Submit - start")
    click.echo("Submitting task.")

    # get an experiment's name
    experiment_name = common.generate_experiment_name()

    # create an enviornment
    experiment_folder, env_error_message = common.create_environment(experiment_name, script_location,
                                                                     script_folder_location)

    if env_error_message:
        click.echo("Training script hasn't been submitted. "
                   "Experiment's environment hasn't been created. Reason - {}".format(env_error_message))
        if experiment_folder:
            common.delete_environment(experiment_folder)
        sys.exit(1)

    # generate draft's data
    output, exit_code = cmd.create(working_directory=experiment_folder, pack_type=template)

    if exit_code:
        click.echo("Training script hasn't been submitted. "
                   "Draft templates haven't been generated. Reason - {}".format(output))
        common.delete_environment(experiment_folder)
        sys.exit(1)

    # reconfigure draft's templates
    exit_code = update_configuration(experiment_folder, script_location, script_folder_location, script_parameters)

    if exit_code:
        click.echo("Training script hasn't been submitted. "
                   "Configuration hasn't been updated.")
        common.delete_environment(experiment_folder)
        sys.exit(1)

    # start port forwarding
    # noinspection PyBroadException
    try:
        process, tunnel_port, container_port = start_port_forwarding('docker-registry')
    except Exception:
        log.exception("Error during creation of a proxy for a docker registry.")
        click.echo("Error during creation of a proxy for a docker registry.")
        sys.exit(1)

    # run socat if on Windows or Mac OS
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyBroadException
        try:
            socat.start(tunnel_port)
        except Exception:
            log.exception("Error during creation of a proxy for a local docker-host tunnel")
            click.echo("Error during creation of a local docker-host tunnel.")

            # TODO: move port-forwarding process management to context manager, so we can avoid that kind of flowers
            # close port forwarding
            # noinspection PyBroadException
            try:
                process.kill()
            except Exception:
                log.exception("Error during closing of a proxy for a docker registry.")
                click.echo("Docker proxy hasn't been closed properly. "
                           "Check whether it still exists, if yes - close it manually.")

            sys.exit(1)

    # run training
    output, exit_code = cmd.up(working_directory=experiment_folder)

    # close port forwarding
    # noinspection PyBroadException
    try:
        process.kill()
    except Exception:
        log.exception("Error during closing of a proxy for a docker registry.")
        click.echo("Docker proxy hasn't been closed properly. "
                   "Check whether it still exists, if yes - close it manually.")

    # terminate socat if on Windows or Mac OS
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyBroadException
        try:
            socat.stop()
        except Exception:
            log.exception("Error during closing of a proxy for a local docker-host tunnel")
            click.echo("Local Docker-host tunnel hasn't been closed properly. "
                       "Check whether it still exists, if yes - close it manually.")

    if exit_code:
        click.echo("Training script hasn't been submitted. "
                   "Job hasn't been deployed. Reason - {}".format(output))
        common.delete_environment(experiment_folder)
        sys.exit(1)

    # display information about status of a training
    click.echo(tabulate([[experiment_name, "Received"]],
                        headers=common.RESULT_HEADER,
                        tablefmt="orgtbl"))

    log.debug("Submit - stop")
