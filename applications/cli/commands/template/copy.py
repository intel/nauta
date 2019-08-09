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

from util.cli_state import common_options
from commands.template.common import get_local_templates, Template
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from cli_text_consts import TemplateCopyCmdTexts as Texts


logger = initialize_logger(__name__)

MAX_TEMPLATE_DESCRIPTION_LENGTH = 255


@click.command(short_help=Texts.HELP, cls=AliasCmd, alias='c', options_metavar='[options]')
@click.argument("src-template-name", type=str, required=True)
@click.argument("dest-template-name", type=str, required=True)
@click.option("-d", "--description", type=str, required=False, help=Texts.HELP_DESCRIPTION)
@click.option("-ve", "--version", type=str, default='0.1.0', required=False, help=Texts.HELP_VERSION)
@common_options()
@click.pass_context
def copy(ctx: click.Context, src_template_name: str, dest_template_name: str, description: str, version: str):
    local_templates = get_local_templates()
    if not local_templates.get(src_template_name):
        click.echo(Texts.SRC_TEMPLATE_NOT_FOUND.format(src_template_name=src_template_name))
        exit(1)

    if local_templates.get(dest_template_name):
        click.echo(Texts.TEMPLATE_ALREADY_EXISTS.format(dest_template_name=dest_template_name))
        exit(1)

    if not description:
        description = None
        while not description or not description.strip():
            description = click.prompt(Texts.DESCRIPTION_PROMPT.format(max_len=MAX_TEMPLATE_DESCRIPTION_LENGTH))

        description = description[:MAX_TEMPLATE_DESCRIPTION_LENGTH]

    try:
        new_template = Template(name=dest_template_name, description=description, local_version=version)
        new_template.render_from_existing_template(src_template_name=src_template_name)
        click.echo(Texts.COPY_SUCCESS.format(dest_template_name=dest_template_name,
                                             src_template_name=src_template_name))
    except Exception:
        error_msg = Texts.COPY_FAILURE.format(src_template_name=src_template_name,
                                              dest_template_name=dest_template_name)
        logger.exception(error_msg)
        click.echo(error_msg)
        exit(1)
