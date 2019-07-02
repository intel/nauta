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
import time

import click

from util.logger import initialize_logger
from util.cli_state import common_options, pass_state, State
from util.k8s.kubectl import UserState
from util.helm import delete_user
from util.exceptions import K8sProxyCloseError
from platform_resources.user_utils import purge_user, check_users_presence
from util.k8s.k8s_info import get_config_map_data, patch_config_map_data
from util.aliascmd import AliasCmd
from util.spinner import spinner
from util.system import handle_error
from cli_text_consts import UserDeleteCmdTexts as Texts

logger = initialize_logger(__name__)

USER_DEL_CM = "nauta-user-del"
NAUTA_NAMESPACE = "nauta"


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='d', options_metavar='[options]')
@click.argument("username", nargs=1)
@click.option("-p", "--purge", is_flag=True, help=Texts.HELP_PR)
@common_options(admin_command=True)
@pass_state
def delete(state: State, username: str, purge: bool):
    """
    Deletes a user with a name given as a parameter.

    :param username: name of a user that should be deleted
    :param purge: if set - command removes also all artifacts associated with a user
    """
    try:
        click.echo(Texts.DELETION_CHECK_PRESENCE)
        user_state = check_users_presence(username)

        if user_state == UserState.NOT_EXISTS:
            handle_error(user_msg=Texts.USER_NOT_EXISTS_ERROR_MSG.format(username=username))
            exit(1)

        if user_state == UserState.TERMINATING:
            handle_error(user_msg=Texts.USER_BEING_REMOVED_ERROR_MSG)
            exit(1)

    except Exception:
        handle_error(logger, Texts.USER_PRESENCE_VERIFICATION_ERROR_MSG,
                     Texts.USER_PRESENCE_VERIFICATION_ERROR_MSG, add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo()
    if not click.confirm(Texts.DELETE_CONFIRM_MSG.format(username=username)):
        click.echo(Texts.DELETE_ABORT_MSG)
        exit(0)

    click.echo()

    try:
        click.echo(Texts.DELETION_START_DELETING)
        delete_user(username)

        patch_config_map_data(name=USER_DEL_CM, namespace=NAUTA_NAMESPACE, key=username, value="1")

        if purge:
            try:
                click.echo(Texts.DELETION_START_PURGING)
                # failure during purging a user doesn't mean that user wasn't deleted
                purge_user(username)
            except Exception:
                handle_error(logger, Texts.PURGE_ERROR_MSG, Texts.PURGE_ERROR_MSG)

        # CAN-616 - wait until user has been really deleted
        with spinner(text=Texts.DELETION_VERIFICATION_OF_DELETING) as user_del_spinner:
            for i in range(60):
                    user_state = check_users_presence(username)

                    user_del_cm_content = get_config_map_data(name=USER_DEL_CM, namespace=NAUTA_NAMESPACE,
                                                              request_timeout=1)
                    if (not user_state or user_state == UserState.NOT_EXISTS) and \
                            (not user_del_cm_content or not user_del_cm_content.get(username)):
                        break
                    time.sleep(1)
            else:
                user_del_spinner.stop()
                click.echo()
                click.echo(Texts.DELETE_IN_PROGRESS_MSG)
                exit(0)

        click.echo()
        click.echo(Texts.DELETE_SUCCESS_MSG.format(username=username))
    except K8sProxyCloseError:
        handle_error(logger, Texts.PROXY_ERROR_LOG_MSG, Texts.PROXY_ERROR_USER_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_LOG_MSG, Texts.OTHER_ERROR_USER_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)
