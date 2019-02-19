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

from commands.workflow.view import view
from cli_text_consts import WorkflowViewTexts as Texts
from platform_resources.workflow import ArgoWorkflow

FAKE_WORKFLOW = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                             k8s_custom_object_api=MagicMock(spec=CustomObjectsApi),
                             status={'phase': 'Succeeded'})

FAKE_WORKFLOW_PATH = '/bla/workflow.yaml'


class WorkflowViewMocks:
    def __init__(self, mocker):
        self.get_namespace = mocker.patch('commands.workflow.view.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.get_workflow = mocker.patch('commands.workflow.view.ArgoWorkflow.get',
                                         return_value=FAKE_WORKFLOW)


@pytest.fixture()
def view_mocks(mocker) -> WorkflowViewMocks:
    return WorkflowViewMocks(mocker=mocker)


def test_view(view_mocks: WorkflowViewMocks):
    result = CliRunner().invoke(view, [FAKE_WORKFLOW.name], catch_exceptions=False)

    assert result.exit_code == 0
    assert FAKE_WORKFLOW.name in result.output
    assert FAKE_WORKFLOW.status['phase'] in result.output


def test_cancel_other_error(view_mocks: WorkflowViewMocks):
    view_mocks.get_workflow.side_effect = RuntimeError
    result = CliRunner().invoke(view, [FAKE_WORKFLOW.name])

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
