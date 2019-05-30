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
import tabulate

from util.cli_state import common_options, pass_state, State
from cli_text_consts import TemplateListCmdTexts as Texts
from commands.template.common import prepare_list_of_templates, TEMPLATE_LIST_HEADERS
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.spinner import spinner


logger = initialize_logger(__name__)


@click.command(name='list', short_help=Texts.HELP, cls=AliasCmd, alias='ls', options_metavar='[options]')
@common_options()
@pass_state
def list_templates(state: State):
    """ List experiments. """
    with spinner(text=Texts.GETTING_LIST_OF_TEMPLATES_MSG):
        list_of_templates, error_messages = prepare_list_of_templates()

    for message in error_messages:
        click.echo(message)

    click.echo(tabulate.tabulate(list_of_templates, headers=TEMPLATE_LIST_HEADERS, tablefmt="orgtbl"))

    if error_messages:
        exit(1)
    else:
        exit(0)
