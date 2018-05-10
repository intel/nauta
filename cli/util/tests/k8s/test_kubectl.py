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
from kubernetes.client import V1PodList, V1Pod, V1ObjectMeta, V1ServiceList, V1Service, V1ServiceSpec, V1ServicePort
from util.k8s.k8s_info import PodStatus
import util.k8s.kubectl as kubectl


TEST_APP_NAME = 'test-app'

PODS_LIST_MOCK = V1PodList(items=[
    V1Pod(metadata=V1ObjectMeta(name='test-1', namespace='test-namespace-1')),
    V1Pod(metadata=V1ObjectMeta(name='test-2', namespace='test-namespace-2'))
]).items

SERVICES_LIST_MOCK = V1ServiceList(items=[
    V1Service(spec=V1ServiceSpec(ports=[V1ServicePort(port=5000, node_port=33451)]))
]).items


@fixture()
def mock_k8s_pods_and_svc(mocker):
    pods_list_mock = mocker.patch('util.k8s.kubectl.get_app_pods')
    pods_list_mock.return_value = PODS_LIST_MOCK
    svcs_list_mock = mocker.patch('util.k8s.kubectl.get_app_services')
    svcs_list_mock.return_value = SERVICES_LIST_MOCK


def test_start_port_forwarding_success(mock_k8s_pods_and_svc, mocker):
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.RUNNING
    popen_mock = mocker.patch('subprocess.Popen')

    process, _, _ = kubectl.start_port_forwarding(TEST_APP_NAME)

    assert process, "proxy process doesn't exist."
    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"


def test_start_port_forwarding_missing_pod(mocker):
    popen_mock = mocker.patch("subprocess.Popen")
    pods_list_mock = mocker.patch('util.k8s.kubectl.get_app_pods')
    pods_list_mock.return_value = []

    with raises(RuntimeError, message="Missing pod name during creation of registry port proxy."):
        kubectl.start_port_forwarding(TEST_APP_NAME)

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"


def test_start_port_forwarding_missing_port(mocker):
    popen_mock = mocker.patch("subprocess.Popen")
    pods_list_mock = mocker.patch('util.k8s.kubectl.get_app_pods')
    pods_list_mock.return_value = PODS_LIST_MOCK
    svcs_list_mock = mocker.patch('util.k8s.kubectl.get_app_services')
    svcs_list_mock.return_value = []
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.RUNNING

    with raises(RuntimeError, message="Missing pod port during creation of registry port proxy."):
        kubectl.start_port_forwarding(TEST_APP_NAME)

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"


def test_start_port_forwarding_other_error(mock_k8s_pods_and_svc, mocker):
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.FAILED
    popen_mock = mocker.patch('subprocess.Popen',
                              side_effect=Exception("Other error during creation of registry port proxy."))

    with raises(RuntimeError, message="Other error during creation of registry port proxy."):
        kubectl.start_port_forwarding(TEST_APP_NAME)

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"


def test_set_registry_port_for_draft_if_docker_registry(mock_k8s_pods_and_svc, mocker):
    app_name = 'docker-registry'
    popen_mock = mocker.patch('subprocess.Popen')
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.RUNNING
    srp_mock = mocker.patch("util.k8s.kubectl.set_registry_port", side_effect=[("OK", 0)])

    kubectl.start_port_forwarding(app_name)

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"


def test_set_registry_port_for_draft_if_not_docker_registry(mock_k8s_pods_and_svc, mocker):
    popen_mock = mocker.patch('subprocess.Popen')
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.RUNNING
    srp_mock = mocker.patch("util.k8s.kubectl.set_registry_port")

    kubectl.start_port_forwarding(TEST_APP_NAME)

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert srp_mock.call_count == 0, "draft.set_registry_port command was called"


def test_start_port_forwarding_draft_config_fail(mock_k8s_pods_and_svc, mocker):
    app_name = 'docker-registry'
    popen_mock = mocker.patch('subprocess.Popen')
    pod_status_mock = mocker.patch('util.k8s.kubectl.get_pod_status')
    pod_status_mock.return_value = PodStatus.RUNNING
    srp_mock = mocker.patch("util.k8s.kubectl.set_registry_port", side_effect=[("Error message", 1)])

    with raises(RuntimeError, message="Setting draft config failed."):
        kubectl.start_port_forwarding(app_name)

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"
