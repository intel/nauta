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

from commands.experiment.common import RUN_INFERENCE_NAME, RUN_PARAMETERS, RUN_START_DATE, RUN_DURATION, \
    RUN_SUBMISSION_DATE, RUN_SUBMITTER, RUN_STATUS, RUN_TEMPLATE_NAME, RUN_TEMPLATE_VERSION, RunKinds
from commands.common import list_runs_in_cli, list_unitialized_experiments_in_cli
from util.cli_state import common_options
from platform_resources.run import RunStatus
from util.aliascmd import AliasCmd
from cli_text_consts import PredictListCmdTexts as Texts


LISTED_RUNS_KINDS = [RunKinds.INFERENCE]


@click.command(name='list', help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='ls',
               options_metavar='[options]')
@click.option('-a', '--all-users', is_flag=True, help=Texts.HELP_A)
@click.option('-n', '--name', type=str, help=Texts.HELP_N)
@click.option('-s', '--status', type=click.Choice([status.name for status in RunStatus]), help=Texts.HELP_S)
@click.option('-u', '--uninitialized', is_flag=True, help=Texts.HELP_U)
@click.option('-c', '--count', type=click.IntRange(min=1), help=Texts.HELP_C)
@click.option('-b', '--brief', is_flag=True, help=Texts.HELP_B)
@common_options()
@click.pass_context
def list_inference_instances(ctx: click.Context, all_users: bool, name: str, status: str, uninitialized: bool,
                             count: int, brief: bool):
    """ List inference instances. """
    status = RunStatus[status] if status else None
    if brief:
        table_headers = [RUN_INFERENCE_NAME, RUN_SUBMISSION_DATE, RUN_SUBMITTER, RUN_STATUS]
    else:
        table_headers = [RUN_INFERENCE_NAME, RUN_PARAMETERS, RUN_SUBMISSION_DATE, RUN_START_DATE, RUN_DURATION,
                         RUN_SUBMITTER, RUN_STATUS, RUN_TEMPLATE_NAME, RUN_TEMPLATE_VERSION]
    if uninitialized:
        list_unitialized_experiments_in_cli(verbosity_lvl=ctx.obj.verbosity, all_users=all_users, name=name,
                                            headers=table_headers,
                                            listed_runs_kinds=LISTED_RUNS_KINDS, count=count, brief=brief)
    else:
        list_runs_in_cli(ctx.obj.verbosity, all_users, name, LISTED_RUNS_KINDS, table_headers,
                         status=status, with_metrics=False, count=count, brief=brief)
