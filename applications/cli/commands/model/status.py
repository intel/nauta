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
from typing import List

from util.config import TBLT_TABLE_FORMAT
from cli_text_consts import ModelStatusCmdTexts as Texts
from commands.model.common import MODEL_HEADERS
from platform_resources.workflow import ArgoWorkflow
from util.aliascmd import AliasCmd
from util.cli_state import common_options
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.system import handle_error
from util.spinner import spinner


logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='s', options_metavar='[options]')
@click.option('-u', '--username', help=Texts.HELP_U)
@common_options(admin_command=False)
@click.pass_context
def status(ctx: click.Context, username: str):
    """
    Returns status of a model
    :param username; if checked - searches for model for a certain user
    """
    try:
        workflows: List[ArgoWorkflow.ArgoWorkflowCliModel] = []
        if not username:
            namespace = get_kubectl_current_context_namespace()
        else:
            namespace = username
        with spinner(text=Texts.LOAD_DATA_MSG):
            # filtering out workflows used to build images with training jobs
            workflows = [workflow.cli_representation for workflow in
                         ArgoWorkflow.list(namespace=namespace,
                                           label_selector="type!=build-workflow")]

        click.echo(tabulate(workflows, headers=MODEL_HEADERS, tablefmt=TBLT_TABLE_FORMAT))
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=True)
        exit(1)
