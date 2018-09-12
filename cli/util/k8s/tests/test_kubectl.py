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

from pytest import raises, fixture
from kubernetes.client import V1ObjectMeta, V1ServiceList, V1Service, V1ServiceSpec, V1ServicePort
import util.k8s.kubectl as kubectl
from util.app_names import DLS4EAppNames
from util.exceptions import KubectlConnectionError, LocalPortOccupiedError
from cli_text_consts import UTIL_KUBECTL_TEXTS as TEXTS


SERVICES_LIST_MOCK = V1ServiceList(items=[
    V1Service(metadata=V1ObjectMeta(name="service", namespace="namespace"),
              spec=V1ServiceSpec(ports=[V1ServicePort(port=5000, node_port=33451)]))
]).items


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

    with raises(RuntimeError, message=TEXTS["proxy_creation_missing_port_error_msg"]):
        kubectl.start_port_forwarding(DLS4EAppNames.DOCKER_REGISTRY)

    assert subprocess_command_mock.call_count == 0, "kubectl proxy-forwarding command was called"


def test_start_port_forwarding_other_error(mock_k8s_svc, mocker):
    popen_mock = mocker.patch('util.system.execute_subprocess_command',
                              side_effect=Exception("Other error during creation of registry port proxy."))
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=True)
    print("test start port forwarding")
    with raises(RuntimeError, message=TEXTS["proxy_creation_other_error_msg"]):
        kubectl.start_port_forwarding(DLS4EAppNames.ELASTICSEARCH)

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command was called"
    assert check_port_avail.call_count == 1, "port availability wasn't checked"


def test_start_port_forwarding_lack_of_ports(mock_k8s_svc, mocker):
    subprocess_command_mock = mocker.patch('util.system.execute_subprocess_command')
    check_port_avail = mocker.patch("util.k8s.kubectl.check_port_availability", return_value=False)

    with raises(LocalPortOccupiedError, message=TEXTS["no_available_port_error_msg"]):
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
    subprocess_command_mock = mocker.patch('util.system.execute_system_command', return_value=('output', error_code))
    kubectl.check_connection_to_cluster()
    assert subprocess_command_mock.call_count == 1, "kubectl get pods command wasn't called"


def test_check_connection_to_cluster_with_error(mocker):
    error_code = 1
    subprocess_command_mock = mocker.patch('util.system.execute_system_command', return_value=('output', error_code))
    with raises(KubectlConnectionError):
        kubectl.check_connection_to_cluster()
    assert subprocess_command_mock.call_count == 1, "kubectl get pods command wasn't called"
