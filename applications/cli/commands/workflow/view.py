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
import yaml
from tabulate import tabulate

from util.cli_state import common_options, pass_state, State
from cli_text_consts import WorkflowViewTexts as Texts
from commands.workflow.common import HEADERS
from platform_resources.workflow import ArgoWorkflow
from util.aliascmd import AliasCmd
from util.config import TBLT_TABLE_FORMAT
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.system import handle_error

logger = initialize_logger(__name__)


@click.command(cls=AliasCmd, alias='v', options_metavar='[options]', help=Texts.HELP, short_help=Texts.SHORT_HELP)
@click.argument("workflow-name", type=str, required=True)
@common_options(admin_command=False)
@pass_state
def view(state: State, workflow_name: str):
    try:
        namespace = get_kubectl_current_context_namespace()
        workflow: ArgoWorkflow = ArgoWorkflow.get(namespace=namespace, name=workflow_name)
        if not workflow:
            click.echo(Texts.NOT_FOUND_MSG.format(workflow_name=workflow_name))
            exit(0)

        click.echo(tabulate([workflow.cli_representation], headers=HEADERS, tablefmt=TBLT_TABLE_FORMAT))
        click.echo('\nWorkflow status:\n')
        click.echo(yaml.safe_dump(workflow.status))
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=True)
        exit(1)
