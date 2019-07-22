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
import sys
from typing import Tuple, List

import click
from tabulate import tabulate

from util.cli_state import common_options
from util.aliascmd import AliasCmd
from cli_text_consts import ModelExportCmdTexts as Texts
from commands.model.common import get_list_of_workflows, EXPORT_WORKFLOWS_LOCATION, EXPORT_LIST_HEADERS, MODEL_HEADERS
from platform_resources.workflow import ArgoWorkflow
from util.config import Config
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.config import NAUTAConfigMap, TBLT_TABLE_FORMAT
from util.system import handle_error

logger = initialize_logger(__name__)

FORMATS_OPTION = "formats"


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='e')
@click.argument("path", required=True, metavar="PATH/formats")
@click.argument("format", required=False, type=str, metavar="[FORMAT]")
@click.argument("operation-options", required=False, nargs=-1, metavar="[-- operation-options]")
@common_options(admin_command=False)
def export(path: str, format: str, operation_options: Tuple[str, ...]):
    if path == FORMATS_OPTION:
        try:
            list_of_workflows = get_list_of_workflows(EXPORT_WORKFLOWS_LOCATION)
        except Exception:
            handle_error(logger, Texts.EXPORT_LIST_ERROR_MSG, Texts.EXPORT_LIST_ERROR_MSG)
            sys.exit(1)

        click.echo(tabulate(list_of_workflows, headers=EXPORT_LIST_HEADERS,
                            tablefmt=TBLT_TABLE_FORMAT))
        sys.exit(0)

    config_path = Config().config_path
    formats: List[str] = []  # noqa: E701
    if os.path.isdir(config_path):
        workflow_exports_files = os.listdir(f'{config_path}/workflows/exports')
        formats = [os.path.splitext(file)[0] for file in workflow_exports_files if file.endswith('.yaml')]

    if not format:
        click.echo(Texts.MISSING_EXPORT_FORMAT.format(formats=formats))
        sys.exit(2)

    format = format.lower()

    if format not in formats:
        click.echo(Texts.WRONG_EXPORT_FORMAT.format(format=format, formats=formats))
        sys.exit(2)

    additional_params_str = " ".join(operation_options)

    try:
        current_namespace = get_kubectl_current_context_namespace()

        export_workflow = ArgoWorkflow.from_yaml(f'{Config().config_path}/workflows/exports/{format}.yaml')

        export_workflow.parameters = {
            'cluster-registry-address': NAUTAConfigMap().registry,
            'saved-model-dir-path': path,
            'additional-params': additional_params_str
        }

        export_workflow.create(namespace=current_namespace)

        workflow: ArgoWorkflow = ArgoWorkflow.get(namespace=current_namespace, name=export_workflow.name)
    except Exception:
        error_msg = 'Failed to create export workflow.'
        click.echo(error_msg)
        logger.exception(error_msg)
        sys.exit(1)

    click.echo(tabulate([workflow.cli_representation], headers=MODEL_HEADERS, tablefmt=TBLT_TABLE_FORMAT))
    click.echo(f'\nSuccessfully created export workflow')
