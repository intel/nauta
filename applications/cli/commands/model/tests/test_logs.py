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

from click.testing import CliRunner
from unittest.mock import patch, mock_open

from commands.model import logs
from logs_aggregator.k8s_log_entry import LogEntry
from platform_resources.workflow import ArgoWorkflow
from cli_text_consts import ModelExportCommonTexts as ModelExportCommonTexts
from cli_text_consts import CmdsCommonTexts as CmdsCommonTexts

POD_NAME = 'openvinoskvrx'

TEST_LOG_ENTRIES = [LogEntry(date='2018-04-17T09:28:39+00:00',
                             content='TensorFlow specific parameters:\n',
                             pod_name=POD_NAME,
                             namespace='default'),
                    LogEntry(date='2018-04-17T09:28:49+00:00',
                             content='[ SUCCESS ] BIN file: /mnt/output/home/openvinoskvrx/saved_model.bin\n',
                             pod_name=POD_NAME,
                             namespace='default')]


def test_show_logs_success(mocker):
    es_client_mock = mocker.patch('commands.model.common.K8sElasticSearchClient')
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_argo_workflow_logs_generator.return_value = TEST_LOG_ENTRIES

    gk_host_mock = mocker.patch("commands.model.common.get_kubectl_host")
    ga_key_mock = mocker.patch("commands.model.common.get_api_key")

    get_current_namespace_mock = mocker.patch('commands.model.common.get_kubectl_current_context_namespace')
    fake_operation_name = POD_NAME
    list_operations_mock = mocker.patch('commands.model.common.ArgoWorkflow.list')
    list_operations_mock.return_value = [ArgoWorkflow(name=fake_operation_name)]

    runner = CliRunner()
    result = runner.invoke(logs.logs, [fake_operation_name])

    assert gk_host_mock.call_count == 1, "kubectl host was not retrieved"
    assert ga_key_mock.call_count == 1, "api ket was not retrieved"
    assert get_current_namespace_mock.call_count == 1, 'namespace was not retrieved'
    assert list_operations_mock.call_count == 1, 'operation was not retrieved'
    assert es_client_instance.get_argo_workflow_logs_generator.call_count == 1, 'operation logs were not retrieved'
    assert POD_NAME in result.output


def test_show_logs_failure(mocker):
    es_client_mock = mocker.patch('commands.model.common.K8sElasticSearchClient')
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_argo_workflow_logs_generator.side_effect = RuntimeError

    gk_host_mock = mocker.patch("commands.model.common.get_kubectl_host")
    ga_key_mock = mocker.patch("commands.model.common.get_api_key")

    get_current_namespace_mock = mocker.patch('commands.model.common.get_kubectl_current_context_namespace')
    fake_operation_name = POD_NAME
    list_operations_mock = mocker.patch('commands.model.common.ArgoWorkflow.list')
    list_operations_mock.return_value = [ArgoWorkflow(name=fake_operation_name)]

    runner = CliRunner()

    result = runner.invoke(logs.logs, [fake_operation_name])

    assert gk_host_mock.call_count == 1, "kubectl host was not retrieved"
    assert ga_key_mock.call_count == 1, "api ket was not retrieved"
    assert get_current_namespace_mock.call_count == 1, 'namespace was not retrieved'
    assert list_operations_mock.call_count == 1, 'operation was not retrieved'
    assert es_client_instance.get_argo_workflow_logs_generator.call_count == 1, 'operation logs were not retrieved'
    assert result.exit_code == 1


def test_show_logs_too_many_params(mocker):
    runner = CliRunner()

    result = runner.invoke(logs.logs, [POD_NAME, '-m', 'match_name'])

    assert ModelExportCommonTexts.NAME_M_BOTH_GIVEN_ERROR_MSG in result.output


def test_show_logs_lack_of_params(mocker):
    runner = CliRunner()

    result = runner.invoke(logs.logs)

    assert ModelExportCommonTexts.NAME_M_NONE_GIVEN_ERROR_MSG in result.output


