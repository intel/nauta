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
import re
from sys import exit

import click
from tabulate import tabulate

from util.logger import initialize_logger
from util.cli_state import common_options, pass_state, State
from util.k8s.k8s_info import get_current_user, get_users_samba_password, is_current_user_administrator, \
    get_kubectl_host
from util.aliascmd import AliasGroup, AliasCmd
from util.system import handle_error, execute_system_command
from cli_text_consts import MountCmdTexts as Texts


logger = initialize_logger(__name__)

NAUTA_IDENTITY_STRING = "domain=NAUTA"


class ShareData():
    LINUX_MOUNTS_LIST_HEADERS = ["Username", "Remote location", "Local folder"]
    WIN_MOUNTS_LIST_HEADERS = ["Status", "Local folder", "Remote location", "Network"]

    def __init__(self, remote_share: str = None, local_share: str = None, username: str = None,
                 status: str = None, network: str = None):
        self.remote_share = remote_share
        self.local_share = local_share
        self.username = username
        self.status = status
        self.network = network

    def linux_osx_tabular_format(self):
        return [self.username, self.remote_share, self.local_share]

    def windows_tabular_format(self):
        return [self.status, self.local_share, self.remote_share, self.network]


def is_admin(state: State):
    try:
        return is_current_user_administrator()
    except Exception:
        handle_error(logger, Texts.ADMIN_CHECK_ERROR_MSG, Texts.ADMIN_CHECK_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)


def print_unmount():
    click.echo()
    click.echo(Texts.UNMOUNT_COMMAND_MSG)
    click.echo(get_unmount_command())

    if platform.system() == "Linux":
        click.echo(Texts.UNMOUNT_OPTIONS_MSG)
    elif platform.system() == "Darwin":
        click.echo(Texts.UNMOUNT_OPTIONS_OSX_MSG)


@click.group(short_help=Texts.HELP, help=Texts.HELP, cls=AliasGroup, alias='m', invoke_without_command=True,
             subcommand_metavar='command [options]')
@common_options(admin_command=False)
@pass_state
@click.pass_context
def mount(context, state: State):
    if context.invoked_subcommand is None:

        click.echo(Texts.MAIN_MSG)

        try:
            click.echo(get_mount_command())
        except Exception:
            handle_error(logger, Texts.GET_MOUNT_COMMAND_ERROR_MSG, Texts.GET_MOUNT_COMMAND_ERROR_MSG,
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)

        print_unmount()


def get_unmount_command() -> str:
    if platform.system() == 'Linux':
        return get_unmount_command_linux()
    elif platform.system() == 'Windows':
        return get_unmount_command_windows()
    else:  # OSX
        return get_unmount_command_osx()


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
    return f"sudo mount.cifs -o username={usr},password={psw},rw,uid={usr_id} //{adr}/<NAUTA_FOLDER> <MOUNTPOINT>"


def get_unmount_command_linux() -> str:
    return f"sudo umount <MOUNTPOINT> [-fl]"


def get_mount_command_windows(usr: str, psw: str, adr: str) -> str:
    return f"net use <MOUNTPOINT> \\\\{adr}\\<NAUTA_FOLDER> /user:{usr} {psw}"


def get_unmount_command_windows() -> str:
    return f"net use <MOUNTPOINT> /d"


def get_mount_command_osx(usr: str, psw: str, adr: str) -> str:
    return f"mount_smbfs //'{usr}:{psw}'@{adr}/<NAUTA_FOLDER> <MOUNTPOINT>"


def get_unmount_command_osx() -> str:
    return f"umount <MOUNTPOINT> [-f]"


def get_mounts_linux_osx(username: str = "", is_admin: bool = False, osx: bool = False):
    output, error_code, log_output = execute_system_command("mount")

    if error_code:
        handle_error(logger, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG)
        exit(1)
    host = get_kubectl_host(with_port=False)
    if osx:
        username_string = f"//{username}@"
    else:
        username_string = f"username={username},"

    if osx:
        mnt_regex = "//(.*)@(.*) on (.*) \("
    else:
        mnt_regex = "(.*) on (.*) type"

    ret_list = []

    if output:
        for item in [nauta_item for nauta_item in output.split("\n") if
                     host in nauta_item and (is_admin or username_string in nauta_item)]:
            try:
                mount_data = re.search(mnt_regex, item)
                if osx:
                    username = mount_data.group(1)
                    remote_location = mount_data.group(2)
                    local_folder = mount_data.group(3)
                else:
                    remote_location = mount_data.group(1)
                    local_folder = mount_data.group(2)
                    username = re.search("username=(.*?),", item).group(1)

                ret_list.append(ShareData(remote_share=remote_location, local_share=local_folder, username=username))
            except Exception:
                handle_error(logger, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG)

    ret_list.sort(key=lambda x: x.username, reverse=False)

    click.echo(tabulate([x.linux_osx_tabular_format() for x in ret_list], headers=ShareData.LINUX_MOUNTS_LIST_HEADERS,
                        tablefmt="orgtbl"))


def get_mounts_windows():
    output, error_code, log_output = execute_system_command(["net", "use"])

    if error_code:
        handle_error(logger, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG, Texts.MOUNTS_LIST_COMMAND_ERROR_MSG)
        exit(1)
    host = get_kubectl_host(with_port=False)
    data = output.split("\n")

    start_analyzing = False
    ret_list = []
    first_line = None
    second_line = None

    for item in data:
        if start_analyzing:
            if "The command completed successfully." in item:
                break
            else:
                if not first_line:
                    first_line = item
                elif not second_line:
                    second_line = item

                if first_line and second_line:
                    if host in first_line:
                        split_first_line = first_line.split()
                        status = None
                        remote_location = None
                        if len(split_first_line) == 3:
                            status = split_first_line[0].strip()
                            local_folder = split_first_line[1].strip()
                            remote_location = split_first_line[2].strip()
                        elif len(split_first_line) == 2:
                            status = split_first_line[0].strip()
                            local_folder = ""
                            remote_location = split_first_line[1].strip()
                        network = second_line.strip()
                        if status and remote_location:
                            ret_list.append(ShareData(remote_share=remote_location, local_share=local_folder,
                                                      status=status, network=network))
                    first_line = None
                    second_line = None
        elif "--------" in item:
            start_analyzing = True

    ret_list.sort(key=lambda x: x.remote_share, reverse=False)

    click.echo(tabulate([x.windows_tabular_format() for x in ret_list], headers=ShareData.WIN_MOUNTS_LIST_HEADERS,
                        tablefmt="orgtbl"))


@mount.command(help=Texts.HELP_L, short_help=Texts.HELP_L, cls=AliasCmd, alias='ls', options_metavar='[options]')
@common_options()
@pass_state
def list(state: State):
    username = get_current_user()

    if platform.system() == 'Linux':
        get_mounts_linux_osx(username=username, is_admin=is_admin(state))
    elif platform.system() == 'Windows':
        get_mounts_windows()
    else:  # OSX
        get_mounts_linux_osx(username=username, is_admin=is_admin(state), osx=True)

    print_unmount()
