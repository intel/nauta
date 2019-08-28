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

import pytest


@pytest.fixture(autouse=True)
def mock_cli_validation(mocker):
    mocker.patch('util.cli_state.verify_cli_dependencies')
    mocker.patch('util.cli_state.verify_cli_config_path')
    mocker.patch('util.cli_state.verify_user_privileges')


@pytest.fixture(autouse=True)
def mock_k8s_client(mocker):
    mocker.patch('platform_resources.platform_resource.PlatformResourceApiClient.get')


@pytest.fixture(autouse=True)
def mock_check_nauta_pods(mocker):
    mocker.patch('util.system.check_nauta_pods')


@pytest.fixture(autouse=True)
def mock_get_click_context(mocker):
    click_context = mocker.patch('click.get_current_context')
    click_context.return_value.obj.force = False
    return click_context


@pytest.fixture()
def mock_exp_script_file(tmpdir):
    test_dir = tmpdir.mkdir('test-dir')
    test_file = test_dir.join('training_script.py')
    test_file.write('script code')
    return test_file.strpath
