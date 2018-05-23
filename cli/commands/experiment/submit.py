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
import itertools
from pathlib import Path
from typing import Tuple, List
import os

import click
from marshmallow import ValidationError
from tabulate import tabulate

from commands.experiment.common import RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE, \
    create_environment, delete_environment, convert_to_number, RunDescription, RunStatus
from cli_state import common_options, pass_state, State
import draft.cmd as cmd
from packs.tf_training import update_configuration
import platform_resources.experiments as experiments_api
import platform_resources.experiment_model as experiments_model
from platform_resources.custom_object_meta_model import validate_kubernetes_name
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.system import get_current_os, OS
from util import socat
from util.exceptions import KubectlIntError
from util.app_names import DLS4EAppNames
from util.k8s.k8s_proxy_context_manager import K8sProxy, K8sProxyOpenError, K8sProxyCloseError

log = initialize_logger('commands.submit')

HELP = "Command used to submitting training scripts for a single-node tensorflow training."
HELP_N = "Experiment custom name"
HELP_SFL = "Name of a folder with additional files used by a script - other .py files, data etc. " \
           "If not given - its content won't be copied into an image."
HELP_T = "Name of a template used to create a delpoyment. By default a single-node tensorflow training" \
         " template is chosen. List of available templates might be obtained by" \
         " issuing dlsctl template_list command."
HELP_PR = "Values (set or range) of a single parameter. "
HELP_PS = "Set of values of one or several parameters."


def validate_experiment_name(ctx, param, value):
    try:
        if value:
            validate_kubernetes_name(value)
            return value
    except ValidationError as ex:
        raise click.BadParameter(ex)


@click.command(help=HELP)
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=HELP_SFL)
@click.option("-t", "--template", help=HELP_T, default="tf-training")
@click.option("-n", "--name", help=HELP_N, callback=validate_experiment_name)
@click.option("-pr", "--parameter_range", nargs=2, multiple=True, help=HELP_PR)
@click.option("-ps", "--parameter_set", multiple=True, help=HELP_PS)
@click.argument("script_parameters", nargs=-1)
@common_options
@pass_state
def submit(state: State, script_location: str, script_folder_location: str, template: str, name: str,
           parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
           script_parameters: Tuple[str, ...]):
    log.debug("Submit - start")

    if not os.path.isfile(script_location):
        click.echo(f'Cannot find script: {script_location}. Make sure that provided path is correct.')
        sys.exit(1)

    if script_folder_location and not os.path.isdir(script_folder_location):
        click.echo(f'Cannot find script folder: {script_folder_location}. Make sure that provided path is correct.')
        sys.exit(1)

    click.echo("Submitting experiments.")

    try:
        namespace = get_kubectl_current_context_namespace()
        experiment_name = experiments_api.generate_experiment_name(script_name=Path(script_location).name,
                                                                   namespace=namespace, name=name)
        runs_list = prepare_list_of_runs(experiment_name=experiment_name, parameter_range=parameter_range,
                                         parameter_set=parameter_set)
    except KubectlIntError as exe:
        log.exception(str(exe))
        click.echo(str(exe))
        sys.exit(1)
    except Exception:
        message = "Problem during preparation of experiments' data."
        log.exception(message)
        click.echo(message)
        sys.exit(1)

    k8s_app_name = DLS4EAppNames.DOCKER_REGISTRY
    try:
        # start port forwarding
        # noinspection PyBroadException
        with K8sProxy(k8s_app_name) as proxy:

            try:
                # prepare environments for all experiment's runs
                for experiment_run in runs_list:
                    if script_parameters and experiment_run.parameters:
                        current_script_parameters = script_parameters + experiment_run.parameters
                    elif script_parameters:
                        current_script_parameters = script_parameters
                    elif experiment_run.parameters:
                        current_script_parameters = experiment_run.parameters
                    else:
                        current_script_parameters = ""

                    experiment_run.folder = prepare_experiment_environment(experiment_name=experiment_name,
                                                                           run_name=experiment_run.name,
                                                                           script_location=script_location,
                                                                           script_folder_location=script_folder_location,  # noqa: E501
                                                                           script_parameters=current_script_parameters,
                                                                           pack_type=template,
                                                                           internal_registry_port=proxy.tunnel_port)
            except Exception:
                # any error in this step breaks execution of this command
                message = "Problems during creation of experiments' environments."
                log.exception(message)
                click.echo(message)
                # just in case - remove folders that were created with a success
                delete_runs(runs_list)

                sys.exit(1)

            # if there is more than one run to be scheduled - first ask whether all of them should be submitted
            if len(runs_list) > 1:
                click.echo("Please confirm that the following Runs should be submitted.")
                click.echo(tabulate({RUN_NAME: [run.name for run in runs_list],
                                     RUN_PARAMETERS: [run.formatted_parameters() for run in runs_list]},
                                    headers=[RUN_NAME, RUN_PARAMETERS], tablefmt="orgtbl"))
                if not click.confirm('Do you want to continue?', default=True):
                    delete_runs(runs_list)
                    sys.exit(1)

            # run socat if on Windows or Mac OS
            if get_current_os() in (OS.WINDOWS, OS.MACOS):
                # noinspection PyBroadException
                try:
                    socat.start(proxy.tunnel_port)
                except Exception:
                    log.exception("Error during creation of a proxy for a local docker-host tunnel")
                    click.echo("Error during creation of a local docker-host tunnel.")
                    sys.exit(1)

            # create Experiment model
            # TODO template_name & template_namespace should be filled after Template implementation
            experiments_api.add_experiment(experiments_model.Experiment(name=experiment_name, template_name=template,
                                                                        parameters_spec=list(script_parameters),
                                                                        template_namespace="template-namespace"),
                                           namespace)

            # submit runs
            for run in runs_list:
                try:
                    submit_one_run(run.folder)
                    run.status = RunStatus.SUBMITTED
                except Exception as exe:
                    run.status = RunStatus.ERROR
                    run.message = exe

    except K8sProxyCloseError:
        click.echo('Docker proxy hasn\'t been closed properly. '
                   'Check whether it still exists, if yes - close it manually.')
        log.exception('Error during closing of a proxy for a {}'.format(k8s_app_name))
    except K8sProxyOpenError:
        error_msg = "Error during opening of a proxy for a docker registry."
        log.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)
    except Exception:
        error_msg = 'Other error during submitting exepriments.'
        log.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)
    finally:
        # noinspection PyBroadException
        # terminate socat if on Windows or Mac OS
        if get_current_os() in (OS.WINDOWS, OS.MACOS):
            # noinspection PyBroadException
            try:
                socat.stop()
            except Exception:
                log.exception("Error during closing of a proxy for a local docker-host tunnel")
                click.echo("Local Docker-host tunnel hasn't been closed properly. "
                           "Check whether it still exists, if yes - close it manually.")

    # display information about status of a training
    click.echo(tabulate({RUN_NAME: [run.name for run in runs_list],
                         RUN_PARAMETERS: [run.formatted_parameters() for run in runs_list],
                         RUN_STATUS: [run.formatted_status() for run in runs_list],
                         RUN_MESSAGE: [run.error_message for run in runs_list]},
                        headers=[RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE], tablefmt="orgtbl"))
    log.debug("Submit - finish")


