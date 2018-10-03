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

from collections import namedtuple
from typing import List
from sys import exit

import click
from tabulate import tabulate

import platform_resources.runs as runs_api
import platform_resources.experiments as experiments_api
from platform_resources.run_model import RunStatus, Run, RunKinds
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from platform_resources.experiment_model import Experiment, ExperimentStatus
from util.system import handle_error, format_timestamp_for_cli
from cli_text_consts import CmdsCommonTexts as Texts


logger = initialize_logger(__name__)

"""
A namedtuple representing uninitialized experiments in CLI.
"""
UninitializedExperimentCliModel = namedtuple('Experiment', ['name', 'parameters_spec', 'metrics',
                                                            'creation_timestamp', 'start_date', 'end_date',
                                                            'submitter', 'status', 'template_name'])


def uninitialized_experiment_cli_representation(experiment: Experiment):
    return UninitializedExperimentCliModel(name=experiment.name, parameters_spec=' '.join(experiment.parameters_spec),
                                           metrics='', start_date='', end_date='',
                                           creation_timestamp=format_timestamp_for_cli(experiment.creation_timestamp),
                                           submitter=experiment.submitter, status=experiment.state.value,
                                           template_name=experiment.template_name)


def list_unitialized_experiments_in_cli(verbosity_lvl: int, all_users: bool,
                                        name: str, headers: List[str], listed_runs_kinds: List[RunKinds] = None):
    """
    Display a list of selected runs in the cli.

    :param verbosity_lvl: level at which error messages should be logged or displayed
    :param all_users: whether to display runs regardless of their owner or not
    :param name: regular expression to which names of the shown runs have to match
    :param headers: headers which will be displayed on top of a table shown in the cli
    """

    if not listed_runs_kinds:
        listed_runs_kinds = [RunKinds.TRAINING, RunKinds.JUPYTER]

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()

        creating_experiments = experiments_api.list_experiments(namespace=namespace,
                                                                state=ExperimentStatus.CREATING,
                                                                run_kinds_filter=listed_runs_kinds,
                                                                name_filter=name)
        runs = runs_api.list_runs(namespace=namespace, name_filter=name, run_kinds_filter=listed_runs_kinds)

        # Get Experiments without associated Runs
        names_of_experiment_with_runs = set()
        for run in runs:
            names_of_experiment_with_runs.add(run.experiment_name)

        uninitialized_experiments = [experiment for experiment in creating_experiments
                                     if experiment.name not in names_of_experiment_with_runs]

        click.echo(tabulate([uninitialized_experiment_cli_representation(experiment)
                             for experiment in uninitialized_experiments],
                            headers=headers, tablefmt="orgtbl"))
    except experiments_api.InvalidRegularExpressionError:
        handle_error(logger, Texts.INVALID_REGEX_ERROR_MSG, Texts.INVALID_REGEX_ERROR_MSG,
                     add_verbosity_msg=verbosity_lvl == 0)
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=verbosity_lvl == 0)
        exit(1)


def list_runs_in_cli(verbosity_lvl: int, all_users: bool, name: str, status: RunStatus,
                     listed_runs_kinds: List[RunKinds], runs_list_headers: List[str], with_metrics: bool):
    """
    Display a list of selected runs in the cli.

    :param verbosity_lvl: level at which error messages should be logged or displayed
    :param all_users: whether to display runs regardless of their owner or not
    :param name: regular expression to which names of the shown runs have to match
    :param status: display runs with this status
    :param listed_runs_kinds: list of kinds of runs that will be listed out
    :param runs_list_headers: headers which will be displayed on top of a table shown in the cli
    :param with_metrics: whether to show metrics column or not
    """

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()
        status = RunStatus[status] if status else None

        # List experiments command is actually listing Run resources instead of Experiment resources with one
        # exception - if run is initialized - dlsctl displays data of an experiment instead of data of a run
        runs = replace_initializing_runs(runs_api.list_runs(namespace=namespace, state_list=[status], name_filter=name,
                                                            run_kinds_filter=listed_runs_kinds))
        runs_representations = [run.cli_representation for run in runs]
        if with_metrics:
            runs_table_data = runs_representations
        else:
            runs_table_data = [
                (run_representation.name, run_representation.parameters, run_representation.submission_date,
                 run_representation.start_date, run_representation.end_date,
                 run_representation.submitter, run_representation.status, run_representation.template_name)
                for run_representation in runs_representations
            ]
        click.echo(tabulate(runs_table_data, headers=runs_list_headers, tablefmt="orgtbl"))
    except runs_api.InvalidRegularExpressionError:
        handle_error(logger, Texts.INVALID_REGEX_ERROR_MSG, Texts.INVALID_REGEX_ERROR_MSG,
                     add_verbosity_msg=verbosity_lvl == 0)
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=verbosity_lvl == 0)
        exit(1)


def replace_initializing_runs(run_list: List[Run]):
    """
    Creates a list of runs with initializing runs replaced by fake runs created based
    on experiment data. If there is at least one initializing run within a certain
    experiment - none of runs creating this experiment is displayed.
    :param run_list: list of runs to be checked
    :return: list without runs that are initialized at the moment
    """
    initializing_experiments = set()
    ret_list = []
    for run in run_list:
        exp_name = run.experiment_name
        if (run.state is None or run.state == '') and exp_name not in initializing_experiments:
            experiment = experiments_api.get_experiment(exp_name, run.submitter)
            ret_list.append(create_fake_run(experiment))
            initializing_experiments.add(exp_name)
        elif exp_name not in initializing_experiments:
            ret_list.append(run)

    return ret_list


def create_fake_run(experiment: Experiment) -> Run:
    return Run(name=experiment.name, experiment_name=experiment.name, metrics={},
               parameters=experiment.parameters_spec, pod_count=0,
               pod_selector={}, state=RunStatus.CREATING, submitter=experiment.submitter,
               creation_timestamp=experiment.creation_timestamp,
               template_name=experiment.template_name)
