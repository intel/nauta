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


from unittest.mock import Mock
from util.system import get_current_os, OS
from click.testing import CliRunner
import pytest

from commands.common import ExperimentDescription
from commands import submit
from util.exceptions import KubectlIntError
from commands.tests.test_common import config_path_mock  # noqa: F401

EXPERIMENT_FOLDER = "\\HOME\\FOLDER\\"
EXPERIMENT_NAME = "experiment_name"
SCRIPT_LOCATION = "training_script.py"

PARAMETERS = "--param1=value1 -param2=value2 param3=value3"
TEMPLATE_PARAM = "--template"
TEMPLATE_NAME = "non-existing-template"
FAKE_NODE_PORT = 345678
FAKE_CONTAINER_PORT = 5000

EXPERIMENT_NAME = "experiment_name"
PR_PARAMETER = ["-pr", "param1", "{1...2:1}"]
PS_PARAMETER = ["-ps", "{param2:3}"]


def test_submit_success(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    add_experiment_mock = mocker.patch("platform_resources.experiments.add_experiment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.submit.socat")

    runner = CliRunner()
    runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert gen_expname_mock.call_count == 1, "experiment name wasn't created"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "configuration wasn't updated"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert add_experiment_mock.call_count == 1, "experiment model was not created"
    assert cmd_up_mock.call_count == 1, "training wasn't deployed"
    assert del_env_mock.call_count == 0, "environment folder was deleted"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 1, "socat wasn't started"


def test_submit_fail(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[KubectlIntError()])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])
    del_env_mock = mocker.patch("commands.common.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    runner = CliRunner()
    runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment was created"
    assert cmd_create_mock.call_count == 0, "deployment was created"
    assert upd_conf_mock.call_count == 0, "configuration was updated"
    assert cmd_up_mock.call_count == 0, "training was deployed"
    assert del_env_mock.call_count == 0, "environment folder was deleted"


def test_submit_depl_fail(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("error message", 1)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])
    del_env_mock = mocker.patch("commands.submit.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    runner = CliRunner()
    runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "app didn't try to deploy training"
    assert upd_conf_mock.call_count == 0, "configuration was updated"
    assert cmd_up_mock.call_count == 0, "training was deployed"


def test_submit_env_update_fail(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[KubectlIntError])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])
    del_env_mock = mocker.patch("commands.submit.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    runner = CliRunner()
    runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 0, "port was forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "app didn't try to update its configuration"
    assert cmd_up_mock.call_count == 0, "training was deployed"


def test_submit_start_depl_fail(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("error message", 1)])
    del_env_mock = mocker.patch("commands.submit.delete_environment")
    add_experiment_mock = mocker.patch("platform_resources.experiments.add_experiment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.submit.socat")

    runner = CliRunner()
    runner.invoke(submit.submit, [SCRIPT_LOCATION])

    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_create_mock.call_count == 1, "deployment wasn't created"
    assert upd_conf_mock.call_count == 1, "configuration was updated"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert cmd_up_mock.call_count == 1, "app didn't try to start deployment"
    assert add_experiment_mock.call_count == 1, "experiment model was not created"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert socat_mock.start.call_count == 1, "socat wasn't started"
        socat_mock.start.assert_called_with(FAKE_NODE_PORT)


