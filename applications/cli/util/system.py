#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
from enum import Enum
import os
import subprocess
import sys
from typing import List, Tuple
import errno
import socket
import dateutil.tz
import dateutil.parser
from datetime import timedelta
import signal
import platform
from distutils.version import LooseVersion
import click
import distro

from util.logger import initialize_logger
from cli_text_consts import UtilSystemTexts as Texts, VERBOSE_RERUN_MSG

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


class ExternalCliCommand:
    def __init__(self, cmd: List[str], env: dict = None, cwd: str = None, timeout: int = None):
        """
        :param cmd: List of strings which define a command that will be executed, e.g. ['git', 'clone']
        :param env: Dictionary containing environment variables that will be used during command execution
        :param cwd: Path to working directory
        :param timeout: Timeout in seconds
        """
        self.cmd = cmd
        self.env = env
        self.cwd = cwd
        self.timeout = timeout

    def __call__(self, *args, **kwargs) -> Tuple[str, int, str]:
        """
        Call command.
        :param args: Positional arguments will be passed unchanged to the executed command
        :param kwargs: Keyword arguments will be passed as long parameters, e.g. passing `foo=bar` will add
         `--foo`, 'bar' to the executed command. If keyword argument has binary value, it will be treated as a flag,
         e.g. passing `foo=True` argument will add `--foo` to the executed command and passing `foo=False` will not add
         anything new to the command. Underscores in keyword argument names will be replaced with hyphens
        :return: output, exit code and formatted output of called command
        """
        cmd = self.cmd
        env = kwargs.get('_env') or self.env
        cwd = kwargs.get('_cwd') or self.cwd
        for arg in args:
            cmd.append(arg)
        for kwarg_name, kwarg_value in kwargs.items():
            if not kwarg_name.startswith('_'):  # kwargs that have name starting with '_' are reserved
                option_name = kwarg_name.replace('_', '-')
                if kwarg_value is False:  # Handle flags
                    continue
                elif kwarg_value is True:
                    cmd.append(f'--{option_name}')
                else:  # Standard options
                    cmd.append(f'--{option_name}')
                    cmd.append(kwarg_value)
        output, exit_code, log_output = execute_system_command(command=cmd, env=env, cwd=cwd, timeout=self.timeout)
        if exit_code != 0:
            log.error(log_output)
            raise RuntimeError(f'Failed to execute command: {self.cmd}')
        else:
            return output, exit_code, log_output


class ExternalCliClient:
    """
    This class allows to easily create a wrapper for external CLI. Usage example:
      git_client = ExternalCliClient('git')
      git_client.clone('https://repo.git', quiet=True)
      git_client.add('-u')
      git_client.commit(message='test')
    """
    def __init__(self, executable: str, env: dict = None, cwd: str = None, timeout: int = None):
        """
        :param executable: Name of external CLI executable e.g. 'git' or 'helm'
        :param env: Dictionary containing environment variables that will be used by the client
        :param cwd: Path to working directory
        :param timeout: Timeout in seconds for commands executed by the client
        """
        self.executable = executable
        self.env = env
        self.cwd = cwd
        self.timeout = timeout

    def __getattr__(self, item):
        return self._make_command(item)

    def _make_command(self, name: str):
        return ExternalCliCommand(env=self.env, cwd=self.cwd, cmd=[self.executable, name], timeout=self.timeout)


