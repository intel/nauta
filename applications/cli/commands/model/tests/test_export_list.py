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

from commands.model.export_list import export_list
from commands.model.common import workflow_description
from cli_text_consts import ModelExportListCmdTexts as Texts


FEM_NAME = "EXPORT_1"
SEM_NAME = "EXPORT_2"
FEM_PARAMETERS = "parameters 1"
SEM_PARAMETERS = None

TWO_MODEL_OUTPUT = [workflow_description(name=FEM_NAME, parameters=FEM_PARAMETERS),
                    workflow_description(name=SEM_NAME, parameters=SEM_PARAMETERS)]


def test_export_list(mocker):
    mocker.patch("commands.model.export_list.get_list_of_workflows", return_value=TWO_MODEL_OUTPUT)

    result = CliRunner().invoke(export_list)

    assert FEM_NAME in result.output
    assert SEM_NAME in result.output
    assert FEM_PARAMETERS in result.output
    assert "---" in result.output


def test_export_list_error(mocker):
    mocker.patch("commands.model.export_list.get_list_of_workflows", side_effect=RuntimeError)

    result = CliRunner().invoke(export_list)

    assert Texts.EXPORT_LIST_ERROR_MSG in result.output
