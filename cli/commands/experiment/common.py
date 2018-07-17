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

import os
import shutil
import itertools
import sys

import click
from typing import Tuple, List
from pathlib import Path
from tabulate import tabulate
from marshmallow import ValidationError

from util.k8s.k8s_info import get_kubectl_current_context_namespace
import draft.cmd as cmd
from packs.tf_training import update_configuration
import platform_resources.experiments as experiments_api
import platform_resources.experiment_model as experiments_model
from platform_resources.run_model import RunStatus
from util.config import EXPERIMENTS_DIR_NAME, FOLDER_DIR_NAME, Config
from util.logger import initialize_logger
from util.system import get_current_os, OS
from util import socat
from util.exceptions import KubectlIntError, K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError, \
    SubmitExperimentError
from util.app_names import DLS4EAppNames
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.k8s.k8s_info import get_app_service_node_port
from platform_resources.custom_object_meta_model import validate_kubernetes_name

# definitions of headers content for different commands
RUN_NAME = "Run"
RUN_STATUS = "Status"
RUN_MESSAGE = "Message"
RUN_PARAMETERS = "Parameters used"

log = initialize_logger('commands.common')


def get_run_environment_path(run_name: str) -> str:
    return os.path.join(Config().config_path, EXPERIMENTS_DIR_NAME, run_name)


def check_run_environment(run_environment_path: str):
    """
    If Run environment is not empty, ask user if it should be deleted in order to proceed with Run environment creation.
    """
    if os.path.isdir(run_environment_path) and os.listdir(run_environment_path):
        if click.confirm(f'Experiment data directory: {run_environment_path} already exists. '
                         f'It will be deleted in order to proceed with experiment submission. '
                         f'Do you want to continue?'):
            delete_environment(run_environment_path)
        else:
            click.echo(f"Cannot continue experiment submission. "
                       f"Please delete experiment's data directory "
                       f"{run_environment_path} manually or use different name for experiment.")
            sys.exit(1)


def create_environment(experiment_name: str, file_location: str, folder_location: str) -> str:
    """
    Creates a complete environment for executing a training using draft.

    :param experiment_name: name of an experiment used to create a folder
                            with content of an experiment
    :param file_location: location of a training script
    :param folder_location: location of a folder with additional data
    :return: (experiment_folder)
    experiment_folder - folder with experiment's artifacts
    In case of any problems during creation of an enviornment it throws an
    exception with a description of a problem
    """
    log.debug("Create environment - start")
    message_prefix = "Experiment's environment hasn't been created. Reason - {}"

    # create a folder for experiment's purposes
    run_environment_path = get_run_environment_path(experiment_name)
    folder_path = os.path.join(run_environment_path, FOLDER_DIR_NAME)
    # copy folder content
    if folder_location:
        try:
            shutil.copytree(folder_location, folder_path)
        except Exception:
            log.exception("Create environment - copying training folder error.")
            raise KubectlIntError(message_prefix.format("Additional folder cannot"
                                                        " be copied into experiment's folder."))

    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    except Exception as exe:
        log.exception("Create environment - creating experiment folder error.")
        raise KubectlIntError(message_prefix.format("Folder with experiments' data cannot be created."))

    # copy training script - it overwrites the file taken from a folder_location
    if file_location:
        try:
            shutil.copy2(file_location, folder_path)
        except Exception as exe:
            log.exception("Create environment - copying training script error.")
            raise KubectlIntError(message_prefix.format("Training script cannot be created."))

    log.debug("Create environment - end")
    return run_environment_path


def delete_environment(experiment_folder: str):
    """
    Deletes draft environment located in a folder given as a paramater
    :param experiment_folder: location of an environment
    """
    try:
        shutil.rmtree(experiment_folder)
    except Exception as exe:
        log.error("Delete environment - i/o error : {}".format(exe))


def convert_to_number(s: str) -> int or float:
    """
    Converts string to number of a proper type.

    :param s: - string to be converted
    :return: number in a proper format - float or int
    """
    try:
        return int(s)
    except ValueError:
        return float(s)


class RunDescription:
    def __init__(self, name: str="", status: RunStatus=None,
                 error_message: str="", folder: str="", parameters: Tuple[str, ...]=None):
        self.name = name
        self.status = status
        self.error_message = error_message
        self.folder = folder
        self.parameters = parameters

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name \
                   and self.status == other.status \
                   and self.error_message == other.error_message \
                   and self.folder == other.folder \
                   and self.parameters == other.parameters

        return False

    def formatted_parameters(self):
        # parameters are stored in a tuple of strings
        if self.parameters:
            return "\n".join(self.parameters)
        else:
            return ""

    def formatted_status(self):
        return self.status.name


