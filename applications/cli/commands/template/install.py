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

import os
import shutil
import sys

import click

from util.cli_state import common_options, pass_state, State
from cli_text_consts import TemplateInstallCmdTexts as Texts
from commands.template.common import load_chart, get_repository_configuration, get_local_templates
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from util.spinner import spinner
from util.github import Github
from util.config import Config


logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, cls=AliasCmd, alias='i', options_metavar='[options]')
@click.argument("template-name", type=str, required=True)
@common_options()
@pass_state
def install(state: State, template_name: str):
    chart_file_location = os.path.join(Config.get_config_path(), "packs", template_name)

    with spinner(text=Texts.GETTING_LIST_OF_TEMPLATES_MSG):
        repository_name, access_token = get_repository_configuration()

        remote_template = load_chart(template_name, Github(repository_name=repository_name, token=access_token))

        if not remote_template:
            click.echo(Texts.REMOTE_TEMPLATE_NOT_FOUND.format(template_name=template_name))
            sys.exit(1)

    local_templates = get_local_templates()
    local_template_counterpart = local_templates.get(template_name)

    if local_template_counterpart:
        click.confirm(Texts.LOCAL_VERSION_ALREADY_INSTALLED.format(
                                                            local_version=local_template_counterpart.local_version,
                                                            template_name=local_template_counterpart.name,
                                                            remote_version=remote_template.remote_version),
                      abort=True)

        # noinspection PyBroadException
        try:
            shutil.rmtree(chart_file_location)
        except Exception:
            logger.exception("failed to remove local copy of template!")

    with spinner(text=Texts.DOWNLOADING_TEMPLATE):
        repository_name, access_token = get_repository_configuration()

        g = Github(repository_name, access_token)

        g.download_whole_directory(template_name, chart_file_location)

    click.echo("successfully installed!")
