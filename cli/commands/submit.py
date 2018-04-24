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
from util.kubectl import start_port_forwarding

log = initialize_logger('commands.submit')

HELP = "Command used to submitting training scripts for a single node tensorflow training."
HELP_SFL = "Name of a folder with additional files used by a script - other .py files, data etc. " \
           "If not given - its content won't be copied into an image."


@click.command(help=HELP)
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=HELP_SFL)
@click.argument("script_parameters", nargs=-1)
def submit(script_location: str, script_folder_location: str, script_parameters: Tuple[str, ...]):
    log.debug("Submit - start")
    click.echo("Submitting task.")

    # get an experiment's name
    experiment_name = common.generate_experiment_name()

    # create an enviornment
    experiment_folder, env_error_message = common.create_environment(experiment_name, script_location, script_folder_location)

    if env_error_message:
        click.echo("Training script hasn't been submitted. "
                   "Experiment's environment hasn't been created. Reason - {}".format(env_error_message))
        if experiment_folder:
            common.delete_environment(experiment_folder)
        sys.exit(1)

    # generate draft's data
    output, exit_code = cmd.create(working_directory=experiment_folder, pack_type="tf-training")

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
    try:
        process = start_port_forwarding()
    except Exception as exe:
        log.exception("Error during creation of a proxy for a docker registry.")
        click.echo("Error during creation of a proxy for a docker registry.")
        sys.exit(1)

    # run training
    output, exit_code = cmd.up(working_directory=experiment_folder)

    # close port forwarding
    try:
        process.kill()
    except Exception as exet:
        log.exception("Error during closing of a proxy for a docker registry.")
        click.echo("Docker proxy hasn't been closed properly. "
                   "Check whether it still exists, if yes - close it manually.")

    if exit_code:
        click.echo("Training script hasn't been submitted. "
                   "Job hasn't been deployed. Reason - {}".format(output))
        common.delete_environment(experiment_folder)
        sys.exit(1)

    # display information about status of a training
    click.echo(tabulate([[experiment_name, "Received"]],
                        headers=common.RESULT_HEADER,
                        tablefmt="grid"))

    log.debug("Submit - stop")