def prepare_list_of_runs(parameter_range: List[Tuple[str, str]], experiment_name: str,
                         parameter_set: Tuple[str, ...]) -> List[RunDescription]:
    run_list = []

    if not parameter_range and not parameter_set:
        run_list = [RunDescription(name=experiment_name)]
    else:
        list_of_range_parameters = [("", )]
        list_of_set_parameters = [("", )]

        if parameter_range:
            list_of_range_parameters = analyze_pr_parameters_list(parameter_range)

        if parameter_set:
            list_of_set_parameters = analyze_ps_parameters_list(parameter_set)

        run_index = 1
        for set_param in list_of_set_parameters:
            for range_param in list_of_range_parameters:
                current_run_name = experiment_name + "-" + str(run_index)
                current_params = ()

                if len(set_param) >= 1 and set_param[0]:
                    current_params = set_param

                if len(range_param) >= 1 and range_param[0]:
                    current_params = current_params + range_param

                run_list.append(RunDescription(name=current_run_name, parameters=current_params))
                run_index = run_index + 1
    return run_list


def prepare_experiment_environment(experiment_name: str, run_name: str, script_location: str,
                                   script_folder_location: str, script_parameters: Tuple[str, ...],
                                   pack_type: str, internal_registry_port: str) -> str:
    """
    Prepares draft's environment for a certain run based on provided parameters
    :param experiment_name: name of an experiment
    :param run_name: name of an experiment run
    :param script_location: location of a script used for training purposes
    :param script_folder_location: location of an additional folder used in training
    :param script_parameters: parameters passed to a script
    :param pack_type: type of a pack used to start training job
    :return: name of folder with an environment created for this run
    In case of any problems - an exception with a description of a problem is thrown
    """
    log.debug(f'Prepare run {run_name} environment - start')
    try:
        # create an environment
        run_folder = create_environment(run_name, script_location, script_folder_location)
        # generate draft's data
        output, exit_code = cmd.create(working_directory=run_folder, pack_type=pack_type)
        if exit_code:
            raise KubectlIntError("Draft templates haven't been generated. Reason - {}".format(output))
        # reconfigure draft's templates
        update_configuration(run_folder, Path(script_location).name, script_folder_location, script_parameters,
                             experiment_name=experiment_name, internal_registry_port=internal_registry_port)
    except Exception as exe:
        delete_environment(run_folder)
        raise KubectlIntError(exe)
    log.debug(f'Prepare run {run_name} environment - finish')
    return run_folder


