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
import itertools
from typing import Tuple, List

from tabulate import tabulate


from commands.common import EXPERIMENT_NAME, EXPERIMENT_PARAMETERS, \
    EXPERIMENT_STATUS, EXPERIMENT_MESSAGE, create_environment, \
    delete_environment, convert_to_number, ExperimentDescription, ExperimentStatus, \
    generate_experiment_name
import draft.cmd as cmd
from util.logger import initialize_logger
from packs.tf_training import update_configuration
from util.k8s.kubectl import start_port_forwarding
from cli_state import common_options, pass_state, State

from util.system import get_current_os, OS
from util import socat
from util.exceptions import KubectlIntError


log = initialize_logger('commands.submit')

HELP = "Command used to submitting training scripts for a single-node tensorflow training."
HELP_SFL = "Name of a folder with additional files used by a script - other .py files, data etc. " \
           "If not given - its content won't be copied into an image."
HELP_T = "Name of a template used to create a delpoyment. By default a single-node tensorflow training" \
         " template is chosen. List of available templates might be obtained by" \
         " issuing dlsctl template_list command."
HELP_PR = "Values (set or range) of a single parameter. "
HELP_PS = "Set of values of one or several parameters."


@click.command(help=HELP)
@click.argument("script_location", type=click.Path(), required=True)
@click.option("-sfl", "--script_folder_location", type=click.Path(), help=HELP_SFL)
@click.option("-t", "--template", help=HELP_T, default="tf-training")
@click.option("-pr", "--parameter_range", nargs=2, multiple=True, help=HELP_PR)
@click.option("-ps", "--parameter_set", multiple=True, help=HELP_PS)
@click.argument("script_parameters", nargs=-1)
@common_options
@pass_state
def submit(state: State, script_location: str, script_folder_location: str, template: str,
           parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
           script_parameters: Tuple[str, ...]):
    log.debug("Submit - start")
    click.echo("Submitting experiment/experiments.")

    try:
        experiments_list = create_list_of_experiments(parameter_range, parameter_set)
    except KubectlIntError as exe:
        log.exception(str(exe))
        click.echo(str(exe))
        sys.exit(1)
    except Exception:
        message = "Problem during preparation of experiments' data."
        log.exception(message)
        click.echo(message)
        sys.exit(1)

    try:
        # prepare enviroments for all experiments
        for experiment in experiments_list:
            if script_parameters and experiment.parameters:
                current_script_parameters = script_parameters + experiment.parameters
            elif script_parameters:
                current_script_parameters = script_parameters
            elif experiment.parameters:
                current_script_parameters = experiment.parameters
            else:
                current_script_parameters = ""

            experiment_folder = prepare_experiment_environment(experiment.name, script_location,
                                                               script_folder_location,
                                                               current_script_parameters,
                                                               template)

            experiment.folder = experiment_folder
    except Exception as exe:
        # any error in this step breaks execution of this command
        message = "Problems during creation of experiments' environments."
        log.exception(message)
        click.echo(message)
        # just in case - remove folders that were created with a success
        delete_experiments(experiments_list)
        sys.exit(1)

    # if there is more than one experiment to be scheduled - first ask whether all of them should
    # be submitted
    if len(experiments_list) > 1:
        click.echo("Please confirm that the following experiments should be submitted.")
        click.echo(tabulate({EXPERIMENT_NAME: [experiment.name for experiment in experiments_list],
                             EXPERIMENT_PARAMETERS:
                                 [experiment.formatted_parameters() for experiment in experiments_list]},
                            headers=[EXPERIMENT_NAME, EXPERIMENT_PARAMETERS],
                            tablefmt="orgtbl"))
        if not click.confirm('Do you want to continue?'):
            delete_experiments(experiments_list)
            sys.exit(1)

    # start port forwarding
    # noinspection PyBroadException
    try:
        process, tunnel_port, container_port = start_port_forwarding('docker-registry')
    except Exception as exe:
        delete_experiments(experiments_list)
        log.exception("Error during creation of a proxy for a docker registry.")
        click.echo("Error during creation of a proxy for a docker registry.")
        click.echo(exe)
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

    # submit experiments
    for experiment in experiments_list:
        try:
            submit_one_experiment(experiment.folder)
            experiment.status = ExperimentStatus.SUBMITTED
        except Exception as exe:
            experiment.status = ExperimentStatus.ERROR
            experiment.message = exe

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

    # display information about status of a training
    click.echo(tabulate({EXPERIMENT_NAME: [experiment.name for experiment in experiments_list],
                         EXPERIMENT_PARAMETERS: [experiment.formatted_parameters() for experiment in experiments_list],
                         EXPERIMENT_STATUS: [experiment.formatted_status() for experiment in experiments_list],
                         EXPERIMENT_MESSAGE: [experiment.error_message for experiment in experiments_list]},
                        headers=[EXPERIMENT_NAME, EXPERIMENT_PARAMETERS, EXPERIMENT_STATUS,
                                 EXPERIMENT_MESSAGE],
                        tablefmt="orgtbl"))

    log.debug("Submit - stop")


