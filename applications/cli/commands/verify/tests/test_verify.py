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

from distutils.version import LooseVersion

from click.testing import CliRunner
import pytest

from commands.verify import verify
from util.exceptions import KubectlConnectionError
from cli_text_consts import VerifyCmdTexts as Texts


@pytest.fixture(autouse=True)
def mock_kubectl_calls(mocker):
    mocker.patch("commands.verify.verify.get_kubectl_current_context_namespace")
    mocker.patch("commands.verify.verify.is_current_user_administrator")


def test_verify_with_kubectl_connection_error(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_connection_mock.side_effect = KubectlConnectionError("Cannot connect to K8S cluster")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    mocker.patch.object(verify, "save_dependency_versions")
    mocker.patch.object(verify, "check_os")

    runner = CliRunner()
    result = runner.invoke(verify.verify, [])

    assert check_dependency_mock.call_count == 1
    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    # noinspection PyUnresolvedReferences
    assert verify.save_dependency_versions.call_count == 0

    assert "Cannot connect to K8S cluster" in result.output, \
        "Bad output. Connection error should be indicated in console output."


def test_verify_with_kubectl_not_found_error(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_connection_mock.side_effect = FileNotFoundError
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    mocker.patch.object(verify, "check_os")
    mocker.patch.object(verify, "save_dependency_versions")

    runner = CliRunner()
    result = runner.invoke(verify.verify, [])

    assert check_dependency_mock.call_count == 1, "dependency wasn't checked"
    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    # noinspection PyUnresolvedReferences
    assert verify.save_dependency_versions.call_count == 0

    assert Texts.KUBECTL_NOT_INSTALLED_ERROR_MSG in result.output, \
        "Bad output. FileNotFoundError indicates that kubectl is not installed."


def test_verify_with_kubectl_connection_success(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_port_forwarding_mock = mocker.patch.object(verify, "check_port_forwarding")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    mocker.patch.object(verify, "check_os")
    mocker.patch.object(verify, "save_dependency_versions")

    fake_config_path = '/usr/ogorek/nctl_config'
    fake_config = mocker.patch('util.dependencies_checker.Config')
    fake_config.return_value.config_path = fake_config_path

    runner = CliRunner()
    runner.invoke(verify.verify, [])

    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    assert check_port_forwarding_mock.call_count == 1, "port forwarding wasn't checked"
    assert check_dependency_mock.call_count != 0, "dependency wasn't checked"
    # noinspection PyUnresolvedReferences
    assert verify.save_dependency_versions.call_count == 1


def test_verify_with_kubectl_namespace_get_error(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_port_forwarding_mock = mocker.patch.object(verify, "check_port_forwarding")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    admin_check_mock = mocker.patch("commands.verify.verify.is_current_user_administrator")
    admin_check_mock.return_value = False
    get_namespace_mock = mocker.patch("commands.verify.verify.get_kubectl_current_context_namespace")
    get_namespace_mock.side_effect = Exception
    mocker.patch.object(verify, "save_dependency_versions")

    runner = CliRunner()
    result = runner.invoke(verify.verify, [])

    assert check_dependency_mock.call_count == 1
    assert check_connection_mock.call_count == 1
    assert check_port_forwarding_mock.call_count == 1
    # noinspection PyUnresolvedReferences
    assert verify.save_dependency_versions.call_count == 0

    assert Texts.GET_K8S_NAMESPACE_ERROR_MSG in result.output, \
        "Bad output. Namespace get error should be indicated in the console."


def test_verify_with_kubectl_admin_check_error(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_port_forwarding_mock = mocker.patch.object(verify, "check_port_forwarding")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    admin_check_mock = mocker.patch("commands.verify.verify.is_current_user_administrator")
    admin_check_mock.side_effect = Exception

    runner = CliRunner()
    result = runner.invoke(verify.verify, [])

    assert check_connection_mock.call_count == 1
    assert check_port_forwarding_mock.call_count == 1
    assert check_dependency_mock.call_count == 1

    assert Texts.GET_K8S_NAMESPACE_ERROR_MSG in result.output, \
        "Bad output. Admin check error should be indicated in the console."


def test_verify_with_port_forwarding_error(mocker):
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_port_forwarding_mock = mocker.patch.object(verify, "check_port_forwarding")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency", return_value=(True, LooseVersion('1.0')))
    check_port_forwarding_mock.side_effect = Exception

    runner = CliRunner()
    result = runner.invoke(verify.verify, [])

    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    assert check_port_forwarding_mock.call_count == 1, "port forwarding wasn't checked"
    assert check_dependency_mock.call_count == 1, "dependency wasn't checked"

    assert Texts.CHECKING_PORT_FORWARDING_FROM_CLUSTER_MSG in result.output, \
        "Bad output. Port forwarding error should be indicated in the console."
