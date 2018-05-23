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

from commands.experiment.common import RunDescription
from commands.experiment import submit
from util.exceptions import KubectlIntError

EXPERIMENT_FOLDER = "\\HOME\\FOLDER\\"
EXPERIMENT_NAME = "experiment-name"
EXPERIMENT_NAMESPACE = "user-namespace"
SCRIPT_LOCATION = "training_script.py"

PARAMETERS = "--param1=value1 -param2=value2 param3=value3"
PR_PARAMETER = ["-pr", "param1", "{1...2:1}"]
PS_PARAMETER = ["-ps", "{param2:3}"]

TEMPLATE_PARAM = "--template"
TEMPLATE_NAME = "non-existing-template"
FAKE_NODE_PORT = 345678
FAKE_CONTAINER_PORT = 5000


class SubmitMocks:
    def __init__(self, mocker, get_namespace=None, gen_exp_name=None, add_exp=None, cmd_create=None, cmd_up=None,
                 update_conf=None, create_env=None, del_env=None, start_port_fwd=None, socat=None, isfile=None,
                 isdir=None) -> None:
        self.mocker = mocker
        self.get_namespace = get_namespace
        self.gen_exp_name = gen_exp_name
        self.add_exp = add_exp
        self.cmd_create = cmd_create
        self.cmd_up = cmd_up
        self.update_conf = update_conf
        self.create_env = create_env
        self.del_env = del_env
        self.start_port_fwd = start_port_fwd
        self.socat = socat
        self.isfile = isfile
        self.isdir = isdir


@pytest.fixture
def prepare_mocks(mocker) -> SubmitMocks:
    get_namespace_mock = mocker.patch("commands.experiment.submit.get_kubectl_current_context_namespace",
                                      side_effect=[EXPERIMENT_NAMESPACE])
    gen_exp_name_mock = mocker.patch("platform_resources.experiments.generate_experiment_name",
                                     side_effect=[EXPERIMENT_NAME])
    add_exp_mock = mocker.patch("platform_resources.experiments.add_experiment")
    cmd_create_mock = mocker.patch("draft.cmd.create", side_effect=[("", 0)])
    cmd_up_mock = mocker.patch("draft.cmd.up", side_effect=[("", 0)])

    update_conf_mock = mocker.patch("commands.experiment.submit.update_configuration", side_effect=[0])
    create_env_mock = mocker.patch("commands.experiment.submit.create_environment",
                                   side_effect=[(EXPERIMENT_FOLDER, "")])
    del_env_mock = mocker.patch("commands.experiment.submit.delete_environment")
    start_port_fwd_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.start_port_forwarding",
                                       side_effect=[(Mock, FAKE_NODE_PORT, FAKE_CONTAINER_PORT)])
    socat_mock = mocker.patch("commands.experiment.submit.socat") \
        if get_current_os() in (OS.WINDOWS, OS.MACOS) else None
    isfile_mock = mocker.patch("os.path.isfile", return_value=True)
    isdir_mock = mocker.patch("os.path.isdir", return_value=True)

    return SubmitMocks(mocker=mocker, get_namespace=get_namespace_mock, gen_exp_name=gen_exp_name_mock,
                       add_exp=add_exp_mock, cmd_create=cmd_create_mock, cmd_up=cmd_up_mock,
                       update_conf=update_conf_mock, create_env=create_env_mock, del_env=del_env_mock,
                       start_port_fwd=start_port_fwd_mock, socat=socat_mock, isfile=isfile_mock, isdir=isdir_mock)


def check_asserts(prepare_mocks: SubmitMocks, get_namespace_count=1, get_exp_name_count=1, create_env_count=1,
                  cmd_create_count=1, update_conf_count=1, start_port_fwd_count=1, add_exp_count=1, cmd_up_count=1,
                  del_env_count=0, isfile_count=1, socat_start_count=1):
    assert prepare_mocks.isfile.call_count == isfile_count, "Script location was not checked"
    assert prepare_mocks.get_namespace.call_count == get_namespace_count, "current user namespace was not fetched"
    assert prepare_mocks.gen_exp_name.call_count == get_exp_name_count, "experiment name wasn't created"
    assert prepare_mocks.create_env.call_count == create_env_count, "environment wasn't created"
    assert prepare_mocks.cmd_create.call_count == cmd_create_count, "deployment wasn't created"
    assert prepare_mocks.update_conf.call_count == update_conf_count, "configuration wasn't updated"
    assert prepare_mocks.start_port_fwd.call_count == start_port_fwd_count, "port wasn't forwarded"
    assert prepare_mocks.add_exp.call_count == add_exp_count, "experiment model was not created"
    assert prepare_mocks.cmd_up.call_count == cmd_up_count, "training wasn't deployed"
    assert prepare_mocks.del_env.call_count == del_env_count, "environment folder was deleted"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert prepare_mocks.socat.start.call_count == socat_start_count, "socat wasn't started"
        if socat_start_count > 0:
            prepare_mocks.socat.start.assert_called_with(FAKE_NODE_PORT)


