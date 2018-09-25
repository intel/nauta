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

import logging
import time
from enum import Enum
import subprocess
import sys
from typing import List, Tuple
import errno
import socket
import dateutil
import signal
import platform
from distutils.version import LooseVersion
import click
import distro

from util.exceptions import KubectlIntError
from util.logger import initialize_logger, get_verbosity_level
from cli_text_consts import UTIL_SYSTEM_TEXTS as TEXTS, VERBOSE_RERUN_MSG


log = initialize_logger('util.system')

WINDOWS_EDITIONS = {
    0: "undefined",
    1: "ultimate",
    2: "home_basic",
    3: "home_premium",
    4: "enterprise",
    5: "home_basic_n",
    6: "business",
    7: "standard_server",
    8: "datacenter_server",
    9: "small_business_server",
    10: "enterprise_server",
    11: "starter",
    12: "datacenter_server_core",
    13: "standard_server_core",
    14: "enterprise_server_core",
    15: "enterprise_server_for_itanium_based_systems",
    16: "business_n",
    17: "web_server",
    18: "cluster_server",
    19: "home_server",
    20: "storage_express_server",
    21: "storage_standard_server",
    22: "storage_workgroup_server",
    23: "storage_enterprise_server",
    24: "server_for_small_business",
    25: "small_business_server_premium",
    29: "web_server_server_core",
    39: "datacenter_edition_without_hyperv_server_core",
    40: "standard_edition_without_hyperv_server_core",
    41: "enterprise_edition_without_hyperv_server_core",
    42: "hyperv_server",
    48: "pro"
}


def execute_system_command(command: List[str], timeout: int or None = None,
                           stdin=None, env=None, cwd=None) -> (str, int):
    try:
        output = subprocess.check_output(command, timeout=timeout, stderr=subprocess.STDOUT, universal_newlines=True,
                                         stdin=stdin, env=env, cwd=cwd, encoding='utf-8')
        log.debug(f'COMMAND: {command} RESULT: {output}'.replace('\n', '\\n'))
    except subprocess.CalledProcessError as ex:
        return ex.output, ex.returncode
    else:
        return output, 0


def execute_subprocess_command(command: List[str], timeout: int or None = 1, stdin=None, env=None,
                               cwd=None, shell=False, join=False) -> subprocess.Popen:

    # if a log level is set to DEBUG - additional information from creation of a proxy are sent to console
    std_output_destination = None if get_verbosity_level == logging.DEBUG else subprocess.DEVNULL
    std_error_destination = subprocess.STDOUT if get_verbosity_level == logging.DEBUG else subprocess.DEVNULL

    if join:
        final_command = ' '.join(command)
    else:
        final_command = command

    log.debug(f'executing COMMAND in subprocess: {final_command}')
    process = subprocess.Popen(args=final_command, stdout=std_output_destination, stderr=std_error_destination,
                               universal_newlines=True, stdin=stdin, env=env, cwd=cwd, encoding='utf-8',
                               shell=shell)

    # wait for command execution initialization
    time.sleep(timeout)

    if not process or process.poll() != (0 or None):
        log.error(f'COMMAND execution FAIL: {command}')
        raise RuntimeError(TEXTS["command_exe_fail_error_msg"].format(command=command))
    return process


class OS(Enum):
    WINDOWS = "win"
    MACOS = "darwin"
    LINUX = "linux"

    @classmethod
    def all_str(cls):
        return ''.join([e.value for e in cls])


def get_current_os() -> OS:
    sys_platform = sys.platform  # type: str
    if sys_platform.startswith(OS.WINDOWS.value):
        return OS.WINDOWS
    elif sys_platform.startswith(OS.LINUX.value):
        return OS.LINUX
    elif sys_platform.startswith(OS.MACOS.value):
        return OS.MACOS

    raise RuntimeError(TEXTS["unsupported_platform_error_msg"]
                       .format(sys_platform=sys_platform, supported_os=OS.all_str()))


def check_port_availability(port: int) -> bool:
    """
    Checks whether a port given as a parameter is available for application.

    :param port: port to be checked
    :return: True if port is available, False - otherwise
    In case of any problems it throws an excpetion
    """
    ret_value = True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            log.debug(f"Port {port} is occupied.")
            ret_value = False
        else:
            # something else raised the socket.error exception
            error_msg = TEXTS["port_availability_check_error_msg"]
            log.exception(error_msg)
            raise KubectlIntError(error_msg) from e

    return ret_value


def format_timestamp_for_cli(timestamp: str) -> str:
    """
    Change timestamp from e.g. "2018-10-11T20:20:30Z" to "2018-10-11 21:20:30" (assuming that local timezone is +01:00).

    :param timestamp: timestamp which will be converted
    :return: formatted version of the timestamp
    """
    cli_timestamp = dateutil.parser.parse(timestamp).astimezone(dateutil.tz.tzlocal()).strftime("%Y-%m-%d %H:%M:%S")
    return cli_timestamp


def wait_for_ctrl_c():
    """ Waits for pressing Ctrl-C key by a user. If Ctrl-C key has been pressed - finishes execution """
    continue_loop = True

    def signal_handler(signal, frame):
        nonlocal continue_loop
        continue_loop = False

    signal.signal(signal.SIGINT, signal_handler)
    while continue_loop:
        time.sleep(0.1)


def handle_error(logger=None, log_msg: str = None, user_msg: str = None, add_verbosity_msg: bool = False):
    """
    Handle error in cli. Log message may be printed. User message may be printed or not, with or without verbosity
    usage info. Execution may end with an exit code. Each combination of these 3 possibilities is achievable by
    specifying correct arguments. Default behaviour is exit with code 1, log nothing and print nothing.

    :param logger: logger which will handle log message. If None, then no message is logged.
    :param log_msg: message to be shown in log. If None, then no message is logged.
    :param user_msg: message to be shown to the user. If None, then no message is shown.
    :param add_verbosity_msg: whether to add information about -v usage or not.
    :return:
    """
    if logger is not None and log_msg is not None:
        logger.exception(log_msg)
    # Internationalization can be plugged in here.
    if user_msg is not None:
        click.echo(user_msg + (" " + VERBOSE_RERUN_MSG if add_verbosity_msg else ""))


def get_windows_edition():
    windows_edition_number, _ = execute_system_command(
        ["powershell.exe", "(Get-WmiObject Win32_OperatingSystem).OperatingSystemSKU"])
    return WINDOWS_EDITIONS[int(windows_edition_number)]


def get_os_version() -> Tuple[str, LooseVersion]:
    system_str = platform.system()
    if system_str == "Darwin":
        return "macos", LooseVersion(platform.mac_ver()[0])
    elif system_str == "Windows":
        if LooseVersion(platform.release()) >= LooseVersion("10"):
            return "windows" + "_" + get_windows_edition(), LooseVersion(platform.release())
        else:
            return "windows", LooseVersion(platform.release())
    elif system_str == "Linux":
        os_info = distro.info()
        return os_info["id"], LooseVersion(os_info["version"])
    return "", LooseVersion("0")