def submit_experiment(script_location: str, script_folder_location: str, template: str, name: str,
                      parameter_range: List[Tuple[str, str]], parameter_set: Tuple[str, ...],
                      script_parameters: Tuple[str, ...], pack_params: List[Tuple[str, str]]):
    log.debug("Submit experiment - start")
    try:
        namespace = get_kubectl_current_context_namespace()
        experiment_name, labels = experiments_api.generate_exp_name_and_labels(script_name=script_location,
                                                                               namespace=namespace, name=name)
        runs_list = prepare_list_of_runs(experiment_name=experiment_name, parameter_range=parameter_range,
                                         parameter_set=parameter_set)
    except KubectlIntError as exe:
        log.exception(str(exe))
        raise SubmitExperimentError(str(exe))
    except SubmitExperimentError as exe:
        log.exception(str(exe))
        raise exe
    except Exception:
        message = "Problem during preparation of experiments' data."
        log.exception(message)
        raise SubmitExperimentError(message)

    try:
        config = Config()

        # start port forwarding
        # noinspection PyBroadException
        with K8sProxy(DLS4EAppNames.DOCKER_REGISTRY, port=config.local_registry_port) as proxy:
            # Save port that was actually used in configuration
            if proxy.tunnel_port != config.local_registry_port:
                config.local_registry_port = proxy.tunnel_port

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

                    cluster_registry_port = get_app_service_node_port(dls4e_app_name=DLS4EAppNames.DOCKER_REGISTRY)
                    experiment_run.folder = prepare_experiment_environment(experiment_name=experiment_name,
                                                                           run_name=experiment_run.name,
                                                                           script_location=script_location,
                                                                           script_folder_location=script_folder_location,  # noqa: E501
                                                                           script_parameters=current_script_parameters,
                                                                           pack_type=template, pack_params=pack_params,
                                                                           local_registry_port=proxy.tunnel_port,
                                                                           cluster_registry_port=cluster_registry_port)
            except Exception:
                # any error in this step breaks execution of this command
                message = "Problems during creation of environments."
                log.exception(message)
                # just in case - remove folders that were created with a success
                delete_run_environments(runs_list)
                raise SubmitExperimentError(message)

            # if there is more than one run to be scheduled - first ask whether all of them should be submitted
            if len(runs_list) > 1:
                click.echo("Please confirm that the following Runs should be submitted.")
                click.echo(tabulate({RUN_NAME: [run.name for run in runs_list],
                                     RUN_PARAMETERS: [run.formatted_parameters() for run in runs_list]},
                                    headers=[RUN_NAME, RUN_PARAMETERS], tablefmt="orgtbl"))
                if not click.confirm('Do you want to continue?', default=True):
                    delete_run_environments(runs_list)
                    sys.exit(1)

            # run socat if on Windows or Mac OS
            if get_current_os() in (OS.WINDOWS, OS.MACOS):
                # noinspection PyBroadException
                try:
                    socat.start(proxy.tunnel_port)
                except Exception:
                    error_msg = "Error during creation of a local docker-host tunnel."
                    log.exception(error_msg)
                    raise SubmitExperimentError(error_msg)

            # create Experiment model
            # TODO template_name & template_namespace should be filled after Template implementation
            parameter_range_spec = [f'-pr {param_name} {param_value}' for param_name, param_value in parameter_range]
            parameter_set_spec = [f'-ps {ps_spec}' for ps_spec in parameter_set]
            experiment_parameters_spec = list(script_parameters) + parameter_range_spec + parameter_set_spec
            experiments_api.add_experiment(experiments_model.Experiment(name=experiment_name, template_name=template,
                                                                        parameters_spec=experiment_parameters_spec,
                                                                        template_namespace="template-namespace"),
                                           namespace, labels=labels)

            # submit runs
            for run in runs_list:
                try:
                    submit_draft_pack(run.folder, namespace)
                    run.status = RunStatus.QUEUED
                except Exception as exe:
                    delete_environment(run.folder)
                    run.status = RunStatus.FAILED
                    run.message = exe

    except LocalPortOccupiedError as exe:
        click.echo(exe.message)
        raise SubmitExperimentError(exe.message)
    except K8sProxyCloseError:
        log.exception('Error during closing of a proxy for a {}'.format(DLS4EAppNames.DOCKER_REGISTRY))
        raise K8sProxyCloseError('Docker proxy hasn\'t been closed properly. '
                                 'Check whether it still exists, if yes - close it manually.')
    except K8sProxyOpenError:
        error_msg = "Error during opening of a proxy for a docker registry."
        log.exception(error_msg)
        raise SubmitExperimentError(error_msg)
    except SubmitExperimentError as exe:
        raise exe
    except Exception:
        error_msg = 'Other error during submitting experiments.'
        log.exception(error_msg)
        raise SubmitExperimentError(error_msg)
    finally:
        # noinspection PyBroadException
        # terminate socat if on Windows or Mac OS
        if get_current_os() in (OS.WINDOWS, OS.MACOS):
            # noinspection PyBroadException
            try:
                socat.stop()
            except Exception:
                log.exception("Error during closing of a proxy for a local docker-host tunnel")
                raise K8sProxyCloseError("Local Docker-host tunnel hasn't been closed properly. "
                                         "Check whether it still exists, if yes - close it manually.")

    log.debug("Submit - finish")
    return runs_list


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
                                   pack_type: str, local_registry_port: int, cluster_registry_port: int,
                                   pack_params: List[Tuple[str, str]]) -> str:
    """
    Prepares draft's environment for a certain run based on provided parameters
    :param experiment_name: name of an experiment
    :param run_name: name of an experiment run
    :param script_location: location of a script used for training purposes
    :param script_folder_location: location of an additional folder used in training
    :param script_parameters: parameters passed to a script
    :param pack_type: type of a pack used to start training job
    :param local_registry_port: port on which docker registry is accessible locally
    :param cluster_registry_port: port on which docker registry is accessible within dls4e cluster
    :param pack_params: additional pack params
    :return: name of folder with an environment created for this run
    In case of any problems - an exception with a description of a problem is thrown
    """
    log.debug(f'Prepare run {run_name} environment - start')
    run_folder = get_run_environment_path(run_name)
    try:
        # check environment directory
        check_run_environment(run_folder)
        # create an environment
        create_environment(run_name, script_location, script_folder_location)
        # generate draft's data
        output, exit_code = cmd.create(working_directory=run_folder, pack_type=pack_type)

        if exit_code:
            raise KubectlIntError("Draft templates haven't been generated. Reason - {}".format(output))
        if script_location:
            script_location = Path(script_location).name
        # reconfigure draft's templates
        update_configuration(run_folder=run_folder, script_location=script_location,
                             script_parameters=script_parameters,
                             experiment_name=experiment_name, run_name=run_name,
                             local_registry_port=local_registry_port, cluster_registry_port=cluster_registry_port,
                             pack_type=pack_type, pack_params=pack_params)
    except Exception as exe:
        delete_environment(run_folder)
        raise KubectlIntError(exe) from exe
    log.debug(f'Prepare run {run_name} environment - finish')
    return run_folder


