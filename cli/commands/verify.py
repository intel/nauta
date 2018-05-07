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

import os
import sys

import click

from cli_state import common_options, pass_state, State
from draft import dependencies_checker
from util.logger import initialize_logger
from util.config import DLS_CTL_CONFIG_DIR_NAME, DLS_CTL_CONFIG_ENV_NAME


HELP = "Command used to verify whether all external components required by dlsctl are installed " \
       "in proper versions. If something is missing - application displays a detailed information" \
       " about it."

log = initialize_logger('commands.verify')


@click.command(help=HELP)
@common_options
@pass_state
def verify(state: State):
    dependencies_checker.check()


def validate_config_path() -> str:
    binary_config_dir_path = os.path.join(os.path.dirname(sys.executable), DLS_CTL_CONFIG_DIR_NAME)
    user_local_config_dir_path = os.path.join(os.path.expanduser('~'), DLS_CTL_CONFIG_DIR_NAME)

    log.debug(f"{DLS_CTL_CONFIG_DIR_NAME} binary executable path:  {binary_config_dir_path}")
    log.debug(f'{DLS_CTL_CONFIG_DIR_NAME} user home path:  {binary_config_dir_path}')

    if DLS_CTL_CONFIG_ENV_NAME in os.environ and os.environ.get(DLS_CTL_CONFIG_ENV_NAME):
        user_path = os.environ.get(DLS_CTL_CONFIG_ENV_NAME)
        if os.path.exists(user_path):
            return user_path
        else:
            message = f'can not find {user_path} directory from {DLS_CTL_CONFIG_ENV_NAME} env!'
            log.exception(message)
            click.echo(message)
            sys.exit(1)
    elif user_local_config_dir_path and os.path.exists(user_local_config_dir_path):
        return user_local_config_dir_path
    elif binary_config_dir_path and os.path.exists(binary_config_dir_path):
        return binary_config_dir_path
    else:
        message = f'can not find {DLS_CTL_CONFIG_DIR_NAME} directory in {binary_config_dir_path} and ' \
                  f'{user_local_config_dir_path}. Use {DLS_CTL_CONFIG_ENV_NAME} env to point ' \
                  f'{DLS_CTL_CONFIG_DIR_NAME} directory location'
        log.exception(message)
        click.echo(message)
        sys.exit(1)
