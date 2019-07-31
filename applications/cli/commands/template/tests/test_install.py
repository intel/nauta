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
from commands.template.install import install


def test_install_template(mocker):
    get_config_path_mock = mocker.patch('commands.template.install.Config.get_config_path', return_value='node_config/')
    get_repo_addr_mock = mocker.patch('commands.template.install.get_repository_address', return_value='http://repo')
    load_remote_template_mock = mocker.patch('commands.template.install.load_remote_template',
                                             return_value=dict(remote_version='1'))
    get_local_templates_mock = mocker.patch('commands.template.install.get_local_templates', return_value=dict())
    download_remote_template_mock = mocker.patch('commands.template.install.download_remote_template')
    override_values_in_packs_mock = mocker.patch('commands.template.install.update_resources_in_packs')
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('shutil.rmtree')

    runner = CliRunner()
    runner.invoke(install, ['template_name'])

    assert get_config_path_mock.call_count == 1, "config path wasn't retrieved"
    assert get_repo_addr_mock.call_count == 1, "repository address wasn't retrieved"
    assert load_remote_template_mock.call_count == 1, "remote template wasn't loaded"
    assert get_local_templates_mock.call_count == 1, "local templates weren't retrieved"
    assert download_remote_template_mock.call_count == 1, "remote template wasn't downloaded"
    assert override_values_in_packs_mock.call_count == 1, "resources in downloaded pack weren't updated"