def submit_draft_pack(run_folder: str, namespace: str = None):
    """
    Submits one run using draft's environment located in a folder given as a parameter.
    :param run_folder: location of a folder with a description of an environment
    :param namespace: namespace where tiller used during deployment is located
    In case of any problems it throws an exception with a description of a problem
    """
    log.debug(f'Submit one run: {run_folder} - start')

    # run training
    output, exit_code = cmd.up(working_directory=run_folder, namespace=namespace)

    if exit_code:
        error_message = "Job hasn't been deployed. Reason - {}".format(output)
        log.error(error_message)
        delete_environment(run_folder)
        raise KubectlIntError(error_message)
    log.debug(f'Submit one run {run_folder} - finish')


def delete_run_environments(runs_list: List[RunDescription]):
    """
    Removes folders with Runs from a list given as a parameter.
    :param runs_list: list of runs to be removed.
    """
    for run in runs_list:
        if run.folder:
            delete_environment(run.folder)


def values_range(param_value: str) -> List[str]:
    """
    Returns a list containing values from start to stop with a step prepared based on
    a string representation of the "pr" parameter.
    :param param value: content of the "pr" parameter
    :return: list of values between start and stop with a given step
    """
    ret_range = []
    range_step = param_value.split(":")
    range_values = range_step[0]
    step = range_step[1]
    start, stop = range_values.split("...")

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
            temp_param_values.extend(values_range(param_values))
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


def validate_experiment_name(ctx, param, value):
    try:
        if value:
            if len(value) > 30:
                # tf-operator requires that {user}-{tfjob's name} is no longer than 63 chars, so we need to limit this
                raise ValidationError("Name cannot be longer than 30 characters.")
            validate_kubernetes_name(value)
            return value
    except ValidationError as ex:
        raise click.BadParameter(ex)
