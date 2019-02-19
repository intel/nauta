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

import commands.workflow.cancel
import commands.workflow.logs
import commands.workflow.submit
import commands.workflow.view
import commands.workflow.workflow_list
from util.aliascmd import AliasGroup
from cli_text_consts import WorkflowCmdTexts as Texts


@click.group(cls=AliasGroup, alias='wf', short_help=Texts.HELP, help=Texts.HELP,
             subcommand_metavar="COMMAND [options] [args]...")
def workflow():
    pass


workflow.add_command(commands.workflow.cancel.cancel)
workflow.add_command(commands.workflow.view.view)
workflow.add_command(commands.workflow.logs.logs)
workflow.add_command(commands.workflow.workflow_list.workflow_list)
workflow.add_command(commands.workflow.submit.submit)
