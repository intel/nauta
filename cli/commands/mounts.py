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
import sys

import click

from util.logger import initialize_logger
from cli_state import common_options, pass_state, State
from util.k8s.k8s_info import get_current_user, get_users_samba_password, is_current_user_administrator
from util.config import DLS4EConfigMap
from util.aliascmd import AliasCmd

log = initialize_logger(__name__)

HELP = "Command displays a command that should be used to mount client's" \
       " folders on his/her local machine."


MOUNT_MESSAGE = '''
Use the following command to mount those folders:
 - replace <MOUNTPOINT> with a proper location on your local machine)
 - replace <DLS4E_FOLDER> with one of the following:
        - input - user's private input folder (read/write)
          (can be accessed as /mnt/input/home from training script)
        - output - user's private output folder (read)
          (can be accessed as /mnt/output/home from training script)
        - input-shared - shared input folder (read/write)
          (can be accessed as /mnt/input/root/public from training script)
        - output-shared - shared output folder (read)
          (can be accessed as /mnt/output/root/public from training script)
Additionally each experiment has a special folder which can be accessed
as /mnt/output/experiment from training script. This folder is shared by Samba
as output/<EXPERIMENT_NAME>.
--------------------------------------------------------------------
'''


@click.command(help=HELP, cls=AliasCmd, alias='m')
@common_options()
@pass_state
def mounts(state: State):
    try:
        if is_current_user_administrator():
            click.echo("DLS4E doesn't create shares for administrators. Please execute this command as "
                       "a regular user.")
            sys.exit(1)
    except Exception:
        error_msg = "Problems during verifying whether current user is an administrator."
        log.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)

    click.echo(MOUNT_MESSAGE)
    click.echo(get_mount_command())


def get_mount_command() -> str:
    try:
        dls4e_config_map = DLS4EConfigMap()
        adr = dls4e_config_map.external_ip
        usr = get_current_user()
        psw = get_users_samba_password(usr)

        if platform.system() == 'Linux':
            return get_mount_command_linux(usr, psw, adr)
        elif platform.system() == 'Windows':
            return get_mount_command_windows(usr, psw, adr)
        else:  # OSX
            return get_mount_command_osx(usr, psw, adr)
    except Exception:
        error_msg = "Error during gathering data needed for mounting samba share."
        log.exception(error_msg)
        click.echo(error_msg)


def get_mount_command_linux(usr: str, psw: str, adr: str) -> str:
    usr_id = str(os.getuid())
    return f"sudo mount.cifs -o username={usr},password={psw},rw,uid={usr_id} //{adr}/<DLS4E_FOLDER> <MOUNTPOINT>"


def get_mount_command_windows(usr: str, psw: str, adr: str) -> str:
    return f"net use \\\\{adr}\\<DLS4E_FOLDER> /user:{usr} {psw}"


def get_mount_command_osx(usr: str, psw: str, adr: str) -> str:
    return f"mount_smbfs //'{usr}:{psw}'@{adr}/<DLS4E_FOLDER> <MOUNTPOINT>"
