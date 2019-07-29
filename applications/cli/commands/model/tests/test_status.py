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

from commands.model.status import status
from cli_text_consts import ModelStatusCmdTexts as Texts
from platform_resources.workflow import ArgoWorkflow, ArgoWorkflowStep

MODEL_STEPS = [ArgoWorkflowStep(name="model1", phase="Running"),
               ArgoWorkflowStep(name="model2", phase="Failed")]


MODEL = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                     k8s_custom_object_api=MagicMock(spec=CustomObjectsApi),
                     phase='Succeeded',
                     steps=MODEL_STEPS,
                     body={'spec': {'templates': [{'container': {'command': ['other command']}}]}})


BUILD_MODEL = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                           k8s_custom_object_api=MagicMock(spec=CustomObjectsApi),
                           phase='Succeeded',
                           steps=MODEL_STEPS,
                           body={'spec': {'templates': [{'container': {'command': ['buildctl']}}]}})


class ModelStatusMocks:
    def __init__(self, mocker):
        self.get_namespace = mocker.patch('commands.model.status.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.list_workflow = mocker.patch('commands.model.status.ArgoWorkflow.list',
                                          return_value=[MODEL])


@pytest.fixture()
def status_mocks(mocker) -> ModelStatusMocks:
    return ModelStatusMocks(mocker=mocker)


def test_status(status_mocks: ModelStatusMocks):
    result = CliRunner().invoke(status, catch_exceptions=False)

    assert result.exit_code == 0
    assert MODEL.name in result.output
    assert MODEL.phase in result.output


def test_status_without_workflows(status_mocks: ModelStatusMocks):
    status_mocks.list_workflow.return_value = []
    result = CliRunner().invoke(status, catch_exceptions=False)
    assert result.exit_code == 0
    assert Texts.MODEL_NOT_FOUND in result.output


def test_status_other_error(status_mocks: ModelStatusMocks):
    status_mocks.list_workflow.side_effect = RuntimeError
    result = CliRunner().invoke(status)

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
