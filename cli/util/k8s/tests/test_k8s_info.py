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

from unittest.mock import MagicMock

import pytest
from kubernetes.client.models import V1Service, V1ObjectMeta, V1Namespace, V1Status, V1ConfigMap, \
                                     V1SecretList, V1Secret, V1ClusterRoleList, V1ClusterRole, \
                                     V1PolicyRule, V1PodList, V1Pod, V1PodStatus, V1ServiceSpec, V1ServicePort, \
                                     V1NamespaceStatus, V1Event, V1EventList, V1ObjectReference
from kubernetes.client.rest import ApiException

from util.k8s.k8s_info import get_kubectl_host, get_app_services, \
                              find_namespace, delete_namespace, get_config_map_data, get_users_token, \
                              get_cluster_roles, is_current_user_administrator, check_pods_status, \
                              PodStatus, get_app_service_node_port, get_pods, NamespaceStatus, get_pod_events, \
                              get_namespaced_pods
from util.config import DLS4EConfigMap
from util.app_names import DLS4EAppNames
from util.exceptions import KubernetesError

test_namespace = "test_namespace"

TEST_EXTERNAL_IP = "1.2.3.4"
TEST_IMAGE_TILLER = "tiller_image:1"

TEST_TOKEN = "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklpSjkuZXlKcGMzTWlPaUpyZFdKbGNtNWxkR1Z6TDNObGN"\
             "uWnBZMlZoWTJOdmRXNTBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5dVlXMW"\
             "xjM0JoWTJVaU9pSjBaWE4wTVRZaUxDSnJkV0psY201bGRHVnpMbWx2TDNObGNuWnBZMlZoWTJOdmRXNTBMM"\
             "05sWTNKbGRDNXVZVzFsSWpvaVpHVm1ZWFZzZEMxMGIydGxiaTAwYTNKNGFpSXNJbXQxWW1WeWJtVjBaWE11"\
             "YVc4dmMyVnlkbWxqWldGalkyOTFiblF2YzJWeWRtbGpaUzFoWTJOdmRXNTBMbTVoYldVaU9pSmtaV1poZFd"\
             "4MElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MW"\
             "JuUXVkV2xrSWpvaU16UTRNbVUzT1RJdE5UZ3hZaTB4TVdVNExUazNOR1l0TlRJM01UQXdNREF4TVRjd0lpd"\
             "2ljM1ZpSWpvaWMzbHpkR1Z0T25ObGNuWnBZMlZoWTJOdmRXNTBPblJsYzNReE5qcGtaV1poZFd4MEluMC5k"\
             "Njdvc3FOZ3hLWGZPOUlFdjFWR0txTmNWVnlIQ09yaHlPRTlkQkxGWlh4SnM0ZUNyYWFaakE4Q05udVVhSTd"\
             "Ha0dXcGxKbTZYT09YckZmN1dFWWxlaWFrc1Uzb2s2UUtsNzRwUDd6THFObXRUcmVOOGxIUHcwU2p0T2FNaX"\
             "J3MVFqVUdqZlRTcWxsaHRodFBrUFJIajFQdGZQREhHQ2g5Yy1ZMnBncXN0YWprSUhwSGtQa25yOGRLV1RER"\
             "3pvVVRmc0JRZWE0SkxENnhfQTJQUzIwc1VRR1RkQXpuZjlKY0oyWUpLNVdkenVFd1Vja1JTcDNDRFpsRmZU"\
             "WUdkOEVIWUY2NHM2T1JyczN1S2Z6dWtnRjdIWDNzQnJWTndrRXlyZHl3N3Zua0xGMENKU2I4U3V6cU9tajh"\
             "GMmtpWmlkRUsweTZhVDhsR1dUTTJGWW1TRzFabC0xd3BHS2pickQtUVlxY2tDODlSa0dkY2NlZUp6UzZBRU"\
             "R4SUN6N1NGWHNsT2tTZnZwSDN4ZUhETE92ZkhGWmJtb1dDbFdMWHpod0h3V3hVQ2RKZG9zWE4yVm5Nc1VRM"\
             "jJwaDhUcXVjWktrb0xhNDdGRFRraWlnYURmdkxqYU5PcGxvS1M2d3pRMWxVUktQMlJGcTRUMDFEVEpsLUFC"\
             "WS0tTVl2UjJtY3o5TTR2dldvZkVGNkREVnpXc2gwTHRyN05HOFpzTnpTaGl3RnUzcDlIbFMxdDdRNjgyc0J"\
             "icEw4Yl9lZTVZTGo5WHJFSUU1MW0zaTlxYzNaY3hGT3BYOHNzV04tVnpHcTV2NGszNFd0MUVwaHp2OG5uS1"\
             "lIa2YzdGZkcHFjYVdFRllaTXM0bzV1d1h0emZRYmF6VVJobUdEVFpIWkNYQUN3eEIzZ1RrSzF0WjR4cw=="

