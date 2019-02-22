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

from kubernetes.client import CustomObjectsApi

from platform_resources.experiment import ExperimentStatus, Experiment
from platform_resources.experiment_utils import generate_exp_name_and_labels
from util.exceptions import SubmitExperimentError, InvalidRegularExpressionError

EXPERIMENT_NAME = 'test-exp'
NAMESPACE = 'test-env'
TEMPLATE_NAME = 'template'
TEMPLATE_NAMESPACE = 'template-namespace-test'

TEST_EXPERIMENTS = [Experiment(name='test-experiment-old', parameters_spec=['a 1', 'b 2'],
                               creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                               state=ExperimentStatus.CREATING, template_name='test-ex-template',
                               template_namespace='test-ex-namespace',
                               metadata={'annotations':
                                            {'kubectl.kubernetes.io/last-applied-configuration':
                                                 '{"apiVersion":"aipg.intel.com/v1",'
                                                 '"kind":"Experiment",'
                                                 '"metadata":{"annotations":{},'
                                                 '"name":"test-experiment-old",'
                                                 '"namespace":"namespace-1"},'
                                                 '"spec":{"name":"test-experiment-old",'
                                                 '"parameters-spec":["a 1", "b 2"],'
                                                 '"state":"CREATING",'
                                                 '"template-name":"test-ex-template",'
                                                 '"template-namespace":"test-ex-namespace"}}\n'},
                                        'clusterName': '',
                                        'creationTimestamp': '2018-04-26T13:43:01Z',
                                        'labels': {'name_origin': 'test-experiment-new', 'script_name': 'mnist_single_node.py'},
                                        'generation': 1,
                                        'name': 'test-experiment-old',
                                        'namespace': 'namespace-1',
                                        'resourceVersion': '1350906',
                                        'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment',
                                        'uid': 'bd298c60-4957-11e8-96f7-527100002000'}),
                    Experiment(name='test-experiment-new', parameters_spec=['a 1', 'b 2'],
                               creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                               state=ExperimentStatus.SUBMITTED, template_name='test-ex-template',
                               template_namespace='test-ex-namespace',
                               metadata={
                                        'annotations': {
                                            'kubectl.kubernetes.io/last-applied-configuration':
                                                '{"apiVersion":"aipg.intel.com/v1",'
                                                '"kind":"Experiment",'
                                                '"metadata":{"annotations":{},"name":"test-experiment-2",'
                                                '"namespace":"namespace-2"},'
                                                '"spec":{"name":"test-experiment-new","parameters-spec":["a 1", "b 2"],'
                                                '"state":"SUBMITTED","template-name":"test-ex-template",'
                                                '"template-namespace":"test-ex-namespace"}}\n'},
                                        'clusterName': '', 'creationTimestamp': '2018-05-08T13:05:04Z',
                                        'labels': {'name_origin': 'test-experiment-new', 'script_name': 'mnist_single_node.py'},
                                        'generation': 1,
                                        'name': 'test-experiment-new', 'namespace': 'namespace-2',
                                        'resourceVersion': '3129108',
                                        'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment-2',
                                        'uid': '6ce9d932-52c0-11e8-ae8b-527100001230'})]

@pytest.fixture()
def mock_platform_resources_api_client(mocker) -> CustomObjectsApi:
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')
    custom_objects_api_mocked_class = mocker.patch('platform_resources.platform_resource.PlatformResourceApiClient.get')
    return custom_objects_api_mocked_class.return_value


def test_create_experiment(mock_platform_resources_api_client: CustomObjectsApi):
    mock_platform_resources_api_client.create_namespaced_custom_object.return_value = ADD_EXPERIMENT_RESPONSE_RAW
    exp = Experiment(name=EXPERIMENT_NAME, template_name=TEMPLATE_NAME, template_namespace=TEMPLATE_NAMESPACE)
    result = exp.create(namespace=NAMESPACE)

    assert result
    assert result.spec.name == EXPERIMENT_NAME
    assert result.spec.template_name == TEMPLATE_NAME
    assert result.spec.template_namespace == TEMPLATE_NAMESPACE
    assert result.spec.state == ExperimentStatus.CREATING
    assert result.metadata.name == EXPERIMENT_NAME
    assert result.metadata.namespace == NAMESPACE

def test_list_experiments(mock_platform_resources_api_client: CustomObjectsApi):
    mock_platform_resources_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = Experiment.list()
    assert TEST_EXPERIMENTS == experiments


def test_list_experiments_from_namespace(mock_platform_resources_api_client: CustomObjectsApi):
    raw_experiments_single_namespace = dict(LIST_EXPERIMENTS_RESPONSE_RAW)
    raw_experiments_single_namespace['items'] = [raw_experiments_single_namespace['items'][0]]
    mock_platform_resources_api_client.list_namespaced_custom_object.return_value = raw_experiments_single_namespace

    experiments = Experiment.list(namespace='namespace-1')

    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_filter_status(mock_platform_resources_api_client: CustomObjectsApi):
    mock_platform_resources_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = Experiment.list(state=ExperimentStatus.CREATING)
    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_name_filter(mock_platform_resources_api_client: CustomObjectsApi):
    mock_platform_resources_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = Experiment.list(name_filter='test-experiment-new')
    assert [TEST_EXPERIMENTS[1]] == experiments


