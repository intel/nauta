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

from sys import exit
from typing import Tuple, List
import os

import click
from tabulate import tabulate

from commands.experiment.common import RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE, RunKinds, \
    validate_env_paramater
from cli_state import common_options, pass_state, State
from util.logger import initialize_logger
from commands.experiment.common import submit_experiment
from util.aliascmd import AliasCmd
from util.exceptions import SubmitExperimentError, K8sProxyCloseError
from commands.experiment.common import validate_experiment_name, validate_pack_params_names
from util.k8s.k8s_info import is_current_user_administrator
from platform_resources.run_model import RunStatus
from util.system import handle_error
from cli_text_consts import ExperimentSubmitCmdTexts as Texts


logger = initialize_logger('commands.submit')

DEFAULT_SCRIPT_NAME = "experiment.py"


def validate_script_location(script_location: str):
    if not (os.path.isfile(script_location) or os.path.isdir(script_location)):
        handle_error(user_msg=Texts.SCRIPT_NOT_FOUND_ERROR_MSG.format(script_location=script_location))
        exit(2)


def get_default_script_location(script_directory: str) -> str:
    default_script_location = os.path.join(script_directory, DEFAULT_SCRIPT_NAME)
    if not os.path.isfile(default_script_location):
        handle_error(
            user_msg=Texts.DEFAULT_SCRIPT_NOT_FOUND_ERROR_MSG.format(
                script_directory=script_directory, default_script_name=default_script_location
            )
        )
        exit(2)
    else:
        return default_script_location


def validate_script_folder_location(script_folder_location: str):
    if not os.path.isdir(script_folder_location):
        handle_error(
            user_msg=Texts.SCRIPT_DIR_NOT_FOUND_ERROR_MSG.format(script_folder_location=script_folder_location)
        )
        exit(2)


def clean_script_parameters(ctx: click.Context, param, value: Tuple[str, ...]):
    new_value = []
    for parameter in value:
        if "\\" == parameter[0]:
            new_value.append(parameter[1:])
        else:
            new_value.append(parameter)
    return tuple(new_value)


@click.command(short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='s')
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=Texts.HELP_SFL)
@click.option("-t", "--template", help=Texts.HELP_T, default="tf-training-tfjob")
@click.option("-n", "--name", help=Texts.HELP_N, callback=validate_experiment_name)
@click.option("-p", "--pack_param", type=(str, str), multiple=True, help=Texts.HELP_P,
              callback=validate_pack_params_names)
@click.option("-pr", "--parameter_range", nargs=2, multiple=True, help=Texts.HELP_PR)
@click.option("-ps", "--parameter_set", multiple=True, help=Texts.HELP_PS)
@click.option("-e", "--env", multiple=True, help=Texts.HELP_E, callback=validate_env_paramater)
@click.argument("script_parameters", nargs=-1, metavar='[-- SCRIPT_PARAMETERS]', callback=clean_script_parameters)
@common_options()
@pass_state
def submit(state: State, script_location: str, script_folder_location: str, template: str, name: str,
           pack_param: List[Tuple[str, str]], parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
           env: List[str], script_parameters: Tuple[str, ...]):
    if is_current_user_administrator():
        handle_error(logger, Texts.USER_IS_ADMIN_LOG_MSG, Texts.USER_IS_ADMIN_USR_MSG)
        exit(1)

    logger.debug(Texts.SUBMIT_START_LOG_MSG)
    validate_script_location(script_location)

    if os.path.isdir(script_location):
        script_location = get_default_script_location(script_directory=script_location)

    if script_folder_location:
        validate_script_folder_location(script_folder_location)

    click.echo(Texts.SUBMIT_START_USER_MSG)

    # noinspection PyBroadException
    try:
        runs_list, _ = submit_experiment(run_kind=RunKinds.TRAINING, script_location=script_location,
                                         script_folder_location=script_folder_location,
                                         template=template, name=name, pack_params=pack_param,
                                         parameter_range=parameter_range, parameter_set=parameter_set,
                                         script_parameters=script_parameters,
                                         env_variables=env)
    except K8sProxyCloseError as exe:
        handle_error(user_msg=exe.message)
        click.echo(exe.message)
    except SubmitExperimentError as exe:
        handle_error(user_msg=Texts.SUBMIT_ERROR_MSG.format(exception_message=exe.message))
        exit(1)
    except Exception:
        handle_error(user_msg=Texts.SUBMIT_OTHER_ERROR_MSG)
        exit(1)

    # display information about status of a training
    click.echo(tabulate([(run.cli_representation.name, run.cli_representation.parameters,
                          run.cli_representation.status, run.message) for run in runs_list],
                        headers=[RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE], tablefmt="orgtbl"))

    # if there is at least one FAILED experiment - application has to return exit code != 0
    if any(run.state == RunStatus.FAILED for run in runs_list):
        handle_error(logger, Texts.FAILED_RUNS_LOG_MSG)
        exit(1)
