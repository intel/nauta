#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from sys import exit
import textwrap
from typing import Tuple, List, Optional
import os

import click
from tabulate import tabulate

from commands.experiment.common import RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE, RunKinds, \
    validate_env_paramater
from util.cli_state import common_options, pass_state, State
from util.logger import initialize_logger
from commands.experiment.common import submit_experiment
from util.aliascmd import AliasCmd
from util.exceptions import SubmitExperimentError, K8sProxyCloseError
from commands.experiment.common import validate_experiment_name, validate_pack_params_names, validate_template_name, \
    validate_pack
from platform_resources.run import RunStatus
from util.system import handle_error
from cli_text_consts import ExperimentSubmitCmdTexts as Texts


logger = initialize_logger('commands.submit')

DEFAULT_SCRIPT_NAME = "experiment.py"
DEFAULT_REQUIREMENTS_NAME = "requirements.txt"


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


def get_default_requirements_location(script_directory: str) -> Optional[str]:
    default_requirements_location = os.path.join(script_directory, DEFAULT_REQUIREMENTS_NAME)
    if os.path.isfile(default_requirements_location):
        return default_requirements_location
    else:
        return None


def check_duplicated_params(pack_params: List[Tuple[str, str]]):
    provided_keys: List[str] = []
    for key, val in pack_params:
        if key not in provided_keys:
            provided_keys.append(key)
        else:
            handle_error(
                user_msg=Texts.DUPLICATED_PACK_PARAM.format(pack_param=key)
            )
            exit(2)


def validate_pack_params(pack_params: List[Tuple[str, str]]):
    check_duplicated_params(pack_params)


def clean_script_parameters(ctx: click.Context, param, value: Tuple[str, ...]):
    new_value = []
    for parameter in value:
        if "\\" == parameter[0]:
            new_value.append(parameter[1:])
        else:
            new_value.append(parameter)
    return tuple(new_value)


def format_run_message(run_message: Optional[str]) -> str:
    return textwrap.fill(run_message, width=60) if run_message else ''


@click.command(short_help=Texts.SHORT_HELP, help=Texts.HELP, cls=AliasCmd, alias='s', options_metavar='[options]')
@click.argument("script_location", type=click.Path(exists=True), required=True)
@click.option("-sfl", "--script-folder-location", type=click.Path(exists=True, file_okay=False), help=Texts.HELP_SFL)
@click.option("-t", "--template", help=Texts.HELP_T, default="tf-training-tfjob", callback=validate_template_name)
@click.option("-n", "--name", help=Texts.HELP_N, callback=validate_experiment_name)
@click.option("-p", "--pack-param", type=(str, str), multiple=True, help=Texts.HELP_P,
              callback=validate_pack_params_names)
@click.option("-pr", "--parameter-range", nargs=2, multiple=True, help=Texts.HELP_PR)
@click.option("-ps", "--parameter-set", multiple=True, help=Texts.HELP_PS)
@click.option("-e", "--env", multiple=True, help=Texts.HELP_E, callback=validate_env_paramater)
@click.option("-r", "--requirements", type=click.Path(exists=True, dir_okay=False), required=False, help=Texts.HELP_R)
@click.argument("script-parameters", nargs=-1, metavar='[-- script-parameters]', callback=clean_script_parameters)
@common_options(admin_command=False)
@pass_state
def submit(state: State, script_location: str, script_folder_location: str, template: str, name: str,
           pack_param: List[Tuple[str, str]], parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
           env: List[str], script_parameters: Tuple[str, ...], requirements: Optional[str]):
    logger.debug(Texts.SUBMIT_START_LOG_MSG)
    validate_script_location(script_location)
    validate_pack_params(pack_param)
    validate_pack(template)

    if os.path.isdir(script_location):
        if not requirements:
            requirements = get_default_requirements_location(script_directory=script_location)
        script_location = get_default_script_location(script_directory=script_location)

    click.echo(Texts.SUBMIT_START_USER_MSG)
    runs_list = None
    # noinspection PyBroadException
    try:
        runs_list, runs_errors, _ = submit_experiment(run_kind=RunKinds.TRAINING, script_location=script_location,
                                                      script_folder_location=script_folder_location,
                                                      template=template, name=name, pack_params=pack_param,
                                                      parameter_range=parameter_range, parameter_set=parameter_set,
                                                      script_parameters=script_parameters,
                                                      env_variables=env, requirements_file=requirements)
    except K8sProxyCloseError as exe:
        handle_error(user_msg=exe.message)
        click.echo(exe.message)
        if not runs_list:
            exit(1)
    except SubmitExperimentError as exe:
        handle_error(user_msg=Texts.SUBMIT_ERROR_MSG.format(exception_message=exe.message))
        exit(1)
    except Exception:
        handle_error(user_msg=Texts.SUBMIT_OTHER_ERROR_MSG)
        exit(1)

    # display information about status of a training
    click.echo(tabulate([(run.cli_representation.name, run.cli_representation.parameters,
                          run.cli_representation.status, format_run_message(runs_errors.get(run.name, "")))
                         for run in runs_list],
                        headers=[RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE], tablefmt="orgtbl"))

    # if there is at least one FAILED experiment - application has to return exit code != 0
    if any(run.state == RunStatus.FAILED for run in runs_list):
        handle_error(logger, Texts.FAILED_RUNS_LOG_MSG)
        exit(1)
