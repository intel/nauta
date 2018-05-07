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

from unittest.mock import call

import pytest

from click.testing import CliRunner

from commands import submit
from util.system import get_current_os, OS

EXPERIMENT_FOLDER = "\\HOME\\FOLDER\\"
EXPERIMENT_NAME = "experiment_name"
SCRIPT_LOCATION = "training_script.py"
EXPERIMENT_NAME = "experiment_name"
PARAMETERS = "--param1=value1 -param2=value2 param3=value3"
FAKE_PORT = 'fake_port'


def test_submit_success(mocker):
    gen_expname_mock = mocker.patch("commands.common.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.common.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect = [("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect = [0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect = [("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        get_registry_port_mock = mocker.patch("commands.submit.get_registry_port", side_effect = [FAKE_PORT])
        socat_mock = mocker.patch("commands.submit.socat")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "configuration wasn't updated"
    assert cmd_up_mock.call_count == 1, "training wasn't deployed"
    assert del_env_mock.call_count == 0, "environment folder was deleted"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert get_registry_port_mock.call_count == 1, "port on MacOS/Windows wasn't returned"
        assert socat_mock.start.call_count == 1, "socat wasn't started"
        socat_mock.start.assert_called_with(FAKE_PORT)


def test_submit_fail(mocker):
    gen_expname_mock = mocker.patch("commands.common.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.common.create_environment", side_effect=[("", "error")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect = [("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect = [0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect = [("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment was created"
    assert cmd_create_mock.call_count == 0, "deployment was created"
    assert upd_conf_mock.call_count == 0, "configuration was updated"
    assert cmd_up_mock.call_count == 0, "training was deployed"
    assert del_env_mock.call_count == 0, "environment folder was deleted"


def test_submit_depl_fail(mocker):
    gen_expname_mock = mocker.patch("commands.common.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.common.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect = [("error message", 1)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect = [0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect = [("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "app didn't try to deploy training"
    assert upd_conf_mock.call_count == 0, "configuration was updated"
    assert cmd_up_mock.call_count == 0, "training was deployed"


def test_submit_env_update_fail(mocker):
    gen_expname_mock = mocker.patch("commands.common.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.common.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect = [("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect = [1])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect = [("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "app didn't try to update its configuration"
    assert cmd_up_mock.call_count == 0, "training was deployed"


def test_submit_start_depl_fail(mocker):
    gen_expname_mock = mocker.patch("commands.common.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.common.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect = [("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect = [0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect = [("error message", 1)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        get_registry_port_mock = mocker.patch("commands.submit.get_registry_port", side_effect = [FAKE_PORT])
        socat_mock = mocker.patch("commands.submit.socat")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "configuration was updated"
    assert cmd_up_mock.call_count == 1, "app didn't try to start deployment"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert get_registry_port_mock.call_count == 1, "port on MacOS/Windows wasn't returned"
        assert socat_mock.start.call_count == 1, "socat wasn't started"
        socat_mock.start.assert_called_with(FAKE_PORT)