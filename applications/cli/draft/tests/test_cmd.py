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

import os

import pytest
from unittest.mock import call, ANY

from draft import cmd
from cli_text_consts import DraftCmdTexts as Texts


FAKE_CLI_CONFIG_DIR_PATH = '/home/fakeuser/dist'
FAKE_DRAFT_BIN_PATH = os.path.join(FAKE_CLI_CONFIG_DIR_PATH, cmd.DRAFT_BIN)

CORRECT_UP_OUTPUT_BUILD_IMAGE = 'Building Docker Image: SUCCESS'
CORRECT_UP_OUTPUT_PUSH_IMAGE = 'Pushing Docker Image: SUCCESS'
CORRECT_UP_OUTPUT_DEPLOY = 'Releasing Application: SUCCESS'

INCORRECT_UP_OUTPUT = 'Building Docker Image: SUCCESS Releasing Application: SUCCESS'

CORRECT_CREATE_OUTPUT = '--> Ready to sail'

INCORRECT_CREATE_OUTPUT = '-->  to sail 1234567890 AbCdEF'


@pytest.fixture
def draft_mock(mocker):
    config_class_mock = mocker.patch('draft.cmd.Config')
    config_instance_mock = config_class_mock.return_value
    config_instance_mock.config_path = FAKE_CLI_CONFIG_DIR_PATH

    exe_mock = mocker.patch.object(cmd, 'execute_system_command')
    exe_mock.return_value = ('some return', 0, 'some_return')

    return cmd


# noinspection PyShadowingNames
def test_create(draft_mock):
    draft_mock.create()

    assert draft_mock.execute_system_command.call_count == 1
    draft_mock.execute_system_command.assert_has_calls([call([FAKE_DRAFT_BIN_PATH, 'create'],
                                                             env=ANY,
                                                             cwd=None,
                                                             logs_size=0)])


# noinspection PyShadowingNames
def test_up(draft_mock, mocker):
    mocker.patch('subprocess.Popen')

    draft_mock.up()

    assert draft_mock.execute_system_command.call_count == 1
    draft_mock.execute_system_command.assert_has_calls([call([FAKE_DRAFT_BIN_PATH, 'up'],
                                                             env=ANY,
                                                             cwd=None,
                                                             logs_size=0)])


def test_check_up_status_success():
    output, exit_code = cmd.check_up_status('{} {} {}'.format(CORRECT_UP_OUTPUT_BUILD_IMAGE,
                                                              CORRECT_UP_OUTPUT_PUSH_IMAGE,
                                                              CORRECT_UP_OUTPUT_DEPLOY))

    assert not exit_code
    assert not output


def test_check_up_status_lack_of_push():
    output, exit_code = cmd.check_up_status('{} {}'.format(CORRECT_UP_OUTPUT_BUILD_IMAGE,
                                                           CORRECT_UP_OUTPUT_DEPLOY))

    assert exit_code == 101
    assert output == Texts.DOCKER_IMAGE_NOT_SENT


def test_check_up_status_lack_of_build():
    output, exit_code = cmd.check_up_status('{}'.format(CORRECT_UP_OUTPUT_DEPLOY))

    assert exit_code == 100
    assert output == Texts.DOCKER_IMAGE_NOT_BUILT


def test_check_up_status_lack_of_deploy():
    output, exit_code = cmd.check_up_status('{} {}'.format(CORRECT_UP_OUTPUT_BUILD_IMAGE,
                                                           CORRECT_UP_OUTPUT_PUSH_IMAGE))

    assert exit_code == 102
    assert output == Texts.APP_NOT_RELEASED


def test_check_create_status_success():
    output, exit_code = cmd.check_create_status(CORRECT_CREATE_OUTPUT)

    assert not exit_code
    assert not output


def test_check_create_status_fail():
    output, exit_code = cmd.check_create_status(INCORRECT_UP_OUTPUT)

    assert exit_code == 100
    assert output == Texts.DEPLOYMENT_NOT_CREATED
