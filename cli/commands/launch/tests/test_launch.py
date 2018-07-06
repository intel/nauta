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

from http import HTTPStatus
import webbrowser
from unittest.mock import MagicMock

from click.testing import CliRunner
import pytest
import requests

from util import launcher
import commands
from commands.launch import launch
from util.system import get_current_os, OS


APP_NAME = 'webui'
DISABLE_BROWSER_ARG = '--no-launch'


@pytest.fixture
def mocked_k8s_config(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocked_conf_class = mocker.patch('kubernetes.client.configuration.Configuration')
    conf_instance = mocked_conf_class.return_value
    conf_instance.api_key = dict(authorization='fake_token')
    return conf_instance


@pytest.fixture
def mocked_browser_check(mocker):
    browser_check_mock = mocker.patch('util.launcher.is_gui_browser_available')
    browser_check_mock.return_value = True
    return browser_check_mock


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_with_browser_success(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("util.launcher.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyUnboundLocalVariable
        assert socat_mock.start.call_count == 1, "socat wasn't started"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_with_kube_config_loading_success(mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    kube_config_mock = mocker.patch('util.k8s.k8s_info.config.load_kube_config')
    kube_client_mock = mocker.patch('kubernetes.client.configuration.Configuration')
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("util.launcher.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert kube_config_mock.call_count == 1, "kube config wasn't loaded"
    assert kube_client_mock.call_count == 1, "kubernetes api key wasn't read"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyUnboundLocalVariable
        assert socat_mock.start.call_count == 1, "socat wasn't started"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_without_browser_success(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("util.launcher.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME, DISABLE_BROWSER_ARG])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was started"
    assert input_mock.call_count == 1, "enter wasn't prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyUnboundLocalVariable
        assert socat_mock.start.call_count == 1, "socat wasn't started"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_start_tunnel_fail(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("util.launcher.socat")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser wasn started"
    assert input_mock.call_count == 0, "enter was prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyUnboundLocalVariable
        assert socat_mock.start.call_count == 0, "socat was started"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_unsupported_browser(mocked_k8s_config, mocked_browser_check, mocker):
    mocked_browser_check.return_value = False

    spf_mock = mocker.patch("util.launcher.K8sProxy")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("util.launcher.socat")

    runner = CliRunner()
    result = runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was not started"
    assert input_mock.call_count == 0, "enter was prompted"

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        # noinspection PyUnboundLocalVariable
        assert socat_mock.start.call_count == 0, "socat was started"

    assert result.exit_code == 1


def test_is_gui_browser_available(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.return_value = webbrowser.Opera()

    assert launcher.is_gui_browser_available() is True


def test_is_gui_browser_available_text_browser(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.return_value = webbrowser.GenericBrowser(name='')

    assert launcher.is_gui_browser_available() is False


def test_is_gui_browser_available_no_browser(mocker):
    webbrowser_get_mock = mocker.patch('webbrowser.get')
    webbrowser_get_mock.side_effect = webbrowser.Error

    assert launcher.is_gui_browser_available() is False


class K8sProxyMock:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args):
        pass

    tunnel_port = 1234


@pytest.fixture
def launch_tensorboard_command_mock(mocker):
    mocker.patch.object(launch, 'K8sProxy', new=K8sProxyMock)
    mocker.spy(launch, 'K8sProxy')
    mocker.patch.object(launch, 'get_kubectl_current_context_namespace').return_value = "current-namespace"
    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.OK,
                                                           content=b'{ "id": "e017442b-f328-47f9-b79d-36c29d9f5494"}')
    mocker.patch.object(launch, 'sleep')
    mocker.patch('commands.launch.launch.launch_app_with_proxy')


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command(launch_tensorboard_command_mock):
    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert launch.K8sProxy.call_count == 1
    requests.post.assert_called_once_with('http://127.0.0.1:1234/create/some-exp')
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 1
    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_no_sleep_when_conflict(mocker, launch_tensorboard_command_mock):
    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.CONFLICT,
                                                           content=b'{ "id": "e017442b-f328-47f9-b79d-36c29d9f5494"}')

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert launch.K8sProxy.call_count == 1
    requests.post.assert_called_once_with('http://127.0.0.1:1234/create/some-exp')
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 0
    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_bad_response(mocker, launch_tensorboard_command_mock):
    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert result.exit_code == 1


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_failed_request(mocker, launch_tensorboard_command_mock):
    mocker.patch('requests.post').side_effect = requests.ConnectionError

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    requests.post.assert_called_once_with('http://127.0.0.1:1234/create/some-exp')
    assert commands.launch.launch.launch_app_with_proxy.call_count == 0
    assert result.exit_code == 1
