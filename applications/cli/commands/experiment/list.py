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

import click

from commands.experiment.common import EXPERIMENTS_LIST_HEADERS, RunKinds, RUN_NAME, RUN_STATUS, RUN_SUBMISSION_DATE,\
    RUN_SUBMITTER
from commands.common.list_utils import list_unitialized_experiments_in_cli, list_runs_in_cli
from util.cli_state import common_options
from platform_resources.run import RunStatus
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from cli_text_consts import ExperimentListCmdTexts as Texts


logger = initialize_logger(__name__)

LISTED_RUNS_KINDS = [RunKinds.TRAINING, RunKinds.JUPYTER]


@click.command(name='list', short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='ls', options_metavar='[options]')
@click.option('-a', '--all-users', is_flag=True, help=Texts.HELP_A)
@click.option('-n', '--name', type=str, help=Texts.HELP_N)
@click.option('-s', '--status', type=click.Choice([status.name for status in RunStatus]), help=Texts.HELP_S)
@click.option('-u', '--uninitialized', is_flag=True, help=Texts.HELP_U)
@click.option('-c', '--count', type=click.IntRange(min=1), help=Texts.HELP_C)
@click.option('-b', '--brief', is_flag=True, help=Texts.HELP_B)
@common_options()
@click.pass_context
def list_experiments(ctx: click.Context, all_users: bool, name: str, status: str, uninitialized: bool, count: int,
                     brief: bool):
    """ List experiments. """
    status = RunStatus[status] if status else None
    if brief:
        list_headers = [RUN_NAME, RUN_SUBMISSION_DATE, RUN_SUBMITTER, RUN_STATUS]
    else:
        list_headers = EXPERIMENTS_LIST_HEADERS
    if uninitialized:
        list_unitialized_experiments_in_cli(verbosity_lvl=ctx.obj.verbosity, all_users=all_users, name=name,
                                            headers=list_headers, count=count, brief=brief)
    else:
        list_runs_in_cli(ctx.obj.verbosity, all_users, name, LISTED_RUNS_KINDS, list_headers, with_metrics=True,
                         status=status, count=count, brief=brief)
