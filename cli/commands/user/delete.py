#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

from sys import exit
import time

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.k8s.kubectl import check_users_presence, UserState
from util.helm import delete_user
from util.exceptions import K8sProxyCloseError
from platform_resources.users import purge_user
from util.k8s.k8s_info import is_current_user_administrator, get_config_map_data, patch_config_map_data
from util.aliascmd import AliasCmd
from util.spinner import spinner
from util.system import handle_error
from cli_text_consts import UserDeleteCmdTexts as Texts

logger = initialize_logger(__name__)

USER_DEL_CM = "dls4enterprise-user-del"
DLS4E_NAMESPACE = "dls4e"


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='d', options_metavar='[options]')
@click.argument("username", nargs=1)
@click.option("-p", "--purge", is_flag=True, help=Texts.HELP_PR)
@common_options()
@pass_state
def delete(state: State, username: str, purge: bool):
    """
    Deletes a user with a name given as a parameter.

    :param username: name of a user that should be deleted
    :param purge: if set - command removes also all artifacts associated with a user
    """
    try:
        if not is_current_user_administrator():
            handle_error(user_msg=Texts.USER_NOT_ADMIN_ERROR_MSG)
            exit(1)
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

        patch_config_map_data(name=USER_DEL_CM, namespace=DLS4E_NAMESPACE, key=username, value="1")

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

                    user_del_cm_content = get_config_map_data(name=USER_DEL_CM, namespace=DLS4E_NAMESPACE,
                                                              request_timeout=1)
                    if (not user_state or user_state == UserState.NOT_EXISTS) and \
                            (not user_del_cm_content or not user_del_cm_content.get(username)):
                        break
                    time.sleep(1)
            else:
                user_del_spinner.hide()
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
