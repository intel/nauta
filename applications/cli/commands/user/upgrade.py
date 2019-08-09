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
from typing import List

import click

from util.cli_state import common_options
from cli_text_consts import UserUpgradeCmdTexts as Texts
from util.aliascmd import AliasCmd
from platform_resources.user import User
from util.app_names import NAUTAAppNames
from util.k8s.k8s_proxy_context_manager import K8sProxy
from git_repo_manager.client import GitRepoManagerClient
from util.spinner import spinner
from util.system import handle_error
from util.logger import initialize_logger

logger = initialize_logger(__name__)


@click.command(help=Texts.SHORT_HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='u')
@common_options(admin_command=True)
@click.pass_context
def upgrade(ctx: click.Context):
    """
    Upgrade users after Nauta upgrade.
    """

    with spinner(text=Texts.UPGRADE_IN_PROGRESS):
        # noinspection PyBroadException
        try:
            # noinspection PyTypeChecker
            users: List[User] = User.list()

            with K8sProxy(NAUTAAppNames.GIT_REPO_MANAGER, number_of_retries_wait_for_readiness=60) as proxy:
                grm_client = GitRepoManagerClient(host='127.0.0.1', port=proxy.tunnel_port)

                for user in users:
                    grm_user = grm_client.get_user(user.name)
                    if not grm_user:
                        grm_client.add_nauta_user(user.name)
        except Exception:
            handle_error(logger, Texts.UPGRADE_FAILED, Texts.UPGRADE_FAILED,
                         add_verbosity_msg=ctx.obj.verbosity == 0)
            sys.exit(1)

    click.echo(Texts.UPGRADE_SUCCEEDED)
