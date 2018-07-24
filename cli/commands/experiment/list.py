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
from tabulate import tabulate
from typing import List

from commands.experiment.common import RUN_NAME, RUN_PARAMETERS, RUN_METRICS, RUN_SUBMISSION_DATE, RUN_SUBMITTER, \
    RUN_STATUS, RUN_TEMPLATE_NAME
from cli_state import common_options, pass_state, State
import platform_resources.runs as runs_api
import platform_resources.experiments as experiments_api
from platform_resources.run_model import RunStatus, Run
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from platform_resources.experiment_model import Experiment

logger = initialize_logger(__name__)


@click.command(name='list', cls=AliasCmd, alias='ls')
@click.option('-a', '--all-users', is_flag=True,
              help='Show all experiments, regardless of the owner.')
@click.option('-n', '--name', type=str,
              help='A regular expression to narrow down list to experiments that match this expression.')
@click.option('-s', '--status', type=click.Choice([status.name for status in RunStatus]),
              help='List experiments with matching status.')
@common_options()
@pass_state
def list_experiments(state: State, all_users: bool, name: str, status: RunStatus):
    """
    List experiments.
    """

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()
        status = RunStatus[status] if status else None

        # List experiments command is actually listing Run resources instead of Experiment resources with one
        # exception - if run is initialized - dlsctl displays data of an experiment instead of data of a run
        runs = replace_initalizing_runs(runs_api.list_runs(namespace=namespace, state=status, name_filter=name))

        click.echo(tabulate([run.cli_representation for run in runs],
                            headers=[RUN_NAME, RUN_PARAMETERS, RUN_METRICS, RUN_SUBMISSION_DATE,
                                     RUN_SUBMITTER, RUN_STATUS, RUN_TEMPLATE_NAME], tablefmt="orgtbl"))
    except runs_api.InvalidRegularExpressionError:
        error_msg = f'Regular expression provided for name filtering is invalid: {name}'
        logger.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)
    except Exception:
        error_msg = 'Failed to get experiments list.'
        logger.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)


def replace_initalizing_runs(run_list: List[Run]):
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