def test_submit_success(prepare_mocks: SubmitMocks):
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION])
    check_asserts(prepare_mocks)


def test_submit_fail(prepare_mocks: SubmitMocks):
    prepare_mocks.create_env = prepare_mocks.mocker.patch("commands.experiment.submit.create_environment",
                                                          side_effect=[KubectlIntError()])
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION])
    check_asserts(prepare_mocks, cmd_create_count=0, update_conf_count=0, start_port_fwd_count=1, add_exp_count=0,
                  cmd_up_count=0, socat_start_count=0)


def test_submit_depl_fail(prepare_mocks: SubmitMocks):
    prepare_mocks.cmd_create = prepare_mocks.mocker.patch("draft.cmd.create", side_effect=[("error message", 1)])
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION])
    check_asserts(prepare_mocks, update_conf_count=0, start_port_fwd_count=1, add_exp_count=0, cmd_up_count=0,
                  del_env_count=1, socat_start_count=0)


def test_submit_env_update_fail(prepare_mocks: SubmitMocks):
    prepare_mocks.update_conf = prepare_mocks.mocker.patch("commands.experiment.submit.update_configuration",
                                                           side_effect=[KubectlIntError])
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION])
    check_asserts(prepare_mocks, start_port_fwd_count=1, add_exp_count=0, cmd_up_count=0, del_env_count=1,
                  socat_start_count=0)


def test_submit_start_depl_fail(prepare_mocks: SubmitMocks):
    prepare_mocks.cmd_up = prepare_mocks.mocker.patch("draft.cmd.up", side_effect=[("error message", 1)])
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION])
    check_asserts(prepare_mocks, del_env_count=1)


def test_submit_two_experiment_success(prepare_mocks: SubmitMocks):
    prepare_mocks.create_env = prepare_mocks.mocker.patch("commands.experiment.submit.create_environment",
                                                          side_effect=[(EXPERIMENT_FOLDER), (EXPERIMENT_FOLDER)])
    prepare_mocks.cmd_create = prepare_mocks.mocker.patch("draft.cmd.create", side_effect=[("", 0), ("", 0)])
    prepare_mocks.update_conf = prepare_mocks.mocker.patch("commands.experiment.submit.update_configuration",
                                                           side_effect=[0, 0])
    prepare_mocks.cmd_up = prepare_mocks.mocker.patch("draft.cmd.up", side_effect=[("", 0), ("", 0)])

    parameters = [SCRIPT_LOCATION]
    parameters.extend(PR_PARAMETER)
    parameters.extend(PS_PARAMETER)

    result = CliRunner().invoke(submit.submit, parameters, input="y")
    check_asserts(prepare_mocks, create_env_count=2, cmd_create_count=2, update_conf_count=2, cmd_up_count=2)
    assert "param1=1" in result.output
    assert "param1=2" in result.output
    assert "param2=3" in result.output


def test_submit_with_name_success(prepare_mocks: SubmitMocks):
    CliRunner().invoke(submit.submit, [SCRIPT_LOCATION, '-n', EXPERIMENT_NAME])
    check_asserts(prepare_mocks)


def test_submit_with_incorrect_name_fail(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit.submit, [SCRIPT_LOCATION, '-n', 'Wrong_&name'])
    assert 'name must consist of lower case alphanumeric characters' in result.output


def test_delete_runs(mocker):
    del_env_mock = mocker.patch("commands.experiment.submit.delete_environment")

    runs_list = [RunDescription(folder="folder1"), RunDescription(), RunDescription(folder="folder3")]
    submit.delete_runs(runs_list)

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
    three_params = ("{param1:value1, param2:value2, param3:value3}",)
    three_params_output = [("param1=value1", "param2=value2", "param3=value3")]
    output = submit.analyze_ps_parameters_list(three_params)
    assert output == three_params_output

    one_param = ("{param1: value2}",)
    one_param_output = [("param1= value2",)]
    output = submit.analyze_ps_parameters_list(one_param)
    assert output == one_param_output

    multiple_two_params = ("{param1: value2, param2:value3}", "{param1:value4,param3:value5}")
    multiple_two_params_output = [("param1= value2", "param2=value3"),
                                  ("param1=value4", "param3=value5")]
    output = submit.analyze_ps_parameters_list(multiple_two_params)
    assert output == multiple_two_params_output


