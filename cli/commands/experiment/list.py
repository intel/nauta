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

from cli_state import common_options, pass_state, State
import platform_resources.runs as runs_api
from platform_resources.run_model import RunStatus
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace

logger = initialize_logger(__name__)


@click.command(name='list', cls=AliasCmd, alias='ls')
@click.option('-a', '--all-users', is_flag=True,
              help='Show all experiments, regardless of owner')
@click.option('-n', '--name', type=str,
              help='A regular expression to narrow down list to experiments that are matching this expression')
@click.option('-s', '--status', type=click.Choice([status.name for status in RunStatus]),
              help='List experiments with matching status')
@common_options()
@pass_state
def list_experiments(state: State, all_users: bool, name: str, status: RunStatus):
    """
    List experiments.
    """

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()
        status = RunStatus[status] if status else None

        # List experiments command is actually listing Run resources instead of Experiment resources
        runs = runs_api.list_runs(namespace=namespace, state=status, name_filter=name)
        click.echo(tabulate([run.cli_short_representation for run in runs],
                            headers=['Name', 'Parameters', 'Metrics', 'Submission date',
                                     'Submitter', 'Status'], tablefmt="orgtbl"))
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
