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
from click.testing import CliRunner

from commands.template.copy import copy, Template


class TemplateCopyMocks:
    def __init__(self, mocker):
        self.create_from_existing_template = mocker.patch(
            'commands.template.copy.Template.render_from_existing_template')
        self.get_local_model_list = mocker.patch('commands.template.copy.get_local_templates', return_value={})


@pytest.fixture()
def copy_mocks(mocker) -> TemplateCopyMocks:
    return TemplateCopyMocks(mocker)


def test_copy_src_template_does_not_exist(copy_mocks: TemplateCopyMocks):
    src_template_name = 'src-template'
    dest_template_name = 'dest-template'
    copy_mocks.get_local_model_list.return_value = {}
    result = CliRunner().invoke(copy, [src_template_name, dest_template_name], catch_exceptions=False)

    assert result.exit_code == 1
    assert f'Source template {src_template_name} has not been found.' in result.output


def test_copy_dest_template_exists(copy_mocks: TemplateCopyMocks):
    src_template_name = 'src-template'
    dest_template_name = 'dest-template'
    copy_mocks.get_local_model_list.return_value = {src_template_name: Template(name=src_template_name, description=''),
                                                    dest_template_name:
                                                    Template(name=dest_template_name, description='')}
    result = CliRunner().invoke(copy, [src_template_name, dest_template_name], catch_exceptions=False)

    assert result.exit_code == 1
    assert f'Template with name {dest_template_name} already exists.' in result.output


def test_copy_description_prompt(copy_mocks: TemplateCopyMocks):
    src_template_name = 'src-template'
    dest_template_name = 'dest-template'
    description = 'bla'
    copy_mocks.get_local_model_list.return_value = {src_template_name: Template(name=src_template_name, description='')}
    result = CliRunner().invoke(copy, [src_template_name, dest_template_name, '--description', description],
                                catch_exceptions=False)

    assert result.exit_code == 0
    copy_mocks.create_from_existing_template.assert_called_with(src_template_name=src_template_name)
    assert f'Template {dest_template_name} was successfully created from {src_template_name} template.' in result.output


def test_copy_failure(copy_mocks: TemplateCopyMocks):
    src_template_name = 'src-template'
    dest_template_name = 'dest-template'
    copy_mocks.create_from_existing_template.side_effect = RuntimeError
    copy_mocks.get_local_model_list.return_value = {src_template_name: Template(name=src_template_name, description='')}
    result = CliRunner().invoke(copy, [src_template_name, dest_template_name], input='bla', catch_exceptions=False)

    assert result.exit_code == 1
    assert f'Failed to create {dest_template_name} template from {src_template_name} template.' in result.output


def test_copy_success(copy_mocks: TemplateCopyMocks):
    src_template_name = 'src-template'
    dest_template_name = 'dest-template'
    copy_mocks.get_local_model_list.return_value = {src_template_name: Template(name=src_template_name, description='')}
    result = CliRunner().invoke(copy, [src_template_name, dest_template_name], input='bla', catch_exceptions=False)

    assert result.exit_code == 0
    assert f'Template {dest_template_name} was successfully created from {src_template_name} template.' in result.output
