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

from commands.model.common import format_workflow_description, get_list_of_workflows, EXPORT_WORKFLOWS_LOCATION
from unittest.mock import patch, mock_open


FULL_WORKFLOW_FILE = """
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: test-workflow
spec:
  entrypoint: test-image
  arguments:
    parameters:
    - name: test-message
      value: test value
    - name: test-number
      value: test number value
  templates:
  - name: test-image
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["{{inputs.parameters.test-message}}"]
"""

LACK_OF_ARGS_WORKFLOW_FILE = """
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: test-workflow2
spec:
  entrypoint: test-image
  templates:
  - name: test-image
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay
      command: [cowsay]
"""


def test_format_workflow_description(mocker):
    m = mock_open(read_data=FULL_WORKFLOW_FILE)

    with patch("builtins.open", m):
        description = format_workflow_description("filename.txt")

    assert "test-workflow" == description.name


def test_format_workflow_description_wo_arguments(mocker):
    m = mock_open(read_data=LACK_OF_ARGS_WORKFLOW_FILE)

    with patch("builtins.open", m):
        description = format_workflow_description("filename.txt")

    assert "test-workflow2" == description.name


def test_list_of_workflows(tmpdir, mocker):
    exports_temp_dir = tmpdir.mkdir("workflows").mkdir("exports")

    first_workflow = exports_temp_dir.join("first_workflow.yaml")
    first_workflow.write(FULL_WORKFLOW_FILE)

    second_workflow = exports_temp_dir.join("second_workflow.yaml")
    second_workflow.write(LACK_OF_ARGS_WORKFLOW_FILE)

    fake_config = mocker.patch("commands.model.common.Config")
    fake_config.return_value.config_path = tmpdir

    list_of_workflows = get_list_of_workflows(EXPORT_WORKFLOWS_LOCATION)

    assert len(list_of_workflows) == 2

    first_found = False
    second_found = False

    for workflow in list_of_workflows:

        if workflow.name == "test-workflow":
            first_found = True

        if workflow.name == "test-workflow2":
            second_found = True

    assert first_found
    assert second_found
