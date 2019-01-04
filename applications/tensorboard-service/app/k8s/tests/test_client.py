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

from kubernetes import client as k8s_models
from kubernetes.client.rest import ApiException
from pytest import fixture, raises
from pytest_mock import MockFixture

from k8s.client import K8SAPIClient

MY_FAKE_NAMESPACE = 'fake-namespace'
FAKE_OBJECT_NAME = 'fake-name'
FAKE_LABEL_SELECTOR = 'key=value'


@fixture
def k8s_api_client_mock(mocker) -> K8SAPIClient:
    mocker.patch('kubernetes.client.AppsV1Api')
    mocker.patch('kubernetes.client.ExtensionsV1beta1Api')
    mocker.patch('kubernetes.client.CoreV1Api')

    client = K8SAPIClient()

    return client


# noinspection PyShadowingNames
def test_create_deployment(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.create_deployment(namespace=MY_FAKE_NAMESPACE, body=k8s_models.V1Deployment())

    k8s_api_client_mock.apps_api_client.create_namespaced_deployment.\
        assert_called_once_with(namespace=MY_FAKE_NAMESPACE, body=k8s_models.V1Deployment())


# noinspection PyShadowingNames
def test_list_deployments(mocker, k8s_api_client_mock: K8SAPIClient):
    fake_deployments = [k8s_models.V1Deployment(metadata=k8s_models.V1ObjectMeta(name='fake-deployment'))]
    fake_deployment_list = k8s_models.V1DeploymentList(items=fake_deployments)

    mocker.patch.object(k8s_api_client_mock.apps_api_client, 'list_namespaced_deployment').return_value = \
        fake_deployment_list

    deployments = k8s_api_client_mock.list_deployments(namespace=MY_FAKE_NAMESPACE)

    assert deployments == fake_deployments
    k8s_api_client_mock.apps_api_client.list_namespaced_deployment.assert_called_once_with(namespace=MY_FAKE_NAMESPACE,
                                                                                           label_selector=None)


# noinspection PyShadowingNames
def test_get_deployment(mocker, k8s_api_client_mock: K8SAPIClient):
    fake_deployment = k8s_models.V1Deployment(metadata=k8s_models.V1ObjectMeta(name='fake-deployment'))

    mocker.patch.object(k8s_api_client_mock.apps_api_client, 'read_namespaced_deployment').return_value = \
        fake_deployment

    deployment = k8s_api_client_mock.get_deployment(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    assert deployment == fake_deployment


# noinspection PyShadowingNames
def test_get_deployment_raises_not_found_api_exception(mocker, k8s_api_client_mock: K8SAPIClient):
    mocker.patch.object(k8s_api_client_mock.apps_api_client, 'read_namespaced_deployment').side_effect = \
        ApiException(status=HTTPStatus.NOT_FOUND)

    deployment = k8s_api_client_mock.get_deployment(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    assert deployment is None


# noinspection PyShadowingNames
def test_get_deployment_raises_other_api_exception(mocker, k8s_api_client_mock: K8SAPIClient):
    mocker.patch.object(k8s_api_client_mock.apps_api_client, 'read_namespaced_deployment').side_effect = \
        ApiException(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    with raises(ApiException):
        k8s_api_client_mock.get_deployment(name='fake-name', namespace=MY_FAKE_NAMESPACE)


# noinspection PyShadowingNames
def test_delete_deployment(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.delete_deployment(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    k8s_api_client_mock.apps_api_client.delete_namespaced_deployment.\
        assert_called_once_with(name='fake-name',
                                namespace=MY_FAKE_NAMESPACE,
                                body=k8s_models.V1DeleteOptions())


# noinspection PyShadowingNames
def test_create_service(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.create_service(namespace=MY_FAKE_NAMESPACE, body=k8s_models.V1Service())

    k8s_api_client_mock.v1_api_client.create_namespaced_service.assert_called_once_with(namespace=MY_FAKE_NAMESPACE,
                                                                                        body=k8s_models.V1Service())


# noinspection PyShadowingNames
def test_get_service(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.get_service(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    k8s_api_client_mock.v1_api_client.read_namespaced_service.assert_called_once_with(name='fake-name',
                                                                                      namespace=MY_FAKE_NAMESPACE)


# noinspection PyShadowingNames
def test_delete_service(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.delete_service(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    k8s_api_client_mock.v1_api_client.delete_namespaced_service.\
        assert_called_once_with(name='fake-name',
                                namespace=MY_FAKE_NAMESPACE,
                                body=k8s_models.V1DeleteOptions())


# noinspection PyShadowingNames
def test_create_ingress(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.create_ingress(namespace=MY_FAKE_NAMESPACE, body=k8s_models.V1beta1Ingress())

    k8s_api_client_mock.extensions_v1beta1_api_client.create_namespaced_ingress.assert_called_once_with(
        namespace=MY_FAKE_NAMESPACE,
        body=k8s_models.V1beta1Ingress()
    )


# noinspection PyShadowingNames
def test_get_ingress(k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.get_ingress(name='fake-name', namespace=MY_FAKE_NAMESPACE)

    k8s_api_client_mock.extensions_v1beta1_api_client.read_namespaced_ingress.assert_called_once_with(
        namespace=MY_FAKE_NAMESPACE,
        name='fake-name'
    )


# noinspection PyShadowingNames
def test_list_ingresses(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    fake_ingresses = [k8s_models.V1beta1Ingress(metadata=k8s_models.V1ObjectMeta(name=FAKE_OBJECT_NAME)),
                      k8s_models.V1beta1Ingress(metadata=k8s_models.V1ObjectMeta(name=FAKE_OBJECT_NAME+'-2'))]
    fake_ingresses_list = k8s_models.V1beta1IngressList(items=fake_ingresses)

    mocker.patch.object(k8s_api_client_mock.extensions_v1beta1_api_client, 'list_namespaced_ingress').return_value = \
        fake_ingresses_list

    ingresses = k8s_api_client_mock.list_ingresses(name='fake-name',
                                                   namespace=MY_FAKE_NAMESPACE,
                                                   label_selector='key=value')

    assert ingresses == fake_ingresses


# noinspection PyShadowingNames
def test_delete_ingress(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    k8s_api_client_mock.delete_ingress(name=FAKE_OBJECT_NAME, namespace=MY_FAKE_NAMESPACE)

    k8s_api_client_mock.extensions_v1beta1_api_client.delete_namespaced_ingress.assert_called_once_with(
        name=FAKE_OBJECT_NAME,
        namespace=MY_FAKE_NAMESPACE,
        body=mocker.ANY
    )


# noinspection PyShadowingNames
def test_get_pod(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    fake_pod = k8s_models.V1Pod(metadata=k8s_models.V1ObjectMeta(name=FAKE_OBJECT_NAME))
    fake_pods = [fake_pod]
    fake_pods_list = k8s_models.V1PodList(items=fake_pods)

    mocker.patch.object(k8s_api_client_mock.v1_api_client, 'list_namespaced_pod').return_value = fake_pods_list

    pod = k8s_api_client_mock.get_pod(namespace=MY_FAKE_NAMESPACE, label_selector=FAKE_LABEL_SELECTOR)

    assert pod == fake_pod
    assert pod.metadata.name == fake_pod.metadata.name


# noinspection PyShadowingNames
def test_get_pod_raises_not_found_api_exception(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    mocker.patch.object(k8s_api_client_mock.v1_api_client, 'list_namespaced_pod').side_effect = \
        ApiException(status=HTTPStatus.NOT_FOUND)

    pod = k8s_api_client_mock.get_pod(namespace=MY_FAKE_NAMESPACE, label_selector=FAKE_LABEL_SELECTOR)

    assert pod is None


# noinspection PyShadowingNames
def test_get_pod_raises_other_api_exception(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    mocker.patch.object(k8s_api_client_mock.v1_api_client, 'list_namespaced_pod').side_effect = \
        ApiException(status=HTTPStatus.BAD_REQUEST)

    with raises(ApiException):
        k8s_api_client_mock.get_pod(namespace=MY_FAKE_NAMESPACE, label_selector=FAKE_LABEL_SELECTOR)


# noinspection PyShadowingNames
def test_get_pod_finds_no_pod(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    fake_pods = []
    fake_pods_list = k8s_models.V1PodList(items=fake_pods)

    mocker.patch.object(k8s_api_client_mock.v1_api_client, 'list_namespaced_pod').return_value = fake_pods_list

    found_pod = k8s_api_client_mock.get_pod(namespace=MY_FAKE_NAMESPACE, label_selector=FAKE_LABEL_SELECTOR)

    assert found_pod is None


# noinspection PyShadowingNames
def test_get_pod_finds_many_pods(mocker: MockFixture, k8s_api_client_mock: K8SAPIClient):
    fake_pod = k8s_models.V1Pod(metadata=k8s_models.V1ObjectMeta(name=FAKE_OBJECT_NAME))
    fake_second_pod = k8s_models.V1Pod(metadata=k8s_models.V1ObjectMeta(name=FAKE_OBJECT_NAME+'-2'))
    fake_pods = [fake_pod, fake_second_pod]
    fake_pods_list = k8s_models.V1PodList(items=fake_pods)

    mocker.patch.object(k8s_api_client_mock.v1_api_client, 'list_namespaced_pod').return_value = fake_pods_list

    found_pod = k8s_api_client_mock.get_pod(namespace=MY_FAKE_NAMESPACE, label_selector=FAKE_LABEL_SELECTOR)

    assert found_pod in (fake_pod, fake_second_pod)
