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

import pytest
from kubernetes.client.models import V1Service, V1ObjectMeta, V1Namespace, V1Status, V1ConfigMap, \
                                     V1SecretList, V1Secret

from util.k8s.k8s_info import get_kubectl_port, get_kubectl_host, get_app_services, get_app_namespace, \
                              find_namespace, delete_namespace, get_config_map_data, get_users_token
from util.config import DLS4EConfigMap

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


@pytest.fixture()
def mocked_k8s_config(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocked_conf_class = mocker.patch('kubernetes.client.configuration.Configuration')
    conf_instance = mocked_conf_class.return_value
    conf_instance.host = 'https://127.0.0.1:8080'


class K8SPodsListMock(object):

    def __init__(self, items):
        self.items = items


class K8SServicesListMock(object):

    def __init__(self, items):
        self.items = items


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
    coreV1API_instance.list_pod_for_all_namespaces.return_value = K8SPodsListMock([1, 2, 3])
    coreV1API_instance.list_service_for_all_namespaces.return_value = K8SServicesListMock([4, 5, 6])

    v1_namespace = V1Namespace()
    v1_metadata_namespace = V1ObjectMeta(name=test_namespace)
    v1_namespace.metadata = v1_metadata_namespace

    coreV1API_instance.read_namespace.return_value = v1_namespace
    coreV1API_instance.delete_namespace.return_value = V1Status(status="{'phase': 'Terminating'}")

    v1_config_map = V1ConfigMap(data=test_config_map_data())

    coreV1API_instance.read_namespaced_config_map.return_value = v1_config_map

    secret_data = {"token": TEST_TOKEN}
    v1_metadata_secret = V1ObjectMeta(name="default-token")
    v1_secret = V1Secret(metadata=v1_metadata_secret, data=secret_data)
    v1_secret_list = V1SecretList(items=[v1_secret])

    coreV1API_instance.list_namespaced_secret.return_value = v1_secret_list

    return coreV1API_instance


def test_get_k8s_host(mocked_k8s_config):
    k8s_host = get_kubectl_host()

    assert k8s_host == '127.0.0.1'


def test_get_k8s_port(mocked_k8s_config):
    k8s_port = get_kubectl_port()

    assert k8s_port == 8080


def test_get_app_services(mocked_k8s_config, mocked_k8s_CoreV1Api):
    app_name = 'test-app'
    services = get_app_services(app_name)

    assert services == [4, 5, 6]


def test_get_app_namespace(mocker):
    get_app_svc_mock = mocker.patch('util.k8s.k8s_info.get_app_services')

    v1_service = V1Service()
    metadata = V1ObjectMeta(namespace=test_namespace)
    v1_service.metadata = metadata

    get_app_svc_mock.return_value = [v1_service]

    namespace = get_app_namespace('app_name')

    assert namespace == test_namespace


def test_find_namespace_success(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig) -> bool:
    assert find_namespace(test_namespace)


def test_find_namespace_failure(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig) -> bool:
    assert not find_namespace(test_namespace+'_wrong')


def test_delete_namespace(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    delete_namespace(test_namespace)

    assert mocked_k8s_CoreV1Api.delete_namespace.call_count == 1


def test_get_config_map_data(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    data = get_config_map_data("config_map_name", test_namespace)

    assert data.get(DLS4EConfigMap.EXTERNAL_IP_FIELD) == TEST_EXTERNAL_IP
    assert data.get(DLS4EConfigMap.IMAGE_TILLER_FIELD) == TEST_IMAGE_TILLER


def test_get_users_token(mocker, mocked_k8s_CoreV1Api, mocked_kubeconfig):
    token = get_users_token(test_namespace)

    assert token == TEST_TOKEN_ENCODED
