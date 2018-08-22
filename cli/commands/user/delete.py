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

import sys
import time

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.k8s.kubectl import check_users_presence, UserState
from util.helm import delete_user
from util.exceptions import K8sProxyCloseError
from platform_resources.users import purge_user
from util.k8s.k8s_info import is_current_user_administrator
from util.aliascmd import AliasCmd
from util.system import handle_error
from cli_text_consts import USER_DELETE_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='d')
@click.argument("username", nargs=1)
@click.option("-p", "--purge", is_flag=True, help=TEXTS["help_pr"])
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
            handle_error(user_msg=TEXTS["user_not_admin_error_msg"])

        user_state = check_users_presence(username)

        if user_state == UserState.NOT_EXISTS:
            handle_error(user_msg=TEXTS["user_not_exists_error_msg"].format(username=username))

        if user_state == UserState.TERMINATING:
            handle_error(user_msg=TEXTS["user_being_removed"])

    except Exception:
        handle_error(logger, TEXTS["user_presence_verification_error_msg"],
                     TEXTS["user_presence_verification_error_msg"], add_verbosity_msg=state.verbosity == 0)

    if not click.confirm(TEXTS["delete_confirm_msg"].format(username=username),):
        click.echo(TEXTS["delete_abort_msg"])
        sys.exit(0)

    try:
        delete_user(username)

        if purge:
            try:
                # failure during purging a user doesn't mean that user wasn't deleted
                purge_user(username)
            except Exception:
                handle_error(logger, TEXTS["purge_error_msg"], TEXTS["purge_error_msg"], exit_code=None)

        # CAN-616 - wait until user has been really deleted
        for i in range(30):
            if not check_users_presence(username):
                break

            time.sleep(1)
        else:
            click.echo(TEXTS["delete_in_progress_msg"])
            sys.exit(0)

        click.echo(TEXTS["delete_success_msg"].format(username=username))
    except K8sProxyCloseError:
        handle_error(logger, TEXTS["proxy_error_log_msg"], TEXTS["proxy_error_user_msg"], exit_code=None,
                     add_verbosity_msg=state.verbosity == 0)
    except Exception:
        handle_error(logger, TEXTS["other_error_log_msg"], TEXTS["other_error_user_msg"],
                     add_verbosity_msg=state.verbosity == 0)
