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

from kubernetes.client import CustomObjectsApi
from kubernetes.client.rest import ApiException

from platform_resources.platform_resource import KubernetesObject
from platform_resources.run import Run, RunStatus
from util.exceptions import InvalidRegularExpressionError

TEST_RUNS = [Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                 parameters=['mnist_single_node.py', '--data_dir', '/app'],
                 state=RunStatus.QUEUED,
                 metrics={'accuracy': 52.322},
                 experiment_name="experiment-name-will-be-added-soon",
                 pod_count=1,
                 pod_selector={'matchLabels': {'app': 'tf-training',
                                               'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                                               'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'}},
                 namespace="mciesiel-dev", creation_timestamp="2018-05-17T14:05:52Z",
                 template_name="tf-training",
                 metadata={'clusterName': '', 'creationTimestamp': '2018-05-17T14:05:52Z', 'generation': 1,
                           'name': 'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                           'namespace': 'mciesiel-dev',
                           'resourceVersion': '435977',
                           'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-dev/runs/'
                                       'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                           'uid': '68af2c7a-59db-11e8-b5db-527100001250'},
                 start_timestamp=None,
                 end_timestamp=None),
             Run(name="exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training",
                 parameters=['mnist_single_node.py', '--data_dir', '/app'], state=RunStatus.COMPLETE,
                 metrics={'accuracy': 52.322}, experiment_name="experiment-name-will-be-added-soon", pod_count=1,
                 pod_selector={
                     'matchLabels': {'app': 'tf-training', 'draft': 'exp-mnist-single-node.py-18.05.17-16.05.56-2',
                                     'release': 'exp-mnist-single-node.py-18.05.17-16.05.56-2'}},
                 namespace="mciesiel-dev", creation_timestamp="2018-05-17T14:06:03Z",
                 template_name="tf-training",
                 metadata={'clusterName': '', 'creationTimestamp': '2018-05-17T14:06:03Z', 'generation': 1,
                           'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                           'namespace': 'mciesiel-dev',
                           'resourceVersion': '436010',
                           'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-dev/runs/'
                                       'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                           'uid': '6f13b47c-59db-11e8-b5db-527100001250'},
                 start_timestamp='2018-05-17T14:10:13Z',
                 end_timestamp='2018-05-17T14:15:41Z')]


@pytest.fixture()
def mock_k8s_api_client(mocker) -> CustomObjectsApi:
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')
    custom_objects_api_mocked_class = mocker.patch('platform_resources.platform_resource.PlatformResourceApiClient.get')
    return custom_objects_api_mocked_class.return_value


def test_list_runs(mock_k8s_api_client):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_RUNS_RESPONSE_RAW
    runs = Run.list()
    assert runs == TEST_RUNS


def test_list_runs_from_namespace(mock_k8s_api_client: CustomObjectsApi):
    raw_runs_single_namespace = dict(LIST_RUNS_RESPONSE_RAW)
    raw_runs_single_namespace['items'] = [raw_runs_single_namespace['items'][0]]
    mock_k8s_api_client.list_namespaced_custom_object.return_value = raw_runs_single_namespace

    runs = Run.list(namespace='namespace-1')

    assert [TEST_RUNS[0]] == runs


def test_list_runs_filter_status(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_RUNS_RESPONSE_RAW
    runs = Run.list(state_list=[RunStatus.QUEUED])
    assert [TEST_RUNS[0]] == runs


def test_list_runs_name_filter(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_RUNS_RESPONSE_RAW
    runs = Run.list(name_filter=TEST_RUNS[1].name)
    assert [TEST_RUNS[1]] == runs


def test_list_runs_invalid_name_filter(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_RUNS_RESPONSE_RAW
    with pytest.raises(InvalidRegularExpressionError):
        Run.list(name_filter='*')

def test_get_run_from_namespace(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.return_value = GET_RUN_RESPONSE_RAW
    run = Run.get(name=RUN_NAME, namespace=NAMESPACE)
    assert run is not None and type(run) is Run


def test_get_run_not_found(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.side_effect = ApiException(status=404)
    run = Run.get(name=RUN_NAME, namespace=NAMESPACE)
    assert run is None


def test_get_run_failure(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.get_namespaced_custom_object.side_effect = ApiException(status=500)
    with pytest.raises(ApiException):
        Run.get(name=RUN_NAME, namespace=NAMESPACE)

LIST_RUNS_RESPONSE_RAW = \
    {
        'apiVersion': 'aipg.intel.com/v1',
        'items': [
            {
                'apiVersion': 'aipg.intel.com/v1',
                'kind': 'Run',
                'metadata': {
                    'clusterName': '',
                    'creationTimestamp': '2018-05-17T14:05:52Z',
                    'generation': 1,
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                    'namespace': 'mciesiel-dev',
                    'resourceVersion': '435977',
                    'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-dev/runs/'
                                'exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training',
                    'uid': '68af2c7a-59db-11e8-b5db-527100001250'
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
                    'state': 'QUEUED',
                    'start-time': None,
                    'end-time': None
                }
            },
            {
                'apiVersion': 'aipg.intel.com/v1',
                'kind': 'Run',
                'metadata': {
                    'clusterName': '',
                    'creationTimestamp': '2018-05-17T14:06:03Z',
                    'generation': 1,
                    'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                    'namespace': 'mciesiel-dev',
                    'resourceVersion': '436010',
                    'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-dev/runs/'
                                'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
                    'uid': '6f13b47c-59db-11e8-b5db-527100001250'
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
        'clusterName': '',
        'creationTimestamp': '2018-05-17T14:06:03Z',
        'generation': 1,
        'name': 'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
        'namespace': 'mciesiel-dev',
        'resourceVersion': '436010',
        'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-dev/runs/'
                    'exp-mnist-single-node.py-18.05.17-16.05.56-2-tf-training',
        'uid': '6f13b47c-59db-11e8-b5db-527100001250'
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

@pytest.fixture()
def mock_k8s_run_api_client(mocker) -> CustomObjectsApi:
    for run in TEST_RUNS:
        mocker.patch.object(run, 'k8s_custom_object_api')
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')
    custom_objects_api_mocked_class = mocker.patch('platform_resources.platform_resource.PlatformResourceApiClient.get')
    return custom_objects_api_mocked_class.return_value

def test_update_run_success(mock_k8s_run_api_client):
    TEST_RUNS[0].k8s_custom_object_api.patch_namespaced_custom_object.return_value = LIST_RUNS_RESPONSE_RAW['items'][0]

    TEST_RUNS[0].update()

    assert TEST_RUNS[0].k8s_custom_object_api.patch_namespaced_custom_object.call_count == 1


def test_update_run_failure(mock_k8s_run_api_client):
    TEST_RUNS[0].k8s_custom_object_api.patch_namespaced_custom_object.side_effect = ApiException()

    with pytest.raises(ApiException):
        TEST_RUNS[0].update()


def test_add_run(mock_k8s_run_api_client: CustomObjectsApi):
    mock_k8s_run_api_client.create_namespaced_custom_object.return_value = GET_RUN_RESPONSE_RAW
    run = Run(name=RUN_NAME, experiment_name='fake')
    added_run = run.create(namespace=NAMESPACE)
    assert added_run is not None and type(added_run) is KubernetesObject


def test_add_run_failure(mock_k8s_run_api_client: CustomObjectsApi):
    mock_k8s_run_api_client.create_namespaced_custom_object.side_effect = ApiException(status=500)
    run = Run(name=RUN_NAME, experiment_name='fake')
    with pytest.raises(ApiException):
        run.create(namespace=NAMESPACE)
