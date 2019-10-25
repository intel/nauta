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

from unittest.mock import MagicMock

import pytest
from kubernetes_asyncio.client import CustomObjectsApi
from kubernetes_asyncio.client.rest import ApiException
from asynctest import CoroutineMock

from nauta_resources.run import Run, RunStatus
from nauta_resources.platform_resource import CustomResourceApiClient

TEST_RUNS = [Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                 parameters=['mnist_single_node.py', '--data_dir', '/app'],
                 state=RunStatus.QUEUED,
                 metrics={'accuracy': 52.322},
                 experiment_name="experiment-name-will-be-added-soon",
                 pod_count=1,
                 pod_selector={'matchLabels': {'app': 'tf-training',
                                               'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                                               'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'}},
                 namespace="mciesiel-dev",
                 template_name="tf-training"),
             Run(name="exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training",
                 parameters=['mnist_single_node.py', '--data_dir', '/app'], state=RunStatus.COMPLETE,
                 metrics={'accuracy': 52.322}, experiment_name="experiment-name-will-be-added-soon", pod_count=1,
                 pod_selector={
                     'matchLabels': {'app': 'tf-training', 'draft': 'exp-mnist-single-node.py-18.05.17-16.05.56-2',
                                     'release': 'exp-mnist-single-node.py-18.05.17-16.05.56-2'}},
                 namespace="mciesiel-dev",
                 template_name="tf-training",
                 start_timestamp='2018-05-17T14:10:13Z',
                 end_timestamp='2018-05-17T14:15:41Z')]


@pytest.fixture(scope='function')
def mock_k8s_api_client() -> CustomObjectsApi:
    custom_objects_api_mock = MagicMock()
    CustomResourceApiClient.k8s_custom_object_api = custom_objects_api_mock

    custom_objects_api_mock.list_cluster_custom_object = CoroutineMock()
    custom_objects_api_mock.list_namespaced_custom_object = CoroutineMock()
    custom_objects_api_mock.get_cluster_custom_object = CoroutineMock()
    custom_objects_api_mock.get_namespaced_custom_object = CoroutineMock()
    custom_objects_api_mock.patch_namespaced_custom_object = CoroutineMock()
    custom_objects_api_mock.create_namespaced_custom_object = CoroutineMock()
    return custom_objects_api_mock


@pytest.mark.asyncio
async def test_list_runs(mock_k8s_api_client):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_RUNS_RESPONSE_RAW
    runs = await Run.list()
    assert runs == TEST_RUNS


@pytest.mark.asyncio
async def test_list_runs_from_namespace(mock_k8s_api_client: CustomObjectsApi):
    raw_runs_single_namespace = dict(LIST_RUNS_RESPONSE_RAW)
    raw_runs_single_namespace['items'] = [raw_runs_single_namespace['items'][0]]
    mock_k8s_api_client.list_namespaced_custom_object.return_value = raw_runs_single_namespace

    runs = await Run.list(namespace='namespace-1')

    assert [TEST_RUNS[0]] == runs


@pytest.mark.asyncio
async def test_get_run_from_namespace(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.return_value = GET_RUN_RESPONSE_RAW
    run = await Run.get(name=RUN_NAME, namespace=NAMESPACE)
    assert run is not None and type(run) is Run


@pytest.mark.asyncio
async def test_get_run_not_found(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.side_effect = ApiException(status=404)
    run = await Run.get(name=RUN_NAME, namespace=NAMESPACE)
    assert run is None


@pytest.mark.asyncio
async def test_get_run_failure(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.side_effect = ApiException(status=500)
    with pytest.raises(ApiException):
        await Run.get(name=RUN_NAME, namespace=NAMESPACE)


@pytest.mark.asyncio
async def test_update_run_success(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.patch_namespaced_custom_object.return_value = LIST_RUNS_RESPONSE_RAW['items'][0]

    await TEST_RUNS[0].update()

    assert mock_k8s_api_client.patch_namespaced_custom_object.call_count == 1


@pytest.mark.asyncio
async def test_update_run_failure(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.patch_namespaced_custom_object.side_effect = ApiException()

    with pytest.raises(ApiException):
        await TEST_RUNS[0].update()


@pytest.mark.asyncio
async def test_add_run(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.create_namespaced_custom_object.return_value = GET_RUN_RESPONSE_RAW
    run = Run(name=RUN_NAME, experiment_name='fake')
    added_run = await run.create(namespace=NAMESPACE)
    assert added_run is not None


@pytest.mark.asyncio
async def test_add_run_failure(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.create_namespaced_custom_object.side_effect = ApiException(status=500)
    run = Run(name=RUN_NAME, experiment_name='fake')
    with pytest.raises(ApiException):
        await run.create(namespace=NAMESPACE)


LIST_RUNS_RESPONSE_RAW = \
    {
        'apiVersion': 'aipg.intel.com/v1',
        'items': [
            {
                'apiVersion': 'aipg.intel.com/v1',
                'kind': 'Run',
                'metadata': {
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                    'namespace': 'mciesiel-dev',
                },
                'spec': {
                    'experiment-name': 'experiment-name-will-be-added-soon',
                    'metrics': {'accuracy': 52.322},
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                    'parameters': ['mnist_single_node.py', '--data_dir', '/app'],
                    'pod-count': 1,
                    'pod-selector': {
                        'matchLabels': {
                            'app': 'tf-training',
                            'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                            'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'
                        }
                    },
                    'state': 'QUEUED'
                }
            },
            {
                'apiVersion': 'aipg.intel.com/v1',
                'kind': 'Run',
                'metadata': {
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                    'namespace': 'mciesiel-dev',
                },
                'spec': {
                    'experiment-name': 'experiment-name-will-be-added-soon',
                    'metrics': {'accuracy': 52.322},
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                    'parameters': ['mnist_single_node.py', '--data_dir', '/app'],
                    'pod-count': 1,
                    'pod-selector': {
                        'matchLabels': {
                            'app': 'tf-training',
                            'draft': 'exp-mnist-single-node.py-18.05.17-16.05.56-2',
                            'release': 'exp-mnist-single-node.py-18.05.17-16.05.56-2'
                        }
                    },
                    'state': 'COMPLETE',
                    'start-time': '2018-05-17T14:10:13Z',
                    'end-time': '2018-05-17T14:15:41Z'
                }
            }
        ],
        'kind': 'RunList',
        'metadata': {
            'continue': '',
            'resourceVersion': '436078',
            'selfLink': '/apis/aipg.intel.com/v1/runs'
        }
    }

NAMESPACE = 'test-env'
RUN_NAME = 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training'
GET_RUN_RESPONSE_RAW = {
    'apiVersion': 'aipg.intel.com/v1',
    'kind': 'Run',
    'metadata': {
        'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
        'namespace': 'mciesiel-dev',
    },
    'spec': {
        'experiment-name': 'experiment-name-will-be-added-soon',
        'metrics': {'accuracy': 52.322},
        'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
        'parameters': ['mnist_single_node.py', '--data_dir', '/app'],
        'pod-count': 1,
        'pod-selector': {
            'matchLabels': {
                'app': 'tf-training',
                'draft': 'exp-mnist-single-node.py-18.05.17-16.05.56-2',
                'release': 'exp-mnist-single-node.py-18.05.17-16.05.56-2'
            }
        },
        'state': 'COMPLETE',
        'start-time': '2018-05-17T14:10:13Z',
        'end-time': '2018-05-17T14:15:41Z'
    }
}
