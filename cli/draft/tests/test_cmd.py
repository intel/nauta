#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

from unittest.mock import call, ANY

from util.config import Config
from unittest.mock import call
import os
import pytest

from draft import cmd


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
    path_mock = mocker.patch.object(Config, 'get')
    path_mock.return_value = FAKE_CLI_CONFIG_DIR_PATH

    exe_mock = mocker.patch.object(cmd, 'execute_system_command')
    exe_mock.return_value = ('some return', 0)

    return cmd


# noinspection PyShadowingNames
def test_create(draft_mock):
    draft_mock.create()

    assert draft_mock.execute_system_command.call_count == 1
    draft_mock.execute_system_command.assert_has_calls([call([FAKE_DRAFT_BIN_PATH, 'create'], env=ANY, cwd=None)])


# noinspection PyShadowingNames
def test_up(draft_mock, mocker):
    mocker.patch('subprocess.Popen')

    draft_mock.up()

    assert draft_mock.execute_system_command.call_count == 1
    draft_mock.execute_system_command.assert_has_calls([call([FAKE_DRAFT_BIN_PATH, 'up'], env=ANY, cwd=None)])


def test_set_registry_port(draft_mock):
    draft_mock.set_registry_port("5000")

    assert draft_mock.execute_system_command.call_count == 1
    assert draft_mock.execute_system_command.call_args == call([FAKE_DRAFT_BIN_PATH, 'config', 'set', 'registry',
                                                                '127.0.0.1:5000'], env=ANY, cwd=None)


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
    assert output == 'Docker image hasn\'t been sent to the cluster.'


def test_check_up_status_lack_of_build():
    output, exit_code = cmd.check_up_status('{}'.format(CORRECT_UP_OUTPUT_DEPLOY))

    assert exit_code == 100
    assert output == 'Docker image hasn\'t been built.'


def test_check_up_status_lack_of_deploy():
    output, exit_code = cmd.check_up_status('{} {}'.format(CORRECT_UP_OUTPUT_BUILD_IMAGE,
                                                           CORRECT_UP_OUTPUT_PUSH_IMAGE))

    assert exit_code == 102
    assert output == 'Application hasn\'t been released.'


def test_check_create_status_success():
    output, exit_code = cmd.check_create_status(CORRECT_CREATE_OUTPUT)

    assert not exit_code
    assert not output


def test_check_create_status_fail():
    output, exit_code = cmd.check_create_status(INCORRECT_UP_OUTPUT)

    assert exit_code == 100
    assert output == 'Deployment hasn\'t been created.'