def submit_one_run(run_folder: str):
    """
    Submits one run using draft's environment located in a folder given as a parameter.
    :param run_folder: location of a folder with a description of an environment
    In case of any problems it throws an exception with a description of a problem
    """
    log.debug(f'Submit one run: {run_folder} - start')

    # run training
    output, exit_code = cmd.up(working_directory=run_folder)

    if exit_code:
        error_message = "Job hasn't been deployed. Reason - {}".format(output)
        log.error(error_message)
        delete_environment(run_folder)
        raise KubectlIntError(error_message)
    log.debug(f'Submit one run {run_folder} - finish')


def delete_runs(runs_list: List[RunDescription]):
    """
    Removes folders with Runs from a list given as a parameter.
    :param runs_list: list of runs to be removed.
    """
    for run in runs_list:
        if run.folder:
            delete_environment(run.folder)


def values_range(start: str, stop: str, step: str) -> List[str]:
    """
    Returns a list containing values from start to stop with a step.
    All params might be floats or ints.
    :param start: first value of a range
    :param stop: last value of a range
    :param step: step
    :return: lsit of values between start and stop with a given step
    """
    ret_range = []
    current_value = convert_to_number(start)
    if "." in step:
        number_of_digits = len(step.split(".")[1])
    else:
        number_of_digits = 0
    step_n = convert_to_number(step)
    stop_n = convert_to_number(stop)
    while current_value <= stop_n:
        ret_range.append(str(current_value))
        current_value = round(current_value + step_n, number_of_digits)

    return ret_range


def prepare_list_of_values(param_name: str, param_values: str) -> List[str]:
    """
    Function converts content of -pr parameter to list of single values.

    :param param_name: name of a parameter which is analysed
    :param param_values: value of a parameter
    :return: list of all values of a parameter
    In case of any problems during analyzing of parameters - it throws
    an exception with a short message about a detected problem.
    More details concerning a cause of such issue can be found in logs.
    """
    error_message = "Parameter {} has incorrect format.".format(param_name)
    if not check_enclosing_brackets(param_values):
        log.error(error_message)
        raise KubectlIntError(error_message)

    try:
        param_values = str.strip(param_values, "{}")
        temp_param_values = []
        # {start...stop:step} form
        if "..." in param_values:
            range_step = param_values.split(":")
            range_values = range_step[0]
            step = range_step[1]
            start, stop = range_values.split("...")
            temp_param_values.extend(values_range(start, stop, step))
        else:
            # {x, y, z} form
            temp_param_values.extend([str.strip(x) for x in param_values.split(",")])

        ret_values = []
        # each value contains parameter name
        for param in temp_param_values:
            ret_values.append("{}={}".format(param_name, param))

    except Exception:
        log.exception(error_message)
        raise KubectlIntError(error_message)

    return ret_values


def analyze_pr_parameters_list(list_of_params: Tuple[Tuple, ...]) -> List[Tuple[str, ...]]:
    """
    Analyzes a list of -pr/--parameter_range paramaters. It returns a list
    containing a tuples with all combinations of values of parameters given by a user.

    :param list_of_params: list with tuples in form (parameter name, parameter value)
            list in this format is returned by a click
    :return: list containing tuples with all combinations of values of params given by
            a user
    In case of any problems during analyzing of parameters - it throws
    an exception with a short message about a detected problem.
    More details concerning a cause of such issue can be found in logs.
    """
    param_names = []
    param_values = []

    for param_name, param_value in list_of_params:
        if param_name in param_names:
            exe_message = "Parameter {} ambiguously defined.".format(param_name)
            log.exception(exe_message)
            raise KubectlIntError(exe_message)

        param_names.append(param_name)

        param_values.append(prepare_list_of_values(param_name, param_value))

    ret_list = list(itertools.product(*param_values))

    return ret_list


def analyze_ps_parameters_list(list_of_params: Tuple[str, ...]):
    """
    Analyzes a list of values of -ps options.
    :param list_of_params:
    :return: list containing tuples of all set of params given as a parameter
    """
    error_message = "One of -ps options has incorrect format."

    ret_list = []

    for param_set in list_of_params:
        if not check_enclosing_brackets(param_set):
            log.error(error_message)
            raise KubectlIntError(error_message)

        try:
            param_values = str.strip(param_set, "{}")
            param_values = [l.strip() for l in param_values.split(",")]
            param_tuple = tuple([l.replace(":", "=", 1) for l in param_values])
            ret_list.append(param_tuple)
        except Exception:
            log.exception(error_message)
            raise KubectlIntError(error_message)

    return ret_list


def check_enclosing_brackets(params: str):
    """
    Performs an initial check of format of a parameters - whether it
    is enclosed in brackets and whether it is not empty
    :param params: parameter to be checked
    :return: True if check was a success, False otherwise
    """
    if not params or (str.strip(params)[0] != "{") or (str.strip(params)[-1] != "}"):
        return False
    return True
