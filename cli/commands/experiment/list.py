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

from commands.experiment.common import EXPERIMENTS_LIST_HEADERS, RunKinds
from commands.common import list_runs_in_cli, list_unitialized_experiments_in_cli
from cli_state import common_options, pass_state, State
from platform_resources.run_model import RunStatus
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from cli_text_consts import EXPERIMENT_LIST_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)

LISTED_RUNS_KINDS = [RunKinds.TRAINING, RunKinds.JUPYTER]


@click.command(name='list', cls=AliasCmd, alias='ls')
@click.option('-a', '--all-users', is_flag=True, help=TEXTS["help_a"])
@click.option('-n', '--name', type=str, help=TEXTS["help_n"])
@click.option('-s', '--status', type=click.Choice([status.name for status in RunStatus]), help=TEXTS["help_s"])
@click.option('-u', '--uninitialized', is_flag=True, help=TEXTS["help_u"])
@common_options()
@pass_state
def list_experiments(state: State, all_users: bool, name: str, status: RunStatus, uninitialized: bool):
    """ List experiments. """
    if uninitialized:
        list_unitialized_experiments_in_cli(verbosity_lvl=state.verbosity, all_users=all_users, name=name,
                                            headers=EXPERIMENTS_LIST_HEADERS)
    else:
        list_runs_in_cli(state.verbosity, all_users, name, status, LISTED_RUNS_KINDS, EXPERIMENTS_LIST_HEADERS,
                         with_metrics=True)
