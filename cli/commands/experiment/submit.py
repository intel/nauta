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
from typing import Tuple, List
import os

import click
from tabulate import tabulate

from commands.experiment.common import RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE
from cli_state import common_options, pass_state, State
from util.logger import initialize_logger
from commands.experiment.common import submit_experiment
from util.aliascmd import AliasCmd
from util.exceptions import SubmitExperimentError, K8sProxyCloseError
from commands.experiment.common import validate_experiment_name
from platform_resources.run_model import RunStatus

log = initialize_logger('commands.submit')

DEFAULT_SCRIPT_NAME = "experiment.py"

HELP = "Command used to submitting training scripts."
HELP_N = "Name for this experiment."
HELP_SFL = "Name of a folder with additional files used by a script, e.g., other .py files, data etc. " \
           "If not given - its content won't be copied into an image."
HELP_T = "Name of a template used to create a deployment. By default, this is a single-node tensorflow training." \
         " Template is chosen. List of available templates might be obtained by" \
         " Issuing dlsctl experiment template_list command."
HELP_P = " Additional pack param in format: 'key value' or 'key.subkey.subkey2 value' " \
         "For lists use: 'key \"['val1', 'val2']\"' For maps use: 'key \"{'a': 'b'}\"' "
HELP_PR = "Values (set or range) of a single parameter."
HELP_PS = "Set of values of one or several parameters."


def validate_script_location(script_location: str):
    if not (os.path.isfile(script_location) or os.path.isdir(script_location)):
        click.echo(f'Cannot find: {script_location}. Make sure that provided path is correct.')
        sys.exit(2)


def get_default_script_location(script_directory: str) -> str:
    default_script_location = os.path.join(script_directory, DEFAULT_SCRIPT_NAME)
    if not os.path.isfile(default_script_location):
        click.echo(f'Cannot find script: {DEFAULT_SCRIPT_NAME} in directory: {script_directory}. '
                   f'If path to directory was passed as submit command argument, then {DEFAULT_SCRIPT_NAME} file '
                   f'has to exist in that directory.')
        sys.exit(2)
    else:
        return default_script_location


def validate_script_folder_location(script_folder_location: str):
    if not os.path.isdir(script_folder_location):
        click.echo(f'Cannot find: {script_folder_location}.'
                   f' script_folder_location must be a path to existing directory.')
        sys.exit(2)


@click.command(short_help=HELP, help=HELP, cls=AliasCmd, alias='s')
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=HELP_SFL)
@click.option("-t", "--template", help=HELP_T, default="tf-training-tfjob")
@click.option("-n", "--name", help=HELP_N, callback=validate_experiment_name)
@click.option("-p", "--pack_param", type=(str, str), multiple=True, help=HELP_P)
@click.option("-pr", "--parameter_range", nargs=2, multiple=True, help=HELP_PR)
@click.option("-ps", "--parameter_set", multiple=True, help=HELP_PS)
@click.argument("script_parameters", nargs=-1)
@common_options()
@pass_state
def submit(state: State, script_location: str, script_folder_location: str, template: str, name: str,
           pack_param: List[Tuple[str, str]], parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
           script_parameters: Tuple[str, ...]):
    log.debug("Submit - start")
    validate_script_location(script_location)

    if os.path.isdir(script_location):
        script_location = get_default_script_location(script_directory=script_location)

    if script_folder_location:
        validate_script_folder_location(script_folder_location)

    click.echo("Submitting experiments.")

    # noinspection PyBroadException
    try:
        runs_list, _ = submit_experiment(script_location=script_location,
                                         script_folder_location=script_folder_location,
                                         template=template, name=name, pack_params=pack_param,
                                         parameter_range=parameter_range, parameter_set=parameter_set,
                                         script_parameters=script_parameters)
    except K8sProxyCloseError as exe:
        click.echo(exe.message)
    except SubmitExperimentError as exe:
        click.echo(f"Problems during submitting experiment:{exe.message}")
        sys.exit(1)
    except Exception:
        click.echo("Other problems during submitting experiment.")
        sys.exit(1)

    # display information about status of a training
    click.echo(tabulate({RUN_NAME: [run.name for run in runs_list],
                         RUN_PARAMETERS: [run.formatted_parameters() for run in runs_list],
                         RUN_STATUS: [run.formatted_status() for run in runs_list],
                         RUN_MESSAGE: [run.error_message for run in runs_list]},
                        headers=[RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE], tablefmt="orgtbl"))

    # if there is at least one FAILED experiment - application has to return exit code != 0
    if any(run.status == RunStatus.FAILED for run in runs_list):
        log.error("There are failed runs.")
        sys.exit(1)