def create_list_of_experiments(parameter_range: List[Tuple[str, str]],
                               parameter_set: Tuple[str, ...]) -> List[ExperimentDescription]:
    # each element of the list contains
    # - experiment name
    # - experiment status
    # - error message (if exists)
    # - experiment folder
    # - experiment paramaters
    experiment_name = generate_experiment_name()

    experiments_list = []

    if not parameter_range and not parameter_set:
        experiments_list = [ExperimentDescription(name=experiment_name)]
    else:
        list_of_range_parameters = [("", )]
        list_of_set_parameters = [("", )]

        if parameter_range:
            list_of_range_parameters = analyze_pr_parameters_list(parameter_range)

        if parameter_set:
            list_of_set_parameters = analyze_ps_parameters_list(parameter_set)

        experiment_index = 1
        for set_param in list_of_set_parameters:
            for range_param in list_of_range_parameters:
                current_experiment_name = experiment_name + "-" + str(experiment_index)

                current_params = ()

                if len(set_param) >= 1 and set_param[0]:
                    current_params = set_param

                if len(range_param) >= 1 and range_param[0]:
                    current_params = current_params + range_param

                experiments_list.append(ExperimentDescription(name=current_experiment_name,
                                                              parameters=current_params))

                experiment_index = experiment_index + 1

    return experiments_list


def prepare_experiment_environment(experiment_name: str, script_location: str,
                                   script_folder_location: str, script_parameters: Tuple[str, ...],
                                   pack_type: str) -> str:
    """
    Prepares draft's environment for a certain experiment based on provided parameters

    :param experiment_name: name of an experiment
    :param script_location: location of a script used for training purposes
    :param script_folder_location: location of an additional folder used in training
    :param script_parameters: parameters passed to a script
    :param pack_type: type of a pack used to start training job
    :return: name of folder with an environment created for this experiment
    In case of any problems - an exception with a description of a problem is thrown
    """
    log.debug("Prepare experiment environment - start")
    log.debug("Prepare experiment environment - experiment name : {}".format(experiment_name))
    try:
        # create an environment
        experiment_folder = create_environment(experiment_name, script_location, script_folder_location)
        # generate draft's data
        output, exit_code = cmd.create(working_directory=experiment_folder, pack_type=pack_type)
        if exit_code:
            raise KubectlIntError("Draft templates haven't been generated. Reason - {}".format(output))
        # reconfigure draft's templates
        update_configuration(experiment_folder, script_location, script_folder_location, script_parameters)
    except Exception as exe:
        delete_environment(experiment_folder)
        raise KubectlIntError(exe)

    log.debug("Prepare experiment environment - stop")
    return experiment_folder


def submit_one_experiment(experiment_folder: str):
    """
    Submits one experiment using draft's environment located in a folder given as a pramater.

    :param experiment_folder: location of a folder with a description of an environment
    In case of any problems it throws an exception with a description of a problem
    """
    log.debug("Submit one experiment - start")
    log.debug("Submit one experiment - experiment name : {}".format(experiment_folder))

    # run training
    output, exit_code = cmd.up(working_directory=experiment_folder)

    if exit_code:
        error_message = "Job hasn't been deployed. Reason - {}".format(output)
        log.error(error_message)
        delete_environment(experiment_folder)
        raise KubectlIntError(error_message)

    log.debug("Submit one experiment - stop")


def delete_experiments(experiments_list: List[ExperimentDescription]):
    """
    Removes folders with experiments from a list given as a parameter.

    :param experiments_list: list of experiments to be removed.
    """
    for experiment in experiments_list:
        if experiment.folder:
            delete_environment(experiment.folder)


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