def test_submit_lack_of_template(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment", side_effect=[(EXPERIMENT_FOLDER, "")])
    cmd_call_draft_mock = mocker.patch("draft.cmd.call_draft",
                                       side_effect=[("Error: could not load pack: rest of a message", 1)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration", side_effect=[0])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])
    del_env_mock = mocker.patch("commands.submit.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding")

    runner = CliRunner()
    result = runner.invoke(submit.submit, [SCRIPT_LOCATION, TEMPLATE_PARAM, TEMPLATE_NAME])

    assert "Problems during creation of experiments' environments." \
           in result.output, "incorrect message from execution of dlsctl"

    assert spf_mock.call_count == 0, "port was forwarded"
    assert del_env_mock.call_count == 1, "environment folder wasn't deleted"
    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 1, "environment wasn't created"
    assert cmd_call_draft_mock.call_count == 1, "app didn't try to deploy training"
    assert upd_conf_mock.call_count == 0, "configuration was updated"
    assert cmd_up_mock.call_count == 0, "training was deployed"


def test_delete_experiments(mocker):
    del_env_mock = mocker.patch("commands.submit.delete_environment")

    experiments_list = [ExperimentDescription(folder="folder1"),
                        ExperimentDescription(),
                        ExperimentDescription(folder="folder3")]

    submit.delete_experiments(experiments_list)

    assert del_env_mock.call_count == 2, "delete environment was called incorrect number of times"


def test_values_range_int():
    list_to_check_1 = ["1", "3", "5", "7", "9"]
    list_to_check_2 = ["2", "4", "6", "8", "10"]

    ret_list = submit.values_range("1", "10", "2")

    assert list_to_check_1 == ret_list

    ret_list = submit.values_range("2", "10", "2")

    assert list_to_check_2 == ret_list


def test_values_range_float():
    list_to_check_1 = ["0.1", "0.2", "0.3", "0.4", "0.5"]
    list_to_check_2 = ["1.0", "2.0", "3.0", "4.0", "5.0"]
    list_to_check_3 = ["0.125", "0.25", "0.375", "0.5", "0.625"]
    ret_list = submit.values_range("0.1", "0.5", "0.1")

    assert list_to_check_1 == ret_list

    ret_list = submit.values_range("1.0", "5.0", "1.0")

    assert list_to_check_2 == ret_list

    ret_list = submit.values_range("0.125", "0.725", "0.125")

    assert list_to_check_3 == ret_list


def test_prepare_list_of_values():
    list_of_params = ['param1=1', 'param1=2', 'param1=3']

    ret_list = submit.prepare_list_of_values("param1", "{1 ,2, 3}")

    assert ret_list == list_of_params

    range_of_params = ["param2=0.1", "param2=0.2", "param2=0.3", "param2=0.4", "param2=0.5", ]

    ret_list = submit.prepare_list_of_values("param2", "{0.1...0.5:0.1}")

    assert ret_list == range_of_params


def test_analyze_pr_parameters_list_success():

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    two_params_list_result = [("param1=0", "param2=0"), ("param1=0", "param2=1"), ("param1=0", "param2=2"),
                              ("param1=1", "param2=0"), ("param1=1", "param2=1"), ("param1=1", "param2=2")]
    ret_list = submit.analyze_pr_parameters_list(two_params_list)

    assert ret_list == two_params_list_result


def test_analyze_pr_parameters_list_ambiguosly_defined():

    identical_param_list = [("param1", "{0, 1}"), ("param1", "{0...2:1}")]

    with pytest.raises(KubectlIntError) as exe:
        submit.analyze_pr_parameters_list(identical_param_list)

    assert str(exe.value) == "Parameter param1 ambiguously defined."


def test_analyze_pr_parameters_list_missing_brackets():

    two_params_list = [("param1", "1, 2, 3"), ("param2", "{0...2:1}")]

    with pytest.raises(KubectlIntError) as exe:
        submit.analyze_pr_parameters_list(two_params_list)

    assert str(exe.value) == "Parameter param1 has incorrect format."


def test_analyze_pr_parameters_list_wrong_format():

    two_params_list = [("param1", "1, 2, 3"), ("param2", "{a...b:1}")]

    with pytest.raises(KubectlIntError) as exe:
        submit.analyze_pr_parameters_list(two_params_list)

    assert str(exe.value) == "Parameter param1 has incorrect format."


def test_analyze_ps_parameters_list_success():
    three_params = ("{param1:value1, param2:value2, param3:value3}", )
    three_params_output = [("param1=value1", "param2=value2", "param3=value3")]

    output = submit.analyze_ps_parameters_list(three_params)

    assert output == three_params_output

    one_param = ("{param1: value2}", )
    one_param_output = [("param1= value2", )]

    output = submit.analyze_ps_parameters_list(one_param)

    assert output == one_param_output

    multiple_two_params = ("{param1: value2, param2:value3}", "{param1:value4,param3:value5}")
    multiple_two_params_output = [("param1= value2", "param2=value3"),
                                  ("param1=value4", "param3=value5")]

    output = submit.analyze_ps_parameters_list(multiple_two_params)

    assert output == multiple_two_params_output


def test_analyze_ps_parameters_wrong_format():
    three_params = ("{param1:value1, param2:value2, param3:value3", )

    with pytest.raises(KubectlIntError) as exe:
        submit.analyze_ps_parameters_list(three_params)

    assert str(exe.value) == "One of -ps options has incorrect format."


def test_check_enclosing_brackets():
    success = "{correct value}"

    assert submit.check_enclosing_brackets(success)

    wrong_format = "wrong format}"

    assert not submit.check_enclosing_brackets(wrong_format)

    missing_value = ""

    assert not submit.check_enclosing_brackets(missing_value)


def test_create_list_of_experiments_pr_only(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    two_params_list_result = \
        [ExperimentDescription(name=experiment_name + "-1", parameters=("param1=0", "param2=0")),
         ExperimentDescription(name=experiment_name + "-2", parameters=("param1=0", "param2=1")),
         ExperimentDescription(name=experiment_name + "-3", parameters=("param1=0", "param2=2")),
         ExperimentDescription(name=experiment_name + "-4", parameters=("param1=1", "param2=0")),
         ExperimentDescription(name=experiment_name + "-5", parameters=("param1=1", "param2=1")),
         ExperimentDescription(name=experiment_name + "-6", parameters=("param1=1", "param2=2"))]

    output = submit.prepare_list_of_experiments(two_params_list, experiment_name, ())

    assert len(output) == 6
    assert output == two_params_list_result


def test_create_list_of_experiments_ps_only(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    multiple_two_params = ("{param1:0, param2:1}", "{param1:2,param3:3}")
    multiple_two_params_list_result = \
        [ExperimentDescription(name=experiment_name + "-1", parameters=("param1=0", "param2=1")),
         ExperimentDescription(name=experiment_name + "-2", parameters=("param1=2", "param3=3"))]
    output = submit.prepare_list_of_experiments((), experiment_name, multiple_two_params)

    assert len(output) == 2
    assert output == multiple_two_params_list_result


def test_create_list_of_experiments_pr_and_ps(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    multiple_two_params = ("{param3:0, param4:1}", "{param3:2,param4:3}")

    expected_result = [ExperimentDescription(name=experiment_name + "-1",
                                             parameters=("param3=0", "param4=1", "param1=0", "param2=0")),
                       ExperimentDescription(name=experiment_name + "-2",
                                             parameters=("param3=0", "param4=1", "param1=0", "param2=1")),
                       ExperimentDescription(name=experiment_name + "-3",
                                             parameters=("param3=0", "param4=1", "param1=0", "param2=2")),
                       ExperimentDescription(name=experiment_name + "-4",
                                             parameters=("param3=0", "param4=1", "param1=1", "param2=0")),
                       ExperimentDescription(name=experiment_name + "-5",
                                             parameters=("param3=0", "param4=1", "param1=1", "param2=1")),
                       ExperimentDescription(name=experiment_name + "-6",
                                             parameters=("param3=0", "param4=1", "param1=1", "param2=2")),
                       ExperimentDescription(name=experiment_name + "-7",
                                             parameters=("param3=2", "param4=3", "param1=0", "param2=0")),
                       ExperimentDescription(name=experiment_name + "-8",
                                             parameters=("param3=2", "param4=3", "param1=0", "param2=1")),
                       ExperimentDescription(name=experiment_name + "-9",
                                             parameters=("param3=2", "param4=3", "param1=0", "param2=2")),
                       ExperimentDescription(name=experiment_name + "-10",
                                             parameters=("param3=2", "param4=3", "param1=1", "param2=0")),
                       ExperimentDescription(name=experiment_name + "-11",
                                             parameters=("param3=2", "param4=3", "param1=1", "param2=1")),
                       ExperimentDescription(name=experiment_name + "-12",
                                             parameters=("param3=2", "param4=3", "param1=1", "param2=2"))]

    output = submit.prepare_list_of_experiments(two_params_list, experiment_name, multiple_two_params)

    assert len(output) == 12
    assert output == expected_result


def test_submit_two_experiment_success(config_path_mock, mocker):  # noqa: F811
    get_namespace_mock = mocker.patch("commands.submit.get_kubectl_current_context_namespace")
    gen_expname_mock = mocker.patch("platform_resources.experiments.generate_experiment_name",
                                    side_effect=[EXPERIMENT_NAME])
    crenv_mock = mocker.patch("commands.submit.create_environment",
                              side_effect=[(EXPERIMENT_FOLDER), (EXPERIMENT_FOLDER)])
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0), ("", 0)])
    upd_conf_mock = mocker.patch("commands.submit.update_configuration")
    add_experiment_mock = mocker.patch("platform_resources.experiments.add_experiment")
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0), ("", 0)])
    del_env_mock = mocker.patch("commands.submit.delete_environment")
    spf_mock = mocker.patch("commands.submit.start_port_forwarding",
                            side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])

    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        socat_mock = mocker.patch("commands.submit.socat")

    runner = CliRunner()
    parameters = [SCRIPT_LOCATION]
    parameters.extend(PR_PARAMETER)
    parameters.extend(PS_PARAMETER)

    result = runner.invoke(submit.submit, parameters, input="y")

    assert get_namespace_mock.call_count == 1, "current user namespace was not fetched"
    assert add_experiment_mock.call_count == 1, "experiment model was not created"
    assert spf_mock.call_count == 1, "port wasn't forwarded"
    assert gen_expname_mock.call_count == 1, "home folder doesn't exist"
    assert crenv_mock.call_count == 2, "environments weren't created"
    assert cmd_create_mock.call_count == 2, "deployments weren't created"
    assert upd_conf_mock.call_count == 2, "configurations weren't updated"
    assert cmd_up_mock.call_count == 2, "training jobs weren't deployed"
    assert del_env_mock.call_count == 0, "environment folder was deleted"

    assert "param1=1" in result.output
    assert "param1=2" in result.output
    assert "param2=3" in result.output