def execute_system_command(command: List[str],
                           timeout: int = None,
                           stdin=None,
                           env=None,
                           cwd=None,
                           logs_size: int = 0) -> Tuple[str, int, str]:
    """
    Executes system's command
    :param command: command to be exeucted
    :param timeout: timeout of execution, when timeout pass - command is interrupted
    :param stdin: stream with input data for command
    :param env: environment within which command is run
    :param cwd: command working directory
    :param logs_size: if other than 0 - system sends to logger logs_size last characters
    :return: output - output of the command
             exit_code - exit code returned by a command
             log_output - output that should be passed to logs. If a real output contains
             special characters that are not present in a current system's encoding, this
             attribute contains information about a need of changing system's encoding
    """
    try:
        output = subprocess.check_output(  # type: ignore
            command,
            timeout=timeout,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            stdin=stdin,
            env=env,
            cwd=cwd,
            encoding='utf-8')
        encoded_output = output[-logs_size:].encode('utf-8')
        log.debug(f'COMMAND: {command} RESULT: {encoded_output}'.replace('\n', '\\n'))
    except subprocess.CalledProcessError as ex:
        log.exception(f'COMMAND: {command} RESULT: {ex.output}'.replace('\n', '\\n'))
        return ex.output, ex.returncode, ex.output
    else:
        return output, 0, encoded_output


def execute_subprocess_command(command: List[str],
                               stdin=None,
                               env=None,
                               cwd=None,
                               shell=False) -> subprocess.Popen:

    log.debug(f'executing COMMAND in subprocess: {str(command)}')
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        stdin=stdin,
        env=env,
        cwd=cwd,
        encoding='utf-8',
        shell=shell)

    if process.poll() is not None:
        log.error(f'{command} execution FAIL: {command}')
        out, err = process.communicate()
        log.error(f'{command} stdout: {out}')
        log.error(f'{command} stderr: {err}')
        raise RuntimeError(
            Texts.COMMAND_EXE_FAIL_ERROR_MSG.format(command=command))
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

    raise RuntimeError(
        Texts.UNSUPPORTED_PLATFORM_ERROR_MSG.format(
            sys_platform=sys_platform, supported_os=OS.all_str()))


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
            error_msg = Texts.PORT_AVAILABILITY_CHECK_ERROR_MSG
            log.exception(error_msg)
            raise RuntimeError(error_msg) from e

    return ret_value


def format_timestamp_for_cli(timestamp: str) -> str:
    """
    Change timestamp from e.g. "2018-10-11T20:20:30Z" to "2018-10-11 9:20:30 PM"
    (assuming that local timezone is +01:00).

    :param timestamp: timestamp which will be converted
    :return: formatted version of the timestamp
    """
    cli_timestamp = dateutil.parser.parse(timestamp).astimezone(
        dateutil.tz.tzlocal()).strftime("%Y-%m-%d %I:%M:%S %p")
    return cli_timestamp


def format_duration_for_cli(timedelta: timedelta) -> str:
    days = timedelta.days
    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{}d {}h {}m {}s'.format(days, hours, minutes, seconds)


def wait_for_ctrl_c():
    """ Waits for pressing Ctrl-C key by a user. If Ctrl-C key has been pressed - finishes execution """
    continue_loop = True

    def signal_handler(signal, frame):
        nonlocal continue_loop
        continue_loop = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if get_current_os() in (OS.LINUX, OS.MACOS):
        os.system("setterm --cursor on")

    while continue_loop:
        time.sleep(0.1)


def handle_error(logger=None,
                 log_msg: str = None,
                 user_msg: str = None,
                 add_verbosity_msg: bool = False):
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
        click.echo(user_msg +
                   (" " + VERBOSE_RERUN_MSG if add_verbosity_msg else ""))


def get_windows_edition():
    windows_edition_number, _, _ = execute_system_command([
        "powershell.exe",
        "(Get-WmiObject Win32_OperatingSystem).OperatingSystemSKU"
    ])
    return WINDOWS_EDITIONS[int(windows_edition_number)]


def get_os_version() -> Tuple[str, LooseVersion]:
    system_str = platform.system()
    if system_str == "Darwin":
        return "macos", LooseVersion(platform.mac_ver()[0])
    elif system_str == "Windows":
        if LooseVersion(platform.release()) >= LooseVersion("10"):
            return "windows" + "_" + get_windows_edition(), LooseVersion(
                platform.release())
        else:
            return "windows", LooseVersion(platform.release())
    elif system_str == "Linux":
        os_info = distro.info()
        return os_info["id"], LooseVersion(os_info["version"])
    return "", LooseVersion("0")
