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

from platform_resources.run import RunKinds
from util.cli_state import common_options
from util.aliascmd import AliasCmd
from cli_text_consts import PredictViewCmdTexts
import commands.experiment.view


@click.command(
    help=PredictViewCmdTexts.HELP,
    short_help=PredictViewCmdTexts.SHORT_HELP,
    cls=AliasCmd,
    alias='v',
    options_metavar='[options]')
@click.argument("prediction_instance_name")
@click.option('-u', '--username', help=PredictViewCmdTexts.HELP_U)
@click.pass_context
@common_options()
def view(ctx: click.Context, prediction_instance_name: str, username: str):
    """
    Displays details of an prediction instance.
    """
    commands.experiment.view.Texts = PredictViewCmdTexts  # type: ignore
    ctx.invoke(commands.experiment.view.view, experiment_name=prediction_instance_name, username=username,
               tensorboard=False, accepted_run_kinds=(RunKinds.INFERENCE.value,))
