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

from commands.workflow.cancel import cancel
from cli_text_consts import WorkflowDeleteTexts as Texts
from platform_resources.workflow import ArgoWorkflow

FAKE_WORKFLOW = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                             k8s_custom_object_api=MagicMock(spec=CustomObjectsApi))


class WorkflowCancelMocks:
    def __init__(self, mocker):
        self.get_namespace = mocker.patch('commands.workflow.cancel.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.get_workflow = mocker.patch('commands.workflow.cancel.ArgoWorkflow.get',
                                         return_value=FAKE_WORKFLOW)
        self.delete_workflow = mocker.patch.object(self.get_workflow.return_value, 'delete')


@pytest.fixture()
def cancel_mocks(mocker) -> WorkflowCancelMocks:
    return WorkflowCancelMocks(mocker=mocker)


def test_cancel(cancel_mocks: WorkflowCancelMocks):
    result = CliRunner().invoke(cancel, [FAKE_WORKFLOW.name], catch_exceptions=False)

    assert result.exit_code == 0
    assert Texts.SUCCESS_MSG.format(workflow_name=FAKE_WORKFLOW.name) in result.output


def test_cancel_not_found(cancel_mocks: WorkflowCancelMocks):
    cancel_mocks.get_workflow.return_value = None
    result = CliRunner().invoke(cancel, [FAKE_WORKFLOW.name])

    assert result.exit_code == 0
    assert Texts.NOT_FOUND_MSG.format(workflow_name=FAKE_WORKFLOW.name) in result.output


def test_cancel_other_error(cancel_mocks: WorkflowCancelMocks):
    cancel_mocks.delete_workflow.side_effect = RuntimeError
    result = CliRunner().invoke(cancel, [FAKE_WORKFLOW.name])

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
