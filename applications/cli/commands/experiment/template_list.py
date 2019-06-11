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

from commands.experiment.common import RUN_TEMPLATE_NAME, get_list_of_packs
from util.cli_state import common_options
from util.aliascmd import AliasCmd
from util.config import TBLT_TABLE_FORMAT
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import ExperimentTemplateListCmdTexts as Texts


log = initialize_logger(__name__)

CHART_YAML_FILENAME = "Chart.yaml"
TEMPL_FOLDER_NAME = "templates"


@click.command("template-list", short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='t',
               options_metavar='[options]')
@common_options()
def template_list():
    list_of_packs = get_list_of_packs()

    if list_of_packs:
        click.echo(tabulate([[row] for row in list_of_packs],
                            headers=[RUN_TEMPLATE_NAME],
                            tablefmt=TBLT_TABLE_FORMAT))
    else:
        handle_error(user_msg=Texts.LACK_OF_PACKS_ERROR_MSG)
        sys.exit(1)
