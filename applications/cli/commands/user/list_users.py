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

from sys import exit

import click
from tabulate import tabulate

from util.cli_state import common_options, pass_state, State
from platform_resources.user import User
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import UserListCmdTexts as Texts


logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.HELP, name='list', cls=AliasCmd, alias='ls',
               options_metavar='[options]')
@click.option('-c', '--count', type=click.IntRange(min=1), help=Texts.HELP_C)
@common_options()
@pass_state
def list_users(state: State, count: int):
    """ List users. """
    try:
        users = User.list()
        displayed_items_count = count if count else len(users)
        click.echo(tabulate([user.cli_representation for user in users[-displayed_items_count:]],
                            headers=Texts.TABLE_HEADERS,
                            tablefmt="orgtbl"))
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=state.verbosity == 0)
        exit(1)
