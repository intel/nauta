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

import pytest
from asynctest import CoroutineMock

from nauta_resources.platform_resource import K8SApiClient, CustomResourceApiClient


@pytest.fixture()
def load_kube_config_mock(mocker):

    return mocker.patch('nauta_resources.platform_resource.config.load_kube_config',
                        new=CoroutineMock())


@pytest.fixture()
def load_incluster_config_mock(mocker):
    return mocker.patch('nauta_resources.platform_resource.config.load_incluster_config')


@pytest.fixture(autouse=True)
def kubernetes_client_mock(mocker):
    return mocker.patch('nauta_resources.platform_resource.client')


@pytest.mark.asyncio
async def test_k8s_api_client_incluster(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = FileNotFoundError
    K8SApiClient.core_api = None
    await K8SApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 1


@pytest.mark.asyncio
async def test_k8s_api_client_kubeconfig(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = None
    K8SApiClient.core_api = None
    await K8SApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0


@pytest.mark.asyncio
async def test_k8s_api_client_failure(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = RuntimeError
    K8SApiClient.core_api = None
    with pytest.raises(RuntimeError):
        await K8SApiClient.get()


@pytest.mark.asyncio
async def test_k8s_api_client_get_twice(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = None
    K8SApiClient.core_api = None
    await K8SApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0

    await K8SApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0


@pytest.mark.asyncio
async def test_custom_resource_client_incluster(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = FileNotFoundError
    CustomResourceApiClient.k8s_custom_object_api = None
    await CustomResourceApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 1


@pytest.mark.asyncio
async def test_custom_resource_api_client_kubeconfig(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = None
    CustomResourceApiClient.k8s_custom_object_api = None
    await CustomResourceApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0


@pytest.mark.asyncio
async def test_custom_resource_api_client_failure(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = RuntimeError
    CustomResourceApiClient.k8s_custom_object_api = None
    with pytest.raises(RuntimeError):
        await CustomResourceApiClient.get()


@pytest.mark.asyncio
async def test_custom_resource_api_client_get_twice(load_kube_config_mock, load_incluster_config_mock):
    load_kube_config_mock.side_effect = None
    CustomResourceApiClient.k8s_custom_object_api = None
    await CustomResourceApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0

    await CustomResourceApiClient.get()

    assert load_kube_config_mock.call_count == 1
    assert load_incluster_config_mock.call_count == 0