def test_show_logs_to_file_error(mocker):
    es_client_mock = mocker.patch('commands.model.common.K8sElasticSearchClient')
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_argo_workflow_logs_generator.return_value = TEST_LOG_ENTRIES

    gk_host_mock = mocker.patch("commands.model.common.get_kubectl_host")
    ga_key_mock = mocker.patch("commands.model.common.get_api_key")

    get_current_namespace_mock = mocker.patch("commands.model.common.get_kubectl_current_context_namespace")

    fake_operation_name = POD_NAME
    list_operations_mock = mocker.patch('commands.model.common.ArgoWorkflow.list')
    list_operations_mock.return_value = [ArgoWorkflow(name=fake_operation_name)]

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m) as open_mock:
        exception = RuntimeError()
        exception.message = "Cause of an error"
        open_mock.return_value.__enter__.side_effect = exception
        result = runner.invoke(logs.logs, [fake_operation_name, '-o'], input='y')

    assert gk_host_mock.call_count == 1, "kubectl host was not retrieved"
    assert ga_key_mock.call_count == 1, "api ket was not retrieved"
    assert CmdsCommonTexts.LOGS_STORING_ERROR in result.output
    assert get_current_namespace_mock.call_count == 1, "namespace was not retrieved"
    assert list_operations_mock.call_count == 1, "operation was not retrieved"
    assert es_client_instance.get_argo_workflow_logs_generator.call_count == 1, "operation logs were not retrieved"


def test_show_logs_to_file_success(mocker):
    es_client_mock = mocker.patch("commands.model.common.K8sElasticSearchClient")
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_argo_workflow_logs_generator.return_value = TEST_LOG_ENTRIES

    gk_host_mock = mocker.patch("commands.model.common.get_kubectl_host")
    ga_key_mock = mocker.patch("commands.model.common.get_api_key")

    get_current_namespace_mock = mocker.patch("commands.model.common.get_kubectl_current_context_namespace")
    fake_operation_name = POD_NAME
    list_operations_mock = mocker.patch('commands.model.common.ArgoWorkflow.list')
    list_operations_mock.return_value = [ArgoWorkflow(name=fake_operation_name)]

    runner = CliRunner()
    m = mock_open()
    with patch("builtins.open", m) as open_mock:
        runner.invoke(logs.logs, [fake_operation_name, '-o'], input='y')

    assert gk_host_mock.call_count == 1, "kubectl host was not retrieved"
    assert ga_key_mock.call_count == 1, "api ket was not retrieved"
    assert get_current_namespace_mock.call_count == 1, "namespace was not retrieved"
    assert list_operations_mock.call_count == 1, "operation was not retrieved"
    assert es_client_instance.get_argo_workflow_logs_generator.call_count == 1, "operation logs were not retrieved"
    assert open_mock.call_count == 1, "File wasn't saved."


def test_show_logs_match(mocker):
    es_client_mock = mocker.patch("commands.model.common.K8sElasticSearchClient")

    es_client_instance = es_client_mock.return_value
    es_client_instance.get_argo_workflow_logs_generator.return_value = TEST_LOG_ENTRIES

    gk_host_mock = mocker.patch("commands.model.common.get_kubectl_host")
    ga_key_mock = mocker.patch("commands.model.common.get_api_key")

    get_current_namespace_mock = mocker.patch('commands.model.common.get_kubectl_current_context_namespace')
    fake_operation_name = 'fake_operation'
    fake_operation_1_name = 'fake-operation-1'
    fake_operation_2_name = 'fake-operation-2'
    list_operations_mock = mocker.patch('commands.model.common.ArgoWorkflow.list')
    list_operations_mock.return_value = [ArgoWorkflow(name=fake_operation_1_name),
                                         ArgoWorkflow(name=fake_operation_2_name)]

    runner = CliRunner()
    result = runner.invoke(logs.logs, ['-m', fake_operation_name])

    assert gk_host_mock.call_count == 1, "kubectl host was not retrieved"
    assert ga_key_mock.call_count == 1, "api ket was not retrieved"
    assert get_current_namespace_mock.call_count == 1, 'namespace was not retrieved'
    assert list_operations_mock.call_count == 1, 'operation was not retrieved'
    assert es_client_instance.get_argo_workflow_logs_generator.call_count == 2, 'operation logs were not retrieved'

    assert fake_operation_1_name in result.output
    assert fake_operation_2_name in result.output
