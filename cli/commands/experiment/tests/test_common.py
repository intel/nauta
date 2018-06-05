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


import os

import pytest

from commands.experiment import common
from util.exceptions import KubectlIntError
import util.config


EXPERIMENT_FOLDER = "\\HOME\\FOLDER\\"
EXPERIMENT_NAME = "experiment_name"
SCRIPT_LOCATION = "training_script.py"

FAKE_CLI_CONFIG_DIR_PATH = '/home/fakeuser/dist'
FAKE_CLI_EXPERIMENT_PATH = os.path.join(FAKE_CLI_CONFIG_DIR_PATH, util.config.EXPERIMENTS_DIR_NAME, EXPERIMENT_NAME)


@pytest.fixture()
def config_mock(mocker):
    config_class_mock = mocker.patch('commands.experiment.common.Config')
    config_instance_mock = config_class_mock.return_value
    config_instance_mock.config_path = FAKE_CLI_CONFIG_DIR_PATH
    return config_instance_mock


def test_delete_environment(config_mock, mocker):
    sh_rmtree_mock = mocker.patch("shutil.rmtree")

    common.delete_environment(EXPERIMENT_FOLDER)

    assert sh_rmtree_mock.call_count == 1, "folder wasn't deleted."


def test_create_environment_success(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs")
    sh_copy_mock = mocker.patch("shutil.copy2")
    sh_copytree_mock = mocker.patch("shutil.copytree")

    experiment_path = common.create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert sh_copytree_mock.call_count == 1, "additional folder wan't copied"
    assert sh_copy_mock.call_count == 1, "files weren't copied"
    assert experiment_path == FAKE_CLI_EXPERIMENT_PATH


def test_create_environment_makedir_error(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs", side_effect=Exception("Test exception"))
    sh_copy_mock = mocker.patch("shutil.copy2")
    sh_copytree_mock = mocker.patch("shutil.copytree")

    with pytest.raises(KubectlIntError):
        common.create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert sh_copytree_mock.call_count == 1, "additional folder wan't copied"
    assert sh_copy_mock.call_count == 0, "files were copied"


def test_create_environment_lack_of_home_folder(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    os_mkdirs_mock = mocker.patch("os.makedirs")
    sh_copy_mock = mocker.patch("shutil.copy2")

    with pytest.raises(KubectlIntError):
        common.create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert os_pexists_mock.call_count == 0, "existence of an experiment's folder was checked"
    assert os_mkdirs_mock.call_count == 0, "experiment's folder was created"
    assert sh_copy_mock.call_count == 0, "files were copied"


def test_create_environment_copy_error(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs")
    sh_copy_mock = mocker.patch("shutil.copy2", side_effect=Exception("Test exception"))
    sh_copytree_mock = mocker.patch("shutil.copytree")

    with pytest.raises(KubectlIntError):
        common.create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert sh_copytree_mock.call_count == 1, "additional folder wan't copied"
    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert sh_copy_mock.call_count == 1, "files were copied"
