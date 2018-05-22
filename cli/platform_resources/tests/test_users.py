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

from platform_resources.user_model import User, UserStatus
from platform_resources.users import list_users

TEST_USERS = [User(name='test-dev', uid=1, password='bla', state=UserStatus.DEFINED,
                   creation_timestamp='2018-05-17T12:49:04Z',
                   experiment_runs=[]),
              User(name='test-user', uid=100, password='bla',
                   state=UserStatus.DEFINED, creation_timestamp='2018-05-17T11:42:22Z',
                   experiment_runs=[])]


@pytest.fixture()
def mock_k8s_api_client(mocker) -> CustomObjectsApi:
    mocker.patch('kubernetes.config.load_kube_config')
    mocker.patch('kubernetes.client.ApiClient')
    custom_objects_api_mocked_class = mocker.patch('kubernetes.client.CustomObjectsApi')
    return custom_objects_api_mocked_class.return_value


def test_list_users(mock_k8s_api_client, mocker):
    mocker.patch('platform_resources.users.list_runs')
    mock_k8s_api_client.list_cluster_custom_object.return_value = LIST_USERS_RESPONSE_RAW
    users = list_users()
    assert users == TEST_USERS


LIST_USERS_RESPONSE_RAW = {'apiVersion': 'aipg.intel.com/v1',
                           'items': [
                               {'apiVersion': 'aipg.intel.com/v1',
                                'kind': 'User',
                                'metadata': {'annotations':
                                                 {
                                                     'kubectl.kubernetes.io/last-applied-configuration':
                                                         '{"apiVersion":"aipg.intel.com/v1","kind":'
                                                         '"User",'
                                                         '"metadata":{"annotations":{},"name":"test-dev","namespace":""},'
                                                         '"spec":{"password":"bla","state":"DEFINED","uid":1}}\n'},
                                             'clusterName': '', 'creationTimestamp': '2018-05-17T12:49:04Z',
                                             'generation': 1, 'name': 'test-dev', 'namespace': '',
                                             'resourceVersion': '429638',
                                             'selfLink': '/apis/aipg.intel.com/v1/users/test-dev',
                                             'uid': 'ae1a69e8-59d0-11e8-b5db-527100001250'},
                                'spec': {'password': 'bla', 'state': 'DEFINED', 'uid': 1}},
                               {'apiVersion': 'aipg.intel.com/v1', 'kind': 'User',
                                'metadata': {'annotations': {
                                   'kubectl.kubernetes.io/last-applied-configuration':
                                       '{"apiVersion":"aipg.intel.com/v1",'
                                        '"kind":"User",'
                                        '"metadata":{"annotations":{},"name":"test-user","namespace":""},'
                                        '"spec":{"password":"bla","state":"DEFINED","uid":100}}\n'},
                                                 'clusterName': '',
                                                 'creationTimestamp': '2018-05-17T11:42:22Z',
                                                 'generation': 1,
                                                 'name': 'test-user',
                                                 'namespace': '',
                                                 'resourceVersion': '424142',
                                                 'selfLink': '/apis/aipg.intel.com/v1/users/test-user',
                                                 'uid': '5d13e21f-59c7-11e8-b5db-527100001250'},
                                'spec': {'password': 'bla', 'state': 'DEFINED', 'uid': 100}}], 'kind': 'UserList',
                           'metadata': {'continue': '', 'resourceVersion': '434920',
                                        'selfLink': '/apis/aipg.intel.com/v1/users'}}
