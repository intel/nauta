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
from click.testing import CliRunner
from kubernetes.client import CustomObjectsApi

from commands.workflow.workflow_list import workflow_list
from cli_text_consts import WorkflowViewTexts as Texts
from platform_resources.workflow import ArgoWorkflow

FAKE_WORKFLOWS = [ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                               k8s_custom_object_api=MagicMock(spec=CustomObjectsApi),
                               status={'phase': 'Succeeded'}),
                  ArgoWorkflow(name='fake-workflow-2', namespace='fake-namespace',
                               k8s_custom_object_api=MagicMock(spec=CustomObjectsApi),
                               status={'phase': 'Failed'}),
                  ]


class WorkflowListMocks:
    def __init__(self, mocker):
        self.get_namespace = mocker.patch('commands.workflow.workflow_list.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.list_workflows = mocker.patch('commands.workflow.workflow_list.ArgoWorkflow.list',
                                           return_value=FAKE_WORKFLOWS)


@pytest.fixture()
def list_mocks(mocker) -> WorkflowListMocks:
    return WorkflowListMocks(mocker=mocker)


def test_list(list_mocks: WorkflowListMocks):
    result = CliRunner().invoke(workflow_list, [], catch_exceptions=False)

    assert result.exit_code == 0
    for workflow in FAKE_WORKFLOWS:
        assert workflow.name in result.output
        assert workflow.namespace in result.output


def test_cancel_other_error(list_mocks: WorkflowListMocks):
    list_mocks.list_workflows.side_effect = RuntimeError
    result = CliRunner().invoke(workflow_list, [])

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
