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

from util.cli_state import common_options
from util.aliascmd import AliasCmd
from cli_text_consts import ModelExportCmdTexts as Texts
from platform_resources.workflow import ArgoWorkflow
from util.config import Config
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.config import NAUTAConfigMap

logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='e')
@click.argument("path", required=True)
@click.argument("format", required=True, type=str)
@click.argument("operation-options", nargs=-1, metavar="[-- operation-options]")
@click.option("-p", "--process", type=str, required=False, help=Texts.HELP_P)
@common_options(admin_command=False)
def export(path: str, format: str, operation_options: Tuple[str, ...], process: str):
    additional_params_str = " ".join(operation_options)
    format = format.lower()
    config_path = Config().config_path
    formats: List[str] = []  # noqa: E701
    if os.path.isdir(config_path):
        workflow_exports_files = os.listdir(f'{config_path}/workflows/exports')
        formats = [os.path.splitext(file)[0] for file in workflow_exports_files if file.endswith('.yaml')]

    if format not in formats:
        click.echo(Texts.WRONG_EXPORT_FORMAT.format(format=format, formats=formats))
        sys.exit(2)

    if process:
        process_path = f'{config_path}/workflows/processes'
        kinds: List[str] = []
        if os.path.isdir(process_path):
            process_kinds = os.listdir(f'{config_path}/workflows/processes')
            kinds = [os.path.splitext(file)[0] for file in process_kinds if file.endswith('.yaml')]

        if process not in kinds:
            click.echo(Texts.WRONG_PROCESS_KIND.format(process=process, kinds=kinds))
            sys.exit(2)

    try:
        current_namespace = get_kubectl_current_context_namespace()

        export_workflow = ArgoWorkflow.from_yaml(f'{Config().config_path}/workflows/exports/{format}.yaml')

        export_workflow.parameters = {
            'cluster-registry-address': NAUTAConfigMap().registry,
            'saved-model-dir-path': path,
            'additional-params': additional_params_str
        }

        if process:
            process_workflow = ArgoWorkflow.from_yaml(f'{Config().config_path}/workflows/processes/{process}.yaml')
            export_workflow.add_process(process_workflow)

        export_workflow.create(namespace=current_namespace)
    except Exception:
        error_msg = 'Failed to create export workflow.'
        click.echo(error_msg)
        logger.exception(error_msg)
        sys.exit(1)

    click.echo(f'Successfully created export workflow: {export_workflow.name}')
