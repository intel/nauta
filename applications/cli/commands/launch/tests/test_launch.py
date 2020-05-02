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

from http import HTTPStatus
import webbrowser

from click.testing import CliRunner
import pytest

import commands
from commands.launch import launch
from tensorboard.client import Tensorboard, TensorboardStatus, TensorboardServiceAPIException
from util import launcher
from cli_text_consts import LaunchCmdTexts as Texts


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

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_with_kube_config_loading_success(mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    kube_config_mock = mocker.patch('util.k8s.k8s_info.config.load_kube_config')
    kube_client_mock = mocker.patch('kubernetes.client.configuration.Configuration')
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert kube_config_mock.call_count == 1, "kube config wasn't loaded"
    assert kube_client_mock.call_count == 1, "kubernetes api key wasn't read"
    assert wfc_mock.call_count == 1, "connection wasn't checked"
    assert browser_mock.call_count == 1, "browser wasn't started"
    assert input_mock.call_count == 1, "enter wasn't prompted"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_without_browser_success(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME, DISABLE_BROWSER_ARG])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was started"
    assert input_mock.call_count == 1, "enter wasn't prompted"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_start_tunnel_fail(mocked_k8s_config, mocked_browser_check, mocker):
    spf_mock = mocker.patch("util.launcher.K8sProxy")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    runner = CliRunner()
    runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser wasn started"
    assert input_mock.call_count == 0, "enter was prompted"


# noinspection PyUnusedLocal,PyShadowingNames
def test_launch_webui_unsupported_browser(mocked_k8s_config, mocked_browser_check, mocker):
    mocked_browser_check.return_value = False

    spf_mock = mocker.patch("util.launcher.K8sProxy")
    spf_mock.return_value = 0
    wfc_mock = mocker.patch("util.launcher.wait_for_connection")
    browser_mock = mocker.patch("util.launcher.webbrowser.open_new")
    input_mock = mocker.patch("util.launcher.wait_for_ctrl_c")

    runner = CliRunner()
    result = runner.invoke(launch.launch, [APP_NAME])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert wfc_mock.call_count == 0, "connection was checked"
    assert browser_mock.call_count == 0, "browser was not started"
    assert input_mock.call_count == 0, "enter was prompted"

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

    mocker.patch.object(launch, 'sleep')
    mocker.patch('commands.launch.launch.launch_app_with_proxy')


FAKE_TENSORBOARD_ID = 'd846ed7d-3d17-4c65-9430-40729b27afec'
FAKE_CREATING_TENSORBOARD = Tensorboard(
    id=FAKE_TENSORBOARD_ID,
    status=TensorboardStatus.CREATING,
    url=f'/tb/{FAKE_TENSORBOARD_ID}/',
    invalid_runs=[]
)
FAKE_RUNNING_TENSORBOARD = Tensorboard(
    id=FAKE_TENSORBOARD_ID,
    status=TensorboardStatus.RUNNING,
    url=f'/tb/{FAKE_TENSORBOARD_ID}/',
    invalid_runs=[]
)
FAKE_INVALID_RUNS = [{'name': 'fake_name', 'owner': 'fake_owner'}]


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    mocker.patch('tensorboard.client.TensorboardServiceClient.get_tensorboard').return_value = FAKE_RUNNING_TENSORBOARD

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert launch.K8sProxy.call_count == 1
    assert launch.TensorboardServiceClient.get_tensorboard.call_count == 1
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 0
    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_retries(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    get_tensorboard_side_effect = [FAKE_CREATING_TENSORBOARD for _ in range(3)]
    get_tensorboard_side_effect.append(FAKE_RUNNING_TENSORBOARD)

    mocker.patch('tensorboard.client.TensorboardServiceClient.get_tensorboard').side_effect = \
        get_tensorboard_side_effect

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert launch.K8sProxy.call_count == 1
    assert launch.TensorboardServiceClient.get_tensorboard.call_count == 4
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 3
    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_too_many_retries(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    mocker.patch('tensorboard.client.TensorboardServiceClient.get_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert launch.K8sProxy.call_count == 1
    assert launch.TensorboardServiceClient.get_tensorboard.call_count == launch.TENSORBOARD_TRIES_COUNT
    assert commands.launch.launch.launch_app_with_proxy.call_count == 0
    assert launch.sleep.call_count == launch.TENSORBOARD_TRIES_COUNT
    assert result.exit_code == 2


# noinspection PyUnusedLocal,PyShadowingNames
def test_tensorboard_command_create_exception(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').side_effect = \
        TensorboardServiceAPIException(error_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, message='error')

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert result.exit_code == 1


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_many_experiments(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    mocker.patch('tensorboard.client.TensorboardServiceClient.get_tensorboard').return_value = FAKE_RUNNING_TENSORBOARD

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp', 'another-exp', 'next-exp'])

    assert launch.K8sProxy.call_count == 1
    assert launch.TensorboardServiceClient.get_tensorboard.call_count == 1
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 0
    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyShadowingNames
def test_tensorboard_command_missing_experiment(mocker, launch_tensorboard_command_mock):
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').side_effect = \
        TensorboardServiceAPIException(error_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
                                       message='There is no data for the following experiments :')

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp'])

    assert result.exit_code == 1
    assert 'There is no data for the following experiments' in result.output


# noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
def test_tensorboard_command_many_experiments_some_nonexisting(mocker, launch_tensorboard_command_mock):
    FAKE_CREATING_TENSORBOARD.invalid_runs = FAKE_INVALID_RUNS
    mocker.patch('tensorboard.client.TensorboardServiceClient.create_tensorboard').return_value = \
        FAKE_CREATING_TENSORBOARD

    mocker.patch('tensorboard.client.TensorboardServiceClient.get_tensorboard').return_value = FAKE_RUNNING_TENSORBOARD

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['tensorboard', 'some-exp', 'another-exp', 'next-exp'])

    assert launch.K8sProxy.call_count == 1
    assert launch.TensorboardServiceClient.get_tensorboard.call_count == 1
    assert commands.launch.launch.launch_app_with_proxy.call_count == 1
    assert launch.sleep.call_count == 0
    assert result.exit_code == 0
    assert Texts.TB_INVALID_RUNS_MSG.format(
        invalid_runs=", ".join(f'{item.get("owner")}/{item.get("name")}' for item in FAKE_INVALID_RUNS)
    ) in result.output
