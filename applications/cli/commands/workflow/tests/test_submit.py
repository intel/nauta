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

from commands.workflow.submit import submit
from cli_text_consts import WorkflowSubmitTexts as Texts
from platform_resources.workflow import ArgoWorkflow

FAKE_WORKFLOW = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                             k8s_custom_object_api=MagicMock(spec=CustomObjectsApi))

FAKE_WORKFLOW_PATH = '/bla/workflow.yaml'


class WorkflowSubmitMocks:
    def __init__(self, mocker, tmpdir):
        self.get_namespace = mocker.patch('commands.workflow.submit.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.from_yaml = mocker.patch('commands.workflow.submit.ArgoWorkflow.from_yaml',
                                      return_value=FAKE_WORKFLOW)
        self.create_workflow = mocker.patch.object(self.from_yaml.return_value, 'create')

        self.fake_workflow_spec_file = tmpdir.mkdir('test-worfklow').join('workflow.yaml')
        self.fake_workflow_spec_file.write('kind: Workflow')
        self.fake_workflow_spec_path = self.fake_workflow_spec_file.strpath


@pytest.fixture()
def submit_mocks(mocker, tmpdir) -> WorkflowSubmitMocks:
    return WorkflowSubmitMocks(mocker=mocker, tmpdir=tmpdir)


def test_submit(submit_mocks: WorkflowSubmitMocks):
    result = CliRunner().invoke(submit, [submit_mocks.fake_workflow_spec_path], catch_exceptions=False)

    assert result.exit_code == 0
    assert FAKE_WORKFLOW.name in result.output


def test_submit_io_error(submit_mocks: WorkflowSubmitMocks):
    submit_mocks.from_yaml.side_effect = IOError
    result = CliRunner().invoke(submit, [submit_mocks.fake_workflow_spec_path])

    assert result.exit_code == 1
    assert Texts.LOAD_SPEC_ERROR_MSG.format(msg='') in result.output


def test_cancel_other_error(submit_mocks: WorkflowSubmitMocks):
    submit_mocks.create_workflow.side_effect = RuntimeError
    result = CliRunner().invoke(submit, [submit_mocks.fake_workflow_spec_path])

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
