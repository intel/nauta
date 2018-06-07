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

import subprocess
import errno

import pytest

from util.system import execute_system_command, check_port_availability
from util.exceptions import KubectlIntError


def test_execute_system_command(mocker):
    mocker.patch('subprocess.check_output')
    output, exit_code = execute_system_command(['ls'])

    # noinspection PyUnresolvedReferences
    assert subprocess.check_output.call_count == 1


def test_execute_system_command_known_error(mocker):

    bad_exit_code = 1

    # noinspection PyUnusedLocal
    def raise_command_exception(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=bad_exit_code, cmd='ls')

    mocker.patch('subprocess.check_output', new=raise_command_exception)

    output, exit_code = execute_system_command(['ls'])

    assert exit_code == bad_exit_code


def test_execute_system_command_unknown_error(mocker):

    # noinspection PyUnusedLocal
    def raise_command_exception(*args, **kwargs):
        raise subprocess.SubprocessError()

    mocker.patch('subprocess.check_output', new=raise_command_exception)

    with pytest.raises(subprocess.SubprocessError):
        execute_system_command(['ls'])


def test_check_port_availability_success(mocker):
    mocker.patch("socket.socket")
    assert check_port_availability(9000)


def test_check_port_availability_failure(mocker):
    socket_local = mocker.patch("socket.socket.bind")
    socket_local.side_effect = OSError()

    with pytest.raises(KubectlIntError):
        check_port_availability(9000)


def test_check_port_availability_occupied(mocker):
    socket_local = mocker.patch("socket.socket.bind")
    socket_local.side_effect = OSError(errno.EADDRINUSE, "Address in use")

    assert not check_port_availability(9000)
