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

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.k8s.kubectl import check_users_presence
from util.helm import delete_user
from util.k8s.k8s_proxy_context_manager import K8sProxyCloseError
from platform_resources.users import purge_user
log = initialize_logger(__name__)

HELP = "Command used to delete a user from the platform. Can be only " \
       "run by a platform administrator."
HELP_PR = "If this option is added - command removes all client's artifacts."


@click.command(help=HELP)
@click.argument("username", nargs=1)
@click.option("-p", "--purge", is_flag=True, help=HELP_PR)
@common_options
@pass_state
def delete(state: State, username: str, purge: bool):
    """
    Deletes a user with a name given as a parameter.

    :param username: name of a user that should be deleted
    :param purge: if set - command removes also all artifacts associated with a user
    """
    try:
        if not check_users_presence(username):
            click.echo(f"User {username} doesn't exists.")
            sys.exit(1)
    except Exception:
        err_msg = "Problems during verifying users presence."
        log.exception(err_msg)
        click.echo(err_msg)
        sys.exit(1)

    if not click.confirm(f"User {username} is about to be deleted. Do you want to continue?",):
        click.echo("Operation of deleting of a user was aborted.")
        sys.exit(0)

    try:
        delete_user(username)

        click.echo(f"User {username} has been deleted.")

        if purge and not purge_user(username):
            click.echo("Some artifacts belonging to a user weren't removed.")
    except K8sProxyCloseError:
        log.exception("Error during closing of a proxy for elasticsearch.")
        click.echo("Elasticsearch proxy hasn't been closed properly. "
                   "Check whether it still exists, if yes - close it manually.")
    except Exception:
        log.exception("Error during deleting a user of a user.")
        click.echo("User hasn't been deleted due to technical reasons. To get more information about causes "
                   "of a problem - run command with -v option.")
        sys.exit(1)