TEST_TOKEN_ENCODED = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3"\
                     "ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJ0ZXN0MTYiLCJrdWJlcm5ldGVzLmlvL"\
                     "3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoiZGVmYXVsdC10b2tlbi00a3J4aiIsImt1YmVybmV0ZXMu"\
                     "aW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5"\
                     "pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiMzQ4MmU3OTItNTgxYi0xMWU4LTk3NG"\
                     "YtNTI3MTAwMDAxMTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OnRlc3QxNjpkZWZhdWx0In0.d"\
                     "67osqNgxKXfO9IEv1VGKqNcVVyHCOrhyOE9dBLFZXxJs4eCraaZjA8CNnuUaI7GkGWplJm6XOOXrFf7WEYl"\
                     "eiaksU3ok6QKl74pP7zLqNmtTreN8lHPw0SjtOaMirw1QjUGjfTSqllhthtPkPRHj1PtfPDHGCh9c-Y2pgq"\
                     "stajkIHpHkPknr8dKWTDGzoUTfsBQea4JLD6x_A2PS20sUQGTdAznf9JcJ2YJK5WdzuEwUckRSp3CDZlFfT"\
                     "YGd8EHYF64s6ORrs3uKfzukgF7HX3sBrVNwkEyrdyw7vnkLF0CJSb8SuzqOmj8F2kiZidEK0y6aT8lGWTM2"\
                     "FYmSG1Zl-1wpGKjbrD-QYqckC89RkGdcceeJzS6AEDxICz7SFXslOkSfvpH3xeHDLOvfHFZbmoWClWLXzhw"\
                     "HwWxUCdJdosXN2VnMsUQ22ph8TqucZKkoLa47FDTkiigaDfvLjaNOploKS6wzQ1lURKP2RFq4T01DTJl-AB"\
                     "Y--MYvR2mcz9M4vvWofEF6DDVzWsh0Ltr7NG8ZsNzShiwFu3p9HlS1t7Q682sBbpL8b_ee5YLj9XrEIE51m"\
                     "3i9qc3ZcxFOpX8ssWN-VzGq5v4k34Wt1Ephzv8nnKYHkf3tfdpqcaWEFYZMs4o5uwXtzfQbazURhmGDTZHZ"\
                     "CXACwxB3gTkK1tZ4xs"

K8S_RUNNING_POD_STATUS = "Running"

K8S_PENDING_POD_STATUS = "Pending"


