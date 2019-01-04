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

from pytest import raises, fixture
from kubernetes.client import V1ObjectMeta, V1ServiceList, V1Service, V1ServiceSpec, V1ServicePort
import util.k8s.kubectl as kubectl
from util.app_names import DLS4EAppNames
from util.exceptions import KubectlConnectionError, LocalPortOccupiedError, KubernetesError
from cli_text_consts import UtilKubectlTexts as Texts


SERVICES_LIST_MOCK = V1ServiceList(items=[
    V1Service(metadata=V1ObjectMeta(name="service", namespace="namespace"),
              spec=V1ServiceSpec(ports=[V1ServicePort(port=5000, node_port=33451)]))
]).items

TOP_RESULT_SUCCESS = "NAME CPU(cores) MEMORY(bytes)\ndls4enterprise-fluentd-hdr2p 9m 155Mi"
TOP_RESULT_FAILURE = "NAME CPU(cores) MEMORY(bytes)\ndls4enterprise-fluentd-hdr2p 9m"


@fixture
def mock_k8s_svc(mocker):
    svcs_list_mock = mocker.patch('util.k8s.kubectl.get_app_services')
    svcs_list_mock.return_value = SERVICES_LIST_MOCK


# noinspection PyUnusedLocal,PyShadowingNames
def test_start_port_forwarding_success(mock_k8s_svc, mocker):
    subprocess_command_mock = mocker.patch('util.system.execute_subprocess_command')
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=True)

    process, _, _ = kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH, number_of_retries=2)

    assert process, "proxy process doesn't exist."
    assert subprocess_command_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert check_port_avail.call_count == 1, "port availability wasn't checked"


def test_start_port_forwarding_missing_port(mocker):
    subprocess_command_mock = mocker.patch("util.system.execute_subprocess_command")
    svcs_list_mock = mocker.patch('util.k8s.kubectl.get_app_services')
    svcs_list_mock.return_value = []

    with raises(RuntimeError, message=Texts.PROXY_CREATION_MISSING_PORT_ERROR_MSG):
        kubectl.start_port_forwarding(DLS4EAppNames.DOCKER_REGISTRY)

    assert subprocess_command_mock.call_count == 0, "kubectl proxy-forwarding command was called"


def test_start_port_forwarding_other_error(mock_k8s_svc, mocker):
    popen_mock = mocker.patch('util.system.execute_subprocess_command',
                              side_effect=Exception("Other error during creation of registry port proxy."))
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=True)
    print("test start port forwarding")
    with raises(RuntimeError, message=Texts.PROXY_CREATION_OTHER_ERROR_MSG):
        kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH)

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command was called"
    assert check_port_avail.call_count == 1, "port availability wasn't checked"


def test_start_port_forwarding_lack_of_ports(mock_k8s_svc, mocker):
    subprocess_command_mock = mocker.patch('util.system.execute_subprocess_command')
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=False)

    with raises(LocalPortOccupiedError, message=Texts.NO_AVAILABLE_PORT_ERROR_MSG):
        kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH)

    assert subprocess_command_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert check_port_avail.call_count == 1000, "port availability wasn't checked"


def test_start_port_forwarding_first_two_occupied(mock_k8s_svc, mocker):
    subprocess_command_mock = mocker.patch('util.system.execute_subprocess_command')
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability")
    check_port_avail.side_effect = [False, False, True]

    process, tunnel_port, container_port = kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH)

    assert subprocess_command_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert check_port_avail.call_count == 3, "port availability wasn't checked"


def test_start_port_forwarding_success_with_different_port(mock_k8s_svc, mocker):
    subprocess_command_mock = mocker.patch('util.system.execute_subprocess_command')
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=True)

    process, tunnel_port, _ = kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH, 9999)

    assert process, "proxy process doesn't exist."
    assert subprocess_command_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert check_port_avail.call_count == 1, "port availability wasn't checked"
    assert tunnel_port == 9999, "port wasn't set properly"


def test_check_connection_to_cluster_with_success(mocker):
    error_code = 0
    subprocess_command_mock = mocker.patch('util.system.execute_system_command', return_value=('output', error_code,
                                                                                               'output'))
    kubectl.check_connection_to_cluster()
    assert subprocess_command_mock.call_count == 1, "kubectl get pods command wasn't called"


def test_check_connection_to_cluster_with_error(mocker):
    error_code = 1
    subprocess_command_mock = mocker.patch('util.system.execute_system_command', return_value=('output', error_code,
                                                                                               'output'))
    with raises(KubectlConnectionError):
        kubectl.check_connection_to_cluster()
    assert subprocess_command_mock.call_count == 1, "kubectl get pods command wasn't called"


def test_get_top_for_pod_success(mocker):
    top_command_mock = mocker.patch("util.system.execute_system_command")
    top_command_mock.return_value = TOP_RESULT_SUCCESS, 0, TOP_RESULT_SUCCESS

    cpu, mem = kubectl.get_top_for_pod(name="name", namespace="namespace")

    assert cpu == "9m"
    assert mem == "155Mi"


def test_get_top_for_pod_failure(mocker):
    top_command_mock = mocker.patch("util.system.execute_system_command")
    top_command_mock.return_value = TOP_RESULT_FAILURE, 0, TOP_RESULT_FAILURE

    with raises(KubernetesError):
        kubectl.get_top_for_pod(name="name", namespace="namespace")
