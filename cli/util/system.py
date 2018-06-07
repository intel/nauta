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
from typing import List
import errno
import socket

from util.exceptions import KubectlIntError
from util.logger import initialize_logger


log = initialize_logger('util.system')


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
                               cwd=None) -> subprocess.Popen:

    # if a log level is set to DEBUG - additional information from creation of a proxy are sent to console
    std_output_destination = None if log.getEffectiveLevel() == logging.DEBUG else subprocess.DEVNULL
    std_error_destination = subprocess.STDOUT if log.getEffectiveLevel() == logging.DEBUG else subprocess.DEVNULL

    log.debug(f'executing COMMAND in subprocess: {command}')
    process = subprocess.Popen(args=command, stdout=std_output_destination, stderr=std_error_destination,
                               universal_newlines=True, stdin=stdin, env=env, cwd=cwd, encoding='utf-8')

    # wait for command execution initialization
    time.sleep(timeout)

    if not process or process.poll() != (0 or None):
        log.error(f'COMMAND execution FAIL: {command}')
        raise RuntimeError(f'COMMAND execution FAIL: {command}')
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

    raise RuntimeError(f'unsupported platform: {sys_platform}, supported: {OS.all_str()}!')


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
            error_msg = "Problem during checking port's availability."
            log.exception(error_msg)
            raise KubectlIntError(error_msg) from e

    return ret_value
