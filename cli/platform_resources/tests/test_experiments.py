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

from platform_resources.experiment_model import ExperimentStatus, Experiment
from platform_resources.experiments import list_experiments, InvalidRegularExpressionError, \
    add_experiment, generate_exp_name_and_labels
from util.exceptions import SubmitExperimentError

EXPERIMENT_NAME = 'test-exp'
NAMESPACE = 'test-env'
TEMPLATE_NAME = 'template'
TEMPLATE_NAMESPACE = 'template-namespace-test'

TEST_EXPERIMENTS = [Experiment(name='test-experiment-old', parameters_spec=['a 1', 'b 2'],
                               creation_timestamp='2018-04-26T13:43:01Z', submitter='namespace-1',
                               state=ExperimentStatus.CREATING, template_name='test-ex-template',
                               template_namespace='test-ex-namespace'),
                    Experiment(name='test-experiment-new', parameters_spec=['a 1', 'b 2'],
                               creation_timestamp='2018-05-08T13:05:04Z', submitter='namespace-2',
                               state=ExperimentStatus.SUBMITTED, template_name='test-ex-template',
                               template_namespace='test-ex-namespace')]


@pytest.fixture()
def mock_k8s_api_client(mocker) -> CustomObjectsApi:
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    return custom_objects_api_mocked_class.return_value


def test_list_experiments(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = list_experiments()
    assert TEST_EXPERIMENTS == experiments


def test_list_experiments_from_namespace(mock_k8s_api_client: CustomObjectsApi):
    raw_experiments_single_namespace = dict(LIST_EXPERIMENTS_RESPONSE_RAW)
    raw_experiments_single_namespace['items'] = [raw_experiments_single_namespace['items'][0]]
    mock_k8s_api_client.list_namespaced_custom_object.return_value = raw_experiments_single_namespace

    experiments = list_experiments(namespace='namespace-1')

    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_filter_status(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = list_experiments(state=ExperimentStatus.CREATING)
    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_name_filter(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    experiments = list_experiments(name_filter='test-experiment-new')
    assert [TEST_EXPERIMENTS[1]] == experiments


def test_list_experiments_invalid_name_filter(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    with pytest.raises(InvalidRegularExpressionError):
        list_experiments(name_filter='*')


def test_add_experiment(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.create_namespaced_custom_object.return_value = ADD_EXPERIMENT_RESPONSE_RAW
    exp = Experiment(name=EXPERIMENT_NAME, template_name=TEMPLATE_NAME, template_namespace=TEMPLATE_NAMESPACE)
    result = add_experiment(exp, NAMESPACE)

    assert result
    assert result.spec.name == EXPERIMENT_NAME
    assert result.spec.template_name == TEMPLATE_NAME
    assert result.spec.template_namespace == TEMPLATE_NAMESPACE
    assert result.spec.state == ExperimentStatus.CREATING
    assert result.metadata.name == EXPERIMENT_NAME
    assert result.metadata.namespace == NAMESPACE


def test_generate_experiment_name_if_name_provided_and_exp_no_exists(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_namespaced_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    result, labels = generate_exp_name_and_labels('script', NAMESPACE, 'experiment-not-exist-yet')
    assert result == 'experiment-not-exist-yet'
    assert mock_k8s_api_client.list_namespaced_custom_object.call_count == 1


def test_generate_experiment_name_if_exp_exists_and_name_provided(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_namespaced_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    with pytest.raises(SubmitExperimentError):
        generate_exp_name_and_labels('script', NAMESPACE, 'test-experiment-old')
    assert mock_k8s_api_client.list_namespaced_custom_object.call_count == 1


def test_generate_experiment_name_if_exp_exists_and_name_no_provided(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_namespaced_custom_object.return_value = LIST_EXPERIMENTS_RESPONSE_RAW
    result, labels = generate_exp_name_and_labels('script', NAMESPACE)
    assert result == 'test-experiment-new-3'
    assert mock_k8s_api_client.list_namespaced_custom_object.call_count == 1


def test_generate_experiment_name_if_name_not_provided_and_exp_no_exists(mock_k8s_api_client: CustomObjectsApi):
    mock_k8s_api_client.list_namespaced_custom_object.return_value = LIST_EXPERIMENTS_EMPTY_RESPONSE_RAW
    result, labels = generate_exp_name_and_labels('script.py', NAMESPACE)
    assert 'script-py' in result
    assert mock_k8s_api_client.list_namespaced_custom_object.call_count == 2


ADD_EXPERIMENT_RESPONSE_RAW = {'apiVersion': 'aipg.intel.com/v1', 'kind': 'Experiment',
                               'metadata': {'name': EXPERIMENT_NAME, 'namespace': NAMESPACE},
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
