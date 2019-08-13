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

from util.cli_state import common_options
from util.aliascmd import AliasCmd
import commands.experiment.cancel
from util.logger import initialize_logger
from cli_text_consts import PredictCancelCmdTexts as Texts
from commands.experiment.common import RunKinds

logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='c', options_metavar='[options]')
@click.argument("name", required=False, metavar='[name]')
@click.option('-m', '--match', default=None, help=Texts.HELP_M)
@click.option('-p', '--purge', default=None, help=Texts.HELP_P, is_flag=True)
@common_options(admin_command=False)
@click.pass_context
def cancel(ctx: click.Context, name: str, match: str, purge: bool):
    """
    Cancels chosen prediction instances based on a name provided as a parameter.
    """
    commands.experiment.cancel.experiment_name = Texts.EXPERIMENT_NAME
    commands.experiment.cancel.experiment_name_plural = Texts.EXPERIMENT_NAME_PLURAL
    ctx.forward(commands.experiment.cancel.cancel, listed_runs_kinds=[RunKinds.INFERENCE])
