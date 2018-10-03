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

import platform
import os
from sys import exit

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.k8s.k8s_info import get_current_user, get_users_samba_password, is_current_user_administrator, \
    get_kubectl_host
from util.aliascmd import AliasCmd
from util.system import handle_error
from cli_text_consts import MountCmdTexts as Texts


logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='m')
@common_options()
@pass_state
def mount(state: State):
    try:
        if is_current_user_administrator():
            handle_error(logger, Texts.USER_IS_ADMIN_ERROR_MSG, Texts.USER_IS_ADMIN_ERROR_MSG)
            exit(1)
    except Exception:
        handle_error(logger, Texts.ADMIN_CHECK_ERROR_MSG, Texts.ADMIN_CHECK_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo(Texts.MAIN_MSG)

    try:
        click.echo(get_mount_command())
    except Exception:
        handle_error(logger, Texts.GET_MOUNT_COMMAND_ERROR_MSG, Texts.GET_MOUNT_COMMAND_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)


def get_mount_command() -> str:
    adr = get_kubectl_host(with_port=False)
    usr = get_current_user()
    psw = get_users_samba_password(usr)

    if platform.system() == 'Linux':
        return get_mount_command_linux(usr, psw, adr)
    elif platform.system() == 'Windows':
        return get_mount_command_windows(usr, psw, adr)
    else:  # OSX
        return get_mount_command_osx(usr, psw, adr)


def get_mount_command_linux(usr: str, psw: str, adr: str) -> str:
    usr_id = str(os.getuid())
    return f"sudo mount.cifs -o username={usr},password={psw},rw,uid={usr_id} //{adr}/<DLS4E_FOLDER> <MOUNTPOINT>"


def get_mount_command_windows(usr: str, psw: str, adr: str) -> str:
    return f"net use \\\\{adr}\\<DLS4E_FOLDER> /user:{usr} {psw}"


def get_mount_command_osx(usr: str, psw: str, adr: str) -> str:
    return f"mount_smbfs //'{usr}:{psw}'@{adr}/<DLS4E_FOLDER> <MOUNTPOINT>"
