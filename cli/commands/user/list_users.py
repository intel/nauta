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
from tabulate import tabulate

from cli_state import common_options, pass_state, State
import platform_resources.users as users_api
from util.aliascmd import AliasCmd
from util.logger import initialize_logger

logger = initialize_logger(__name__)


@click.command(name='list', cls=AliasCmd, alias='ls')
@common_options()
@pass_state
def list_users(state: State):
    """
    List users.
    """
    try:
        users = users_api.list_users()
        click.echo(tabulate([user.cli_representation for user in users],
                            headers=['Name', 'Creation date', 'Date of last submitted job',
                                     'Number of running jobs', 'Number of queued jobs'],
                            tablefmt="orgtbl"))
    except Exception:
        error_msg = 'Failed to get users list.'
        logger.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)
