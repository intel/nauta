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

import click

from commands.user.create import create
from commands.user.delete import delete
from commands.user.list_users import list_users
from util.aliascmd import AliasGroup
from util.logger import initialize_logger

log = initialize_logger(__name__)

HELP = "Command for creating/deleting/listing users of the platform. Can only be " \
       "run by a platform administrator."


@click.group(short_help=HELP, cls=AliasGroup, alias='u')
def user():
    pass


user.add_command(create)
user.add_command(list_users)
user.add_command(delete)
