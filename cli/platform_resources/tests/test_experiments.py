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

from platform_resources.experiments import list_experiments, Experiment, ExperimentStatus, InvalidRegularExpressionError

TEST_RAW_EXPERIMENTS = {'apiVersion':
                            'aipg.intel.com/v1',
                        'items': [{'apiVersion': 'aipg.intel.com/v1',
                                   'kind': 'Experiment',
                                   'metadata':
                                       {'annotations':
                                            {'kubectl.kubernetes.io/last-applied-configuration':
                                                 '{"apiVersion":"aipg.intel.com/v1",'
                                                 '"kind":"Experiment",'
                                                 '"metadata":{"annotations":{},'
                                                 '"name":"test-experiment",'
                                                 '"namespace":"namespace-1"},'
                                                 '"spec":{"name":"test-experiment",'
                                                 '"parameters-spec":{"a":1,"b":2},'
                                                 '"state":"CREATING",'
                                                 '"template-name":"test-ex-template",'
                                                 '"template-namespace":"test-ex-namespace"}}\n'},
                                        'clusterName': '',
                                        'creationTimestamp': '2018-04-26T13:43:01Z',
                                        'generation': 1,
                                        'name': 'test-experiment',
                                        'namespace': 'namespace-1',
                                        'resourceVersion': '1350906',
                                        'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment',
                                        'uid': 'bd298c60-4957-11e8-96f7-527100002000'},
                                   'spec': {'name': 'test-experiment', 'parameters-spec': {'a': 1, 'b': 2},
                                            'state': 'CREATING', 'template-name': 'test-ex-template',
                                            'template-namespace': 'test-ex-namespace'}},
                                  {'apiVersion': 'aipg.intel.com/v1', 'kind': 'Experiment', 'metadata': {
                                      'annotations': {
                                          'kubectl.kubernetes.io/last-applied-configuration':
                                              '{"apiVersion":"aipg.intel.com/v1",'
                                              '"kind":"Experiment",'
                                              '"metadata":{"annotations":{},"name":"test-experiment-2",'
                                              '"namespace":"namespace-2"},'
                                              '"spec":{"name":"test-experiment-2","parameters-spec":{"a":1,"b":2},'
                                              '"state":"SUBMITTED","template-name":"test-ex-template",'
                                              '"template-namespace":"test-ex-namespace"}}\n'},
                                      'clusterName': '', 'creationTimestamp': '2018-05-08T13:05:04Z', 'generation': 1,
                                      'name': 'test-experiment-2', 'namespace': 'namespace-2',
                                      'resourceVersion': '3129108',
                                      'selfLink': '/apis/aipg.intel.com/v1/namespaces/mciesiel-ef-stack/experiments/test-experiment-2',
                                      'uid': '6ce9d932-52c0-11e8-ae8b-527100001230'},
                                   'spec': {'name': 'test-experiment-2', 'parameters-spec': {'a': 1, 'b': 2},
                                            'state': 'SUBMITTED', 'template-name': 'test-ex-template',
                                            'template-namespace': 'test-ex-namespace'}}], 'kind': 'ExperimentList',
                        'metadata': {'continue': '', 'resourceVersion': '3136167',
                                     'selfLink': '/apis/aipg.intel.com/v1/experiments'}}

TEST_EXPERIMENTS = [Experiment(name='test-experiment', parameters_spec={'a': 1, 'b': 2},
                               creation_timestamp='2018-04-26T13:43:01Z', submitter='namespace-1',
                               status='CREATING'),
                    Experiment(name='test-experiment-2', parameters_spec={'a': 1, 'b': 2},
                               creation_timestamp='2018-05-08T13:05:04Z', submitter='namespace-2',
                               status='SUBMITTED')]

@pytest.fixture()
def mock_k8s_api_client(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')


def test_list_experiments(mocker, mock_k8s_api_client):
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    mocked_custom_objects_api = custom_objects_api_mocked_class.return_value
    mocked_custom_objects_api.list_cluster_custom_object.return_value = TEST_RAW_EXPERIMENTS

    experiments = list_experiments()

    assert TEST_EXPERIMENTS == experiments


def test_list_experiments_from_namespace(mocker, mock_k8s_api_client):
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    mocked_custom_objects_api = custom_objects_api_mocked_class.return_value
    raw_experiments_single_namespace = dict(TEST_RAW_EXPERIMENTS)
    raw_experiments_single_namespace['items'] = [raw_experiments_single_namespace['items'][0]]
    mocked_custom_objects_api.list_namespaced_custom_object.return_value = raw_experiments_single_namespace

    experiments = list_experiments(namespace='namespace-1')

    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_filter_status(mocker, mock_k8s_api_client):
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    mocked_custom_objects_api = custom_objects_api_mocked_class.return_value
    mocked_custom_objects_api.list_cluster_custom_object.return_value = TEST_RAW_EXPERIMENTS

    experiments = list_experiments(state=ExperimentStatus.CREATING)

    assert [TEST_EXPERIMENTS[0]] == experiments


def test_list_experiments_name_filter(mocker, mock_k8s_api_client):
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    mocked_custom_objects_api = custom_objects_api_mocked_class.return_value
    mocked_custom_objects_api.list_cluster_custom_object.return_value = TEST_RAW_EXPERIMENTS

    experiments = list_experiments(name_filter='experiment-2')

    assert [TEST_EXPERIMENTS[1]] == experiments


def test_list_experiments_invalid_name_filter(mocker, mock_k8s_api_client):
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    mocked_custom_objects_api = custom_objects_api_mocked_class.return_value
    mocked_custom_objects_api.list_cluster_custom_object.return_value = TEST_RAW_EXPERIMENTS

    with pytest.raises(InvalidRegularExpressionError):
        list_experiments(name_filter='*')
