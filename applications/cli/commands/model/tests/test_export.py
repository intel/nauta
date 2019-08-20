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

from cli_text_consts import ModelExportCmdTexts as Texts
from commands.model.common import workflow_description
from commands.model.export import export
from platform_resources.workflow import ArgoWorkflow, QUEUED_PHASE

FEM_NAME = "EXPORT_1"
SEM_NAME = "EXPORT_2"
FEM_PARAMETERS = "PARAMS_1"
SEM_PARAMETERS = "PARAMS_2"

FEM_START_DATE = '2000-01-01'
FEM_NAMESPACE = 'test-namespace'

TEST_AGROWORKFLOW = ArgoWorkflow(name=FEM_NAME, started_at=FEM_START_DATE, finished_at=None,
                                 namespace=FEM_NAMESPACE, phase=None)

TWO_MODEL_OUTPUT = [workflow_description(name=FEM_NAME, parameters=FEM_PARAMETERS),
                    workflow_description(name=SEM_NAME, parameters=SEM_PARAMETERS)]


def setup_mocks(mocker):
    mocker.patch('commands.model.export.get_kubectl_current_context_namespace',
                 return_value='fake-namespace')
    mocker.patch('platform_resources.workflow.ArgoWorkflow.from_yaml',
                 return_value=mocker.MagicMock())
    mocker.patch('platform_resources.workflow.ArgoWorkflow.get',
                 return_value=TEST_AGROWORKFLOW)
    mocker.patch('os.listdir', return_value=['openvino.yaml', 'tensorflow.yaml', 'some_other_file'])
    mocker.patch('commands.model.export.NAUTAConfigMap', return_value=mocker.MagicMock(registry='fake-addr'))
    mocker.patch('commands.model.export.Config')
    mocker.patch('os.path.isdir', return_value=True)


def test_export(mocker):
    setup_mocks(mocker)
    result = CliRunner().invoke(export, ["/fake/path", "openvino"])

    assert result.exit_code == 0
    assert "Successfully created export workflow" in result.output
    assert QUEUED_PHASE in result.output
    assert FEM_NAME in result.output
    assert FEM_START_DATE in result.output
    assert FEM_NAMESPACE in result.output


def test_export_inexistent_format(mocker):
    setup_mocks(mocker)

    result = CliRunner().invoke(export, ["/fake/path", "bad"])

    assert result.exit_code == 2
    assert "Format: bad does not exist. Choose from:" in result.output


def test_export_failure(mocker):
    setup_mocks(mocker)
    mocker.patch('platform_resources.workflow.ArgoWorkflow.from_yaml',
                 return_value=mocker.MagicMock(create=lambda: RuntimeError))

    result = CliRunner().invoke(export, ["/fake/path", "openvino"])

    assert result.exit_code == 1
    assert "Failed to create export workflow" in result.output


def test_export_list(mocker):
    mocker.patch("commands.model.export.get_list_of_workflows", return_value=TWO_MODEL_OUTPUT)

    result = CliRunner().invoke(export, ["list"])

    assert FEM_NAME in result.output
    assert SEM_NAME in result.output
    assert FEM_PARAMETERS in result.output
    assert SEM_PARAMETERS in result.output


def test_export_list_error(mocker):
    mocker.patch("commands.model.export.get_list_of_workflows", side_effect=RuntimeError)

    result = CliRunner().invoke(export, ["list"])

    assert Texts.EXPORT_LIST_ERROR_MSG in result.output


def test_export_missing_format(mocker):
    setup_mocks(mocker)
    result = CliRunner().invoke(export, ["wrong-option"])

    assert Texts.MISSING_EXPORT_FORMAT.format(formats=["openvino", "tensorflow"]) in result.output
