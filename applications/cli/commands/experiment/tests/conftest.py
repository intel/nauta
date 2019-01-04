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
    mocker.patch('cli_state.verify_cli_dependencies')
    mocker.patch('cli_state.verify_cli_config_path')


@pytest.fixture(autouse=True)
def mock_k8s_client(mocker):
    mocker.patch('platform_resources.platform_resource.PlatformResourceApiClient.get')
