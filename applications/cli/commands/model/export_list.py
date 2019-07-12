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

import sys

import click
from tabulate import tabulate

from cli_text_consts import ModelExportListCmdTexts as Texts
from commands.model.common import get_list_of_workflows, EXPORT_WORKFLOWS_LOCATION, EXPORT_LIST_HEADERS
from util.aliascmd import AliasCmd
from util.cli_state import common_options, pass_state, State
from util.config import TBLT_TABLE_FORMAT
from util.logger import initialize_logger
from util.system import handle_error

log = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='ls')
@common_options()
@pass_state
def export_list(state: State):

    try:
        list_of_workflows = get_list_of_workflows(EXPORT_WORKFLOWS_LOCATION)
    except Exception:
        handle_error(log, Texts.EXPORT_LIST_ERROR_MSG, Texts.EXPORT_LIST_ERROR_MSG)
        sys.exit(1)

    click.echo(tabulate(list_of_workflows, headers=EXPORT_LIST_HEADERS, tablefmt=TBLT_TABLE_FORMAT))
