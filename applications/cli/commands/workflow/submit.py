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
from util.config import TBLT_TABLE_FORMAT
from cli_text_consts import WorkflowSubmitTexts as Texts
from util.logger import initialize_logger
from commands.workflow.common import HEADERS
from platform_resources.workflow import ArgoWorkflow
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.spinner import spinner
from util.system import handle_error

logger = initialize_logger(__name__)


@click.command(cls=AliasCmd, alias='s', options_metavar='[options]', help=Texts.HELP, short_help=Texts.SHORT_HELP)
@click.argument("workflow-path", type=click.Path(exists=True, dir_okay=False), required=True)
@common_options(admin_command=False)
@pass_state
def submit(state: State, workflow_path: str):
    try:
        workflow: ArgoWorkflow = ArgoWorkflow.from_yaml(workflow_path)
        namespace = get_kubectl_current_context_namespace()
        with spinner(text=Texts.PROGRESS_MSG):
            workflow.create(namespace=namespace)
            workflow.namespace = namespace  # Set namespace, to properly display owner in CLI
        click.echo(tabulate([workflow.cli_representation], headers=HEADERS, tablefmt=TBLT_TABLE_FORMAT))
    except IOError as e:
        handle_error(logger, Texts.LOAD_SPEC_ERROR_MSG.format(msg=str(e)),
                     Texts.LOAD_SPEC_ERROR_MSG.format(msg=str(e)))
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=True)
        exit(1)