def test_analyze_ps_parameters_wrong_format():
    three_params = ("{param1:value1, param2:value2, param3:value3",)
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


def test_create_list_of_runs_pr_only(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    two_params_list_result = \
        [RunDescription(name=experiment_name + "-1", parameters=("param1=0", "param2=0")),
         RunDescription(name=experiment_name + "-2", parameters=("param1=0", "param2=1")),
         RunDescription(name=experiment_name + "-3", parameters=("param1=0", "param2=2")),
         RunDescription(name=experiment_name + "-4", parameters=("param1=1", "param2=0")),
         RunDescription(name=experiment_name + "-5", parameters=("param1=1", "param2=1")),
         RunDescription(name=experiment_name + "-6", parameters=("param1=1", "param2=2"))]

    output = submit.prepare_list_of_runs(two_params_list, experiment_name, ())
    assert len(output) == 6
    assert output == two_params_list_result


def test_create_list_of_runs_ps_only(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    multiple_two_params = ("{param1:0, param2:1}", "{param1:2,param3:3}")
    multiple_two_params_list_result = \
        [RunDescription(name=experiment_name + "-1", parameters=("param1=0", "param2=1")),
         RunDescription(name=experiment_name + "-2", parameters=("param1=2", "param3=3"))]
    output = submit.prepare_list_of_runs((), experiment_name, multiple_two_params)
    assert len(output) == 2
    assert output == multiple_two_params_list_result


def test_create_list_of_runs_pr_and_ps(mocker):
    experiment_name = "experiment_name"
    mocker.patch("platform_resources.experiments.generate_experiment_name", side_effect=[experiment_name])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    multiple_two_params = ("{param3:0, param4:1}", "{param3:2,param4:3}")

    expected_result = [RunDescription(name=experiment_name + "-1",
                                      parameters=("param3=0", "param4=1", "param1=0", "param2=0")),
                       RunDescription(name=experiment_name + "-2",
                                      parameters=("param3=0", "param4=1", "param1=0", "param2=1")),
                       RunDescription(name=experiment_name + "-3",
                                      parameters=("param3=0", "param4=1", "param1=0", "param2=2")),
                       RunDescription(name=experiment_name + "-4",
                                      parameters=("param3=0", "param4=1", "param1=1", "param2=0")),
                       RunDescription(name=experiment_name + "-5",
                                      parameters=("param3=0", "param4=1", "param1=1", "param2=1")),
                       RunDescription(name=experiment_name + "-6",
                                      parameters=("param3=0", "param4=1", "param1=1", "param2=2")),
                       RunDescription(name=experiment_name + "-7",
                                      parameters=("param3=2", "param4=3", "param1=0", "param2=0")),
                       RunDescription(name=experiment_name + "-8",
                                      parameters=("param3=2", "param4=3", "param1=0", "param2=1")),
                       RunDescription(name=experiment_name + "-9",
                                      parameters=("param3=2", "param4=3", "param1=0", "param2=2")),
                       RunDescription(name=experiment_name + "-10",
                                      parameters=("param3=2", "param4=3", "param1=1", "param2=0")),
                       RunDescription(name=experiment_name + "-11",
                                      parameters=("param3=2", "param4=3", "param1=1", "param2=1")),
                       RunDescription(name=experiment_name + "-12",
                                      parameters=("param3=2", "param4=3", "param1=1", "param2=2"))]

    output = submit.prepare_list_of_runs(two_params_list, experiment_name, multiple_two_params)
    assert len(output) == 12
    assert output == expected_result


def test_submit_invalid_script_path(prepare_mocks: SubmitMocks):
    prepare_mocks.isfile.return_value = False

    script_location = 'invalid-script.py'

    runner = CliRunner()
    parameters = [script_location]

    result = runner.invoke(submit.submit, parameters, input="y")
    assert f"Cannot find script: {script_location}. Make sure that provided path is correct." in result.output
    assert result.exit_code == 1


def test_submit_invalid_script_folder_path(prepare_mocks: SubmitMocks):
    prepare_mocks.isdir.return_value = False

    script_folder_location = 'invalid-script.py'

    runner = CliRunner()
    parameters = [SCRIPT_LOCATION, "-sfl", script_folder_location]

    result = runner.invoke(submit.submit, parameters, input="y")
    assert f"Cannot find script folder: {script_folder_location}." \
           f" Make sure that provided path is correct." in result.output
    assert result.exit_code == 1
