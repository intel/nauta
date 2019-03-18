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
from unittest.mock import MagicMock

from platform_resources.workflow import ArgoWorkflow


def test_parameters():
    test_workflow = ArgoWorkflow()
    test_workflow.body = {'spec': {'arguments': {'parameters': [{'name': 'test-param-1', 'value': 'test-value-1'},
                                                                {'name': 'test-param-2', 'value': 'test-value-2'}]}}}

    assert test_workflow.parameters == {'test-param-1': 'test-value-1', 'test-param-2': 'test-value-2'}


def test_set_parameters():
    test_workflow = ArgoWorkflow()
    test_workflow.body = {'spec': {'arguments': {'parameters': [{'name': 'test-param-1', 'value': 'test-value-1'},
                                                                {'name': 'test-param-2', 'value': 'test-value-2'}]}}}

    test_workflow.parameters = {'test-param-2': 'new-value'}

    assert test_workflow.parameters == {'test-param-1': 'test-value-1', 'test-param-2': 'new-value'}


def test_set_parameters_error():
    test_workflow = ArgoWorkflow()
    test_workflow.body = {'spec': {'arguments': {'parameters': [{'name': 'test-param-1', 'value': 'test-value-1'},
                                                                {'name': 'test-param-2'}]}}}

    with pytest.raises(KeyError):
        test_workflow.parameters = {'test-param-1': 'new-value'}


def test_wait_for_completion(mocker):
    workflow_status_mock = MagicMock()
    workflow_status_mock.phase = 'Succeeded'
    get_workflow_mock = mocker.patch('platform_resources.workflow.ArgoWorkflow.get', return_value=workflow_status_mock)

    test_workflow = ArgoWorkflow()
    test_workflow.wait_for_completion()

    assert get_workflow_mock.call_count == 1


def test_wait_for_completion_failure(mocker):
    workflow_status_mock = MagicMock()
    workflow_status_mock.phase = 'Failed'
    get_workflow_mock = mocker.patch('platform_resources.workflow.ArgoWorkflow.get', return_value=workflow_status_mock)

    test_workflow = ArgoWorkflow()
    with pytest.raises(RuntimeError):
        test_workflow.wait_for_completion()

    assert get_workflow_mock.call_count == 1
