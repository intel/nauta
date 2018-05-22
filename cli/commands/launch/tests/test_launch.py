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

from unittest.mock import Mock
from click.testing import CliRunner

from commands.launch import launch
from util.system import get_current_os, OS

APP_NAME = 'webui'
DISABLE_BROWSER_ARG = '--no-launch'


def test_launch_with_browser_success(mocker):
    spf_mock = mocker.patch("commands.launch.launch.start_port_forwarding", side_effect=[(Mock, 1000, 2000)])
    wfc_mock = mocker.patch("commands.launch.launch.wait_for_connection")
    browser_mock = mocker.patch("commands.launch.launch.webbrowser.open_new")
    input_mock = mocker.patch("commands.launch.launch.input")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.launch.launch.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 1, "socat wasn't started"


def test_launch_without_browser_success(mocker):
    spf_mock = mocker.patch("commands.launch.launch.start_port_forwarding", side_effect=[(Mock, 1000, 2000)])
    wfc_mock = mocker.patch("commands.launch.launch.wait_for_connection")
    browser_mock = mocker.patch("commands.launch.launch.webbrowser.open_new")
    input_mock = mocker.patch("commands.launch.launch.input")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.launch.launch.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME, DISABLE_BROWSER_ARG])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 1, "socat wasn't started"


def test_launch_start_tunnel_fail(mocker):
    spf_mock = mocker.patch("commands.launch.launch.start_port_forwarding")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("commands.launch.launch.wait_for_connection")
    browser_mock = mocker.patch("commands.launch.launch.webbrowser.open_new")
    input_mock = mocker.patch("commands.launch.launch.input")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.launch.launch.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser wasn started"
    assert input_mock.call_count == 0, "enter was prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 0, "socat was started"