@pytest.fixture()
def mocked_k8s_config(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocked_conf_class = mocker.patch('kubernetes.client.configuration.Configuration')
    conf_instance = mocked_conf_class.return_value
    conf_instance.host = 'https://127.0.0.1:8080'


def test_config_map_data():
    return {DLS4EConfigMap.EXTERNAL_IP_FIELD: TEST_EXTERNAL_IP,
            DLS4EConfigMap.IMAGE_TILLER_FIELD: TEST_IMAGE_TILLER}


@pytest.fixture()
def mocked_kubeconfig(mocker):
    mocker.patch("kubernetes.config.load_kube_config")


@pytest.fixture()
def mocked_k8s_CoreV1Api(mocker):
    mocked_coreV1Api_class = mocker.patch('kubernetes.client.CoreV1Api')
    mocker.patch('kubernetes.client.ApiClient')
    coreV1API_instance = mocked_coreV1Api_class.return_value

    pods_mock = MagicMock()
    pods_mock.items = [MagicMock(spec=V1Pod), MagicMock(spec=V1Pod), MagicMock(spec=V1Pod)]
    coreV1API_instance.list_pod_for_all_namespaces.return_value = pods_mock

    services_mock = MagicMock()
    services_mock.items = [MagicMock(spec=V1Service), MagicMock(spec=V1Service), MagicMock(spec=V1Service)]
    coreV1API_instance.list_service_for_all_namespaces.return_value = services_mock

    v1_namespace = V1Namespace()
    v1_metadata_namespace = V1ObjectMeta(name=test_namespace)
    v1_namespace.metadata = v1_metadata_namespace
    v1_namespace_status = V1NamespaceStatus(phase=NamespaceStatus.ACTIVE.value)
    v1_namespace.status = v1_namespace_status

    coreV1API_instance.read_namespace.return_value = v1_namespace
    coreV1API_instance.delete_namespace.return_value = V1Status(status="{'phase': 'Terminating'}")

    v1_config_map = V1ConfigMap(data=test_config_map_data())

    coreV1API_instance.read_namespaced_config_map.return_value = v1_config_map

    secret_data = {"token": TEST_TOKEN}
    v1_metadata_secret = V1ObjectMeta(name="default-token")
    v1_secret = V1Secret(metadata=v1_metadata_secret, data=secret_data)
    v1_secret_list = V1SecretList(items=[v1_secret])

    coreV1API_instance.list_namespaced_secret.return_value = v1_secret_list

    v1_pod_status = V1PodStatus(phase=K8S_RUNNING_POD_STATUS)
    v1_pod = V1Pod(status=v1_pod_status)
    v1_pod_lists = V1PodList(items=[v1_pod])

    coreV1API_instance.list_namespaced_pod.return_value = v1_pod_lists

    v1_metadata_event = V1ObjectMeta(name="default-name")
    v1_object = V1ObjectReference(name="pod_name")
    v1_event = V1Event(message="Insufficient cpu", involved_object=v1_object, metadata=v1_metadata_event)
    v1_event_list = V1EventList(items=[v1_event])

    coreV1API_instance.list_namespaced_event.return_value = v1_event_list

    return coreV1API_instance


@pytest.fixture()
def mocked_k8s_RbacAuthorizationV1Api(mocker):
    mocked_RbacAuthorizationV1Api_class = mocker.patch('kubernetes.client.RbacAuthorizationV1Api')
    mocker.patch('kubernetes.client.ApiClient')
    rbacAuthorizationV1_instance = mocked_RbacAuthorizationV1Api_class.return_value

    v1_metadata_role = V1ObjectMeta(name="metadata-role")
    v1_policy_rule = V1PolicyRule(verbs=["verb"])
    v1_role = V1ClusterRole(metadata=v1_metadata_role, kind="ClusterRole", rules=[v1_policy_rule])
    v1_cluster_role_list = V1ClusterRoleList(items=[v1_role])

    rbacAuthorizationV1_instance.list_cluster_role.return_value = v1_cluster_role_list


def test_get_k8s_host_w_port(mocked_k8s_config):
    k8s_host = get_kubectl_host()

    assert k8s_host == '127.0.0.1:8080'


def test_get_k8s_host_wo_port(mocked_k8s_config):
    k8s_host = get_kubectl_host(with_port=False)

    assert k8s_host == '127.0.0.1'


def test_get_app_services(mocked_k8s_config, mocked_k8s_CoreV1Api):
    services = get_app_services(dls4e_app_name=DLS4EAppNames.DOCKER_REGISTRY)

    assert services


def test_get_pod_events(mocked_k8s_config, mocked_k8s_CoreV1Api):
    events = get_pod_events(namespace=test_namespace)

    assert events


def test_find_namespace_success(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    assert find_namespace(test_namespace) == NamespaceStatus.ACTIVE


def test_find_namespace_failure(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    assert find_namespace(test_namespace+'_wrong') == NamespaceStatus.NOT_EXISTS


def test_find_namespace_terminating(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.read_namespace.return_value.status = V1NamespaceStatus(phase=NamespaceStatus.TERMINATING.value)
    assert find_namespace(test_namespace) == NamespaceStatus.TERMINATING


def test_delete_namespace(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    delete_namespace(test_namespace)

    assert mocked_k8s_CoreV1Api.delete_namespace.call_count == 1


def test_delete_namespace_exception(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.delete_namespace.side_effect = RuntimeError()

    with pytest.raises(KubernetesError):
        delete_namespace(test_namespace)


def test_delete_namespace_failure(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.delete_namespace.return_value = V1Status(status="{'phase': 'Other'}")

    with pytest.raises(KubernetesError):
        delete_namespace(test_namespace)


def test_get_config_map_data(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    data = get_config_map_data("config_map_name", test_namespace)

    assert data.get(DLS4EConfigMap.EXTERNAL_IP_FIELD) == TEST_EXTERNAL_IP
    assert data.get(DLS4EConfigMap.IMAGE_TILLER_FIELD) == TEST_IMAGE_TILLER


def test_get_users_token(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    token = get_users_token(test_namespace)

    assert token == TEST_TOKEN_ENCODED


def test_get_pods(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    pods = get_pods(label_selector='')
    assert pods


def test_get_pods_not_found(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.list_pod_for_all_namespaces.side_effect = ApiException(status=404)
    pods = get_pods(label_selector='')
    assert pods == []


def test_get_pods_error(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.list_pod_for_all_namespaces.side_effect = ApiException(status=500)
    with pytest.raises(ApiException):
        get_pods(label_selector='')


def test_get_namespaced_pods(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    pods = get_namespaced_pods(label_selector='', namespace=test_namespace)
    assert pods


def test_get_namespaced_pods_not_found(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.list_namespaced_pod.side_effect = ApiException(status=404)
    pods = get_namespaced_pods(label_selector='', namespace=test_namespace)
    assert pods == []


def test_get_namespaced_pods_error(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.list_namespaced_pod.side_effect = ApiException(status=500)
    with pytest.raises(ApiException):
        get_namespaced_pods(label_selector='', namespace=test_namespace)


def test_get_cluster_roles(mocked_k8s_config, mocked_k8s_RbacAuthorizationV1Api):
    roles = get_cluster_roles()
    print(roles)
    assert roles.items[0].kind == "ClusterRole"


def test_is_current_user_administrator_is(mocker):
    gcr_mock = mocker.patch("util.k8s.k8s_info.get_cluster_roles")

    assert is_current_user_administrator()
    assert gcr_mock.call_count == 1


def test_is_current_user_administrator_is_not(mocker):
    gcr_mock = mocker.patch("util.k8s.k8s_info.get_cluster_roles", side_effect=ApiException(status=403))

    assert not is_current_user_administrator()
    assert gcr_mock.call_count == 1


def test_is_current_user_administrator_(mocker):
    gcr_mock = mocker.patch("util.k8s.k8s_info.get_cluster_roles", side_effect=ApiException(status=404))

    with pytest.raises(ApiException):
        is_current_user_administrator()

    assert gcr_mock.call_count == 1


def test_check_pods_status_success(mocked_k8s_CoreV1Api, mocked_kubeconfig):
    assert check_pods_status("run_name", test_namespace, PodStatus.RUNNING, None)


def test_check_pods_status_failure(mocked_k8s_CoreV1Api, mocked_kubeconfig):
    mocked_k8s_CoreV1Api.list_namespaced_pod.return_value.items[0].status.phase = K8S_PENDING_POD_STATUS
    assert not check_pods_status("run_name", test_namespace, PodStatus.RUNNING, None)
    mocked_k8s_CoreV1Api.list_namespaced_pod.return_value.items[0].status.phase = K8S_RUNNING_POD_STATUS


def test_check_pods_status_failure_empty_list(mocked_k8s_CoreV1Api, mocked_kubeconfig):
    ret_value = mocked_k8s_CoreV1Api.list_namespaced_pod.return_value
    mocked_k8s_CoreV1Api.list_namespaced_pod.return_value = None
    assert not check_pods_status("run_name", test_namespace, PodStatus.RUNNING, None)
    mocked_k8s_CoreV1Api.list_namespaced_pod.return_value = ret_value


def test_get_app_service_node_port(mocker):
    test_node_port = 1234
    get_app_services_mock = mocker.patch('util.k8s.k8s_info.get_app_services')
    get_app_services_mock.return_value = [
        V1Service(spec=V1ServiceSpec(
            ports=[
                V1ServicePort(node_port=test_node_port,
                              port=test_node_port)
            ]
        ))
    ]
    assert get_app_service_node_port(DLS4EAppNames.DOCKER_REGISTRY) == test_node_port