def test_list_experiments_invalid_name_filter(mock_platform_resources_api_client: CustomObjectsApi):
    mock_platform_resources_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    with pytest.raises(InvalidRegularExpressionError):
        Experiment.list(name_filter='*')

ADD_EXPERIMENT_RESPONSE_RAW = {'apiVersion': 'aipg.intel.com/v1', 'kind': 'Experiment',
                               'metadata': {'name': EXPERIMENT_NAME, 'namespace': NAMESPACE},
                               'spec': {'name': EXPERIMENT_NAME, 'parameters-spec': [], 'state': 'CREATING',
                                        'template-name': TEMPLATE_NAME, 'template-namespace': TEMPLATE_NAMESPACE}}

GET_EXPERIMENT_RESPONSE_RAW = {'apiVersion': 'aipg.intel.com/v1', 'kind': 'Experiment',
                               'metadata': {'name': EXPERIMENT_NAME, 'namespace': NAMESPACE,
                                            'creationTimestamp': '2018-04-26T13:43:01Z'},
                               'spec': {'name': EXPERIMENT_NAME, 'parameters-spec': [], 'state': 'CREATING',
                                        'template-name': TEMPLATE_NAME, 'template-namespace': TEMPLATE_NAMESPACE}}

LIST_EXPERIMENTS_EMPTY_RESPONSE_RAW = {'items': []}
LIST_EXPERIMENTS_RESPONSE_RAW = {'apiVersion':
                                     'aipg.intel.com/v1',
                                 'items': [{'apiVersion': 'aipg.intel.com/v1',
                                            'kind': 'Experiment',
                                            'metadata':
                                                {'annotations':
                                                     {'kubectl.kubernetes.io/last-applied-configuration':
                                                          '{"apiVersion":"aipg.intel.com/v1",'
                                                          '"kind":"Experiment",'
                                                          '"metadata":{"annotations":{},'
                                                          '"name":"test-experiment-old",'
                                                          '"namespace":"namespace-1"},'
                                                          '"spec":{"name":"test-experiment-old",'
                                                          '"parameters-spec":["a 1", "b 2"],'
                                                          '"state":"CREATING",'
                                                          '"template-name":"test-ex-template",'
                                                          '"template-namespace":"test-ex-namespace"}}\n'},
                                                 'clusterName': '',
                                                 'creationTimestamp': '2018-04-26T13:43:01Z',
                                                 'labels': {'name_origin': 'test-experiment-new', 'script_name': 'mnist_single_node.py'},
                                                 'generation': 1,
                                                 'name': 'test-experiment-old',
                                                 'namespace': 'namespace-1',
                                                 'resourceVersion': '1350906',
                                                 'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment',
                                                 'uid': 'bd298c60-4957-11e8-96f7-527100002000'},
                                            'spec': {'name': 'test-experiment-old', 'parameters-spec': ['a 1', 'b 2'],
                                                     'state': 'CREATING', 'template-name': 'test-ex-template',
                                                     'template-namespace': 'test-ex-namespace'}},
                                           {'apiVersion': 'aipg.intel.com/v1', 'kind': 'Experiment', 'metadata': {
                                               'annotations': {
                                                   'kubectl.kubernetes.io/last-applied-configuration':
                                                       '{"apiVersion":"aipg.intel.com/v1",'
                                                       '"kind":"Experiment",'
                                                       '"metadata":{"annotations":{},"name":"test-experiment-2",'
                                                       '"namespace":"namespace-2"},'
                                                       '"spec":{"name":"test-experiment-new","parameters-spec":["a 1", "b 2"],'
                                                       '"state":"SUBMITTED","template-name":"test-ex-template",'
                                                       '"template-namespace":"test-ex-namespace"}}\n'},
                                               'clusterName': '', 'creationTimestamp': '2018-05-08T13:05:04Z',
                                               'labels': {'name_origin': 'test-experiment-new', 'script_name': 'mnist_single_node.py'},
                                               'generation': 1,
                                               'name': 'test-experiment-new', 'namespace': 'namespace-2',
                                               'resourceVersion': '3129108',
                                               'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment-2',
                                               'uid': '6ce9d932-52c0-11e8-ae8b-527100001230'},
                                            'spec': {'name': 'test-experiment-new', 'parameters-spec': ['a 1', 'b 2'],
                                                     'state': 'SUBMITTED', 'template-name': 'test-ex-template',
                                                     'template-namespace': 'test-ex-namespace'}}],
                                 'kind': 'ExperimentList',
                                 'metadata': {'continue': '', 'resourceVersion': '3136167',
                                              'selfLink': '/apis/aipg.intel.com/v1/experiments'}}
