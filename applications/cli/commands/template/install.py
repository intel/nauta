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

from util.cli_state import common_options
from cli_text_consts import TemplateInstallCmdTexts as Texts
from commands.template.common import load_remote_template, get_repository_address, get_local_templates, \
    download_remote_template
from commands.config import update_resources_in_packs
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from util.spinner import spinner
from util.system import handle_error
from util.config import Config


logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, cls=AliasCmd, alias='i', options_metavar='[options]')
@click.argument("template-name", type=str, required=True)
@common_options()
@click.pass_context
def install(ctx: click.Context, template_name: str):
    packs_location = os.path.join(Config.get_config_path(), "packs")
    chart_file_location = os.path.join(packs_location, template_name)
    repository_address = get_repository_address()

    with spinner(text=Texts.GETTING_LIST_OF_TEMPLATES_MSG) as templates_spinner:
        try:
            remote_template = load_remote_template(template_name, repository_address=repository_address)
        except Exception:
            templates_spinner.stop()
            handle_error(logger, user_msg=Texts.FAILED_TO_LOAD_TEMPLATE.format(
                template_name=template_name),
                         log_msg=Texts.FAILED_TO_LOAD_TEMPLATE.format(template_name=template_name),
                         add_verbosity_msg=ctx.obj.verbosity == 0)
            sys.exit(1)

        if not remote_template:
            templates_spinner.stop()
            handle_error(logger, user_msg=Texts.REMOTE_TEMPLATE_NOT_FOUND.format(
                template_name=template_name),
                         log_msg=Texts.REMOTE_TEMPLATE_NOT_FOUND.format(template_name=template_name),
                         add_verbosity_msg=ctx.obj.verbosity == 0)
            sys.exit(1)

    local_templates = get_local_templates()
    local_template_counterpart = local_templates.get(template_name)

    if local_template_counterpart:
        if (not click.get_current_context().obj.force) and (not click.confirm(
                Texts.LOCAL_VERSION_ALREADY_INSTALLED.format(
                    local_version=local_template_counterpart.local_version,
                    template_name=local_template_counterpart.name,
                    remote_version=remote_template.remote_version))):
            sys.exit(0)
        # noinspection PyBroadException
        try:
            shutil.rmtree(chart_file_location)
        except Exception:
            logger.exception("failed to remove local copy of template!")

    with spinner(text=Texts.DOWNLOADING_TEMPLATE) as download_spinner:
        try:
            download_remote_template(template=remote_template, repository_address=repository_address,
                                     output_dir_path=packs_location)
        except Exception:
            download_spinner.stop()
            handle_error(logger,
                         user_msg=Texts.FAILED_TO_INSTALL_TEMPLATE.format(
                             template_name=template_name,
                             repository_name=repository_address),
                         log_msg=Texts.FAILED_TO_INSTALL_TEMPLATE.format(
                             template_name=template_name, repository_name=repository_address),
                         add_verbosity_msg=ctx.obj.verbosity == 0)
            sys.exit(1)

    update_resources_in_packs()

    click.echo("successfully installed!")
