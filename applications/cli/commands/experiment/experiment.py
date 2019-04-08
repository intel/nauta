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

from commands.experiment import list, cancel, logs, view, submit, interact
from util.logger import initialize_logger
from util.aliascmd import AliasGroup
from cli_text_consts import ExperimentCmdTexts as Texts


logger = initialize_logger(__name__)


@click.group(short_help=Texts.SHORT_HELP, help=Texts.HELP, cls=AliasGroup, alias='exp',
             subcommand_metavar="COMMAND [options] [args]...")
def experiment():
    pass


experiment.add_command(cancel.cancel)
experiment.add_command(submit.submit)
experiment.add_command(list.list_experiments)
experiment.add_command(logs.logs)
experiment.add_command(interact.interact)
experiment.add_command(view.view)
