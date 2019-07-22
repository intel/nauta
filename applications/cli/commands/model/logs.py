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

from cli_text_consts import ModelExportLogsCmdTexts as Texts
from commands.model.common import get_logs
from util.cli_state import common_options, pass_state, State
from util.logger import initialize_logger
from util.aliascmd import AliasCmd

logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='lg', options_metavar='[options]')
@click.argument('operation-name', required=False, metavar='[operation_name]')
@click.option('-sd', '--start-date', help=Texts.HELP_SD)
@click.option('-ed', '--end-date', help=Texts.HELP_ED)
@click.option('-m', '--match', help=Texts.HELP_M)
@click.option('-o', '--output', help=Texts.HELP_O, is_flag=True)
@click.option('-pa', '--pager', help=Texts.HELP_PAGER, is_flag=True, default=False)
@click.option('-f', '--follow', help=Texts.HELP_F, is_flag=True, default=False)
@common_options(admin_command=False)
@pass_state
def logs(state: State, operation_name: str, start_date: str,
         end_date: str, match: str, output: bool, pager: bool, follow: bool):
    """
    Show logs for a given model export operation.
    """

    get_logs(operation_name=operation_name, start_date=start_date, end_date=end_date,
             match=match, output=output, pager=pager, follow=follow)
