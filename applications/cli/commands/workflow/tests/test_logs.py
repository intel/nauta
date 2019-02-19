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

from commands.workflow.logs import logs
from cli_text_consts import WorkflowLogsTexts as Texts
from logs_aggregator.k8s_log_entry import LogEntry
from platform_resources.workflow import ArgoWorkflow

FAKE_WORKFLOW = ArgoWorkflow(name='fake-workflow', namespace='fake-namespace',
                             k8s_custom_object_api=MagicMock(spec=CustomObjectsApi))

FAKE_LOGS = [LogEntry(date='2018-04-17T09:28:39+00:00',
                      content='Warning: Unable to load '
                              '/usr/share/zoneinfo/right/Factory as time zone. Skipping it.\n',
                      pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                      namespace='default'),
             LogEntry(date='2018-04-17T09:28:49+00:00',
                      content='MySQL init process done. Ready for start up.\n',
                      pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                      namespace='default')]


class WorkflowLogsMocks:
    def __init__(self, mocker):
        self.get_namespace = mocker.patch('commands.workflow.logs.get_kubectl_current_context_namespace',
                                          return_value='fake-namespace')
        self.get_workflow = mocker.patch('commands.workflow.logs.ArgoWorkflow.get',
                                         return_value=FAKE_WORKFLOW)
        self.k8s_proxy = mocker.patch('commands.workflow.logs.K8sProxy')
        self.es_client = mocker.patch('commands.workflow.logs.K8sElasticSearchClient')
        self.workflow_logs_generator = mocker.patch.object(self.es_client.return_value,
                                                           'get_argo_workflow_logs_generator')


@pytest.fixture()
def logs_mocks(mocker) -> WorkflowLogsMocks:
    return WorkflowLogsMocks(mocker=mocker)


def test_logs(logs_mocks: WorkflowLogsMocks):
    logs_mocks.workflow_logs_generator.return_value = iter(FAKE_LOGS)
    result = CliRunner().invoke(logs, [FAKE_WORKFLOW.name], catch_exceptions=False)

    assert result.exit_code == 0
    for log in FAKE_LOGS:
        assert log.content in result.output


def test_logs_not_found(logs_mocks: WorkflowLogsMocks):
    logs_mocks.get_workflow.return_value = None
    result = CliRunner().invoke(logs, [FAKE_WORKFLOW.name])

    assert result.exit_code == 0
    assert Texts.NOT_FOUND_MSG.format(workflow_name=FAKE_WORKFLOW.name) in result.output


def test_cancel_other_error(logs_mocks: WorkflowLogsMocks):
    logs_mocks.es_client.side_effect = RuntimeError
    result = CliRunner().invoke(logs, [FAKE_WORKFLOW.name])

    assert result.exit_code == 1
    assert Texts.OTHER_ERROR_MSG in result.output
