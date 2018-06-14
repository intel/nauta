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
import webbrowser

from click.testing import CliRunner
import pytest

from commands.launch import launch
from util.system import get_current_os, OS

APP_NAME = 'webui'
DISABLE_BROWSER_ARG = '--no-launch'


@pytest.fixture()
def mocked_k8s_config(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocked_conf_class = mocker.patch('kubernetes.client.configuration.Configuration')
    conf_instance = mocked_conf_class.return_value
    conf_instance.api_key = dict(authorization='fake_token')
    return conf_instance


@pytest.fixture()
def mocked_browser_check(mocker):
    browser_check_mock = mocker.patch('commands.launch.launch.is_gui_browser_available')
    browser_check_mock.return_value = True
    return browser_check_mock


def test_launch_webui_with_browser_success(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            side_effect=[(Mock, 1000, 2000)])
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


def test_launch_webui_with_kube_config_loading_success(mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            side_effect=[(Mock, 1000, 2000)])
    kube_config_mock = mocker.patch('util.k8s.k8s_info.config.load_kube_config')
    kube_client_mock = mocker.patch('kubernetes.client.configuration.Configuration')
    wfc_mock = mocker.patch("commands.launch.launch.wait_for_connection")
    browser_mock = mocker.patch("commands.launch.launch.webbrowser.open_new")
    input_mock = mocker.patch("commands.launch.launch.input")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.launch.launch.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert kube_config_mock.call_count == 1, "kube config wasn't loaded"
    assert kube_client_mock.call_count == 1, "kubernetes api key wasn't read"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 1, "socat wasn't started"


def test_launch_webui_without_browser_success(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            side_effect=[(Mock, 1000, 2000)])
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


def test_launch_webui_start_tunnel_fail(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding")
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


def test_launch_webui_unsupported_browser(mocked_k8s_config, mocked_browser_check, mocker):
    mocked_browser_check.return_value = False

    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("commands.launch.launch.wait_for_connection")
    browser_mock = mocker.patch("commands.launch.launch.webbrowser.open_new")
    input_mock = mocker.patch("commands.launch.launch.input")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.launch.launch.socat")

    runner = CliRunner()
    result = runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was not started"
    assert input_mock.call_count == 0, "enter was prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 0, "socat was started"

    assert result.exit_code == 1


def test_is_gui_browser_available(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.return_value = webbrowser.Opera()

    assert launch.is_gui_browser_available() is True


def test_is_gui_browser_available_text_browser(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.return_value = webbrowser.GenericBrowser(name='')

    assert launch.is_gui_browser_available() is False


def test_is_gui_browser_available_no_browser(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.side_effect = webbrowser.Error

    assert launch.is_gui_browser_available() is False
