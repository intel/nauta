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

from commands.model.export import export


def setup_mocks(mocker):
    mocker.patch('commands.model.export.get_kubectl_current_context_namespace',
                 return_value='fake-namespace')
    mocker.patch('platform_resources.workflow.ArgoWorkflow.from_yaml',
                 return_value=mocker.MagicMock())
    mocker.patch('os.listdir', return_value=['openvino.yaml', 'tensorflow.yaml', 'some_other_file'])
    mocker.patch('commands.model.export.NAUTAConfigMap', return_value=mocker.MagicMock(registry='fake-addr'))
    mocker.patch('commands.model.export.Config')
    mocker.patch('os.path.isdir', return_value=True)


def test_export(mocker):
    setup_mocks(mocker)
    result = CliRunner().invoke(export, ["/fake/path", "openvino"])

    assert result.exit_code == 0
    assert "Successfully created export workflow" in result.output


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
