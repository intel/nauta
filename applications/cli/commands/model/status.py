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

from util.config import TBLT_TABLE_FORMAT
from cli_text_consts import ModelStatusCmdTexts as Texts
from commands.model.common import MODEL_HEADERS, STEP_HEADERS, PodPhase
from platform_resources.workflow import ArgoWorkflow
from util.aliascmd import AliasCmd
from util.cli_state import common_options, pass_state, State
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.system import handle_error
from util.spinner import spinner


logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='s', options_metavar='[options]')
@click.argument("model_name", nargs=1)
@click.option("-s", "--status", type=click.Choice([status.name for status in PodPhase]), help=Texts.HELP_S)
@click.option('-u', '--username', help=Texts.HELP_U)
@common_options(admin_command=False)
@pass_state
def status(state: State, model_name: str, status: PodPhase, username: str):
    """
    Returns status of a model

    :param model_name: name of a model data of which should be displayed
    :param status: status of a model step that should be displayed
    :param username; if checked - searches for model for a certain user
    """
    try:
        if not username:
            namespace = get_kubectl_current_context_namespace()
        else:
            namespace = username
        with spinner(text=Texts.LOAD_DATA_MSG):
            workflow: ArgoWorkflow = ArgoWorkflow.get(namespace=namespace, name=model_name)

        if not workflow:
            click.echo(Texts.MODEL_NOT_FOUND.format(model_name=model_name))
            exit(0)
        click.echo('\nOperation details:\n')
        click.echo(tabulate([workflow.cli_representation], headers=MODEL_HEADERS, tablefmt=TBLT_TABLE_FORMAT))
        click.echo('\nOperation steps:\n')
        if workflow.steps:
            click.echo(tabulate([step.cli_representation for step in workflow.steps
                                 if status is None or status == step.phase], headers=STEP_HEADERS,
                                tablefmt=TBLT_TABLE_FORMAT))
        else:
            click.echo(Texts.LACK_OF_STEPS)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=True)
        exit(1)
