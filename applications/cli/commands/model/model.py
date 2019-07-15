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

from commands.model.status import status

from commands.model import export
from util.logger import initialize_logger
from util.aliascmd import AliasGroup
from cli_text_consts import ModelCmdTexts as Texts


logger = initialize_logger(__name__)


@click.group(short_help=Texts.HELP, help=Texts.HELP, cls=AliasGroup, alias='mo',
             subcommand_metavar="COMMAND [options] [args]...")
def model():
    pass


model.add_command(export.export)
model.add_command(status)
