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

from commands.experiment.common import submit_experiment, RunSubmission, values_range, \
    analyze_ps_parameters_list, analyze_pr_parameters_list, prepare_list_of_values, prepare_list_of_runs, \
    check_enclosing_brackets, delete_environment, create_environment, get_run_environment_path, check_run_environment, \
    RunKinds, validate_pack_params_names, get_log_filename

from util.exceptions import SubmitExperimentError
import util.config
from util.system import get_current_os, OS
from platform_resources.run_model import RunStatus
from cli_text_consts import ExperimentCommonTexts as Texts


EXPERIMENT_FOLDER = "\\HOME\\FOLDER\\"
EXPERIMENT_NAME = "experiment_name"
SCRIPT_LOCATION = "training_script.py"

EXPERIMENT_NAMESPACE = "user-namespace"

PARAMETERS = "--param1=value1 -param2=value2 param3=value3"
PR_PARAMETER = [("param1", "{1...2:1}")]
PS_PARAMETER = ["{param2:3}"]

TEMPLATE_PARAM = "--template"
TEMPLATE_NAME = "non-existing-template"
FAKE_NODE_PORT = 345678
FAKE_CONTAINER_PORT = 5000

FAKE_CLI_CONFIG_DIR_PATH = '/home/fakeuser/dist'
FAKE_CLI_EXPERIMENT_PATH = os.path.join(FAKE_CLI_CONFIG_DIR_PATH, util.config.EXPERIMENTS_DIR_NAME, EXPERIMENT_NAME)

EXAMPLE_PACK_PARAM_KEY = "key"
INVALID_PACK_PARAM_KEY = "key=value"
EXAMPLE_PACK_PARAM_VALUE = "value"

LOG_FILENAME = "01CTJNM0YFPHVWHBSWMB7YE7H1"
LOG_WITH_FILE = "Application nmnist-horo-418-18-10-24-05-13-49: Releasing  Application " \
                "nmnist-horo-418-18-10-24-05-13-49: Releasing   Application nmnist-horo-418-18-10-24-05-13-49 " \
                ": Releasing Application -\\nmnist-horo-418-18-10-24-05-13-49: Releasing Application: " \
                "FAIL \\xe2\\x9d\\x8c  (0.2356s)\\nInspect the logs with `draft logs {}`\\n".format(LOG_FILENAME)

LOG_WITHOUT_FILE = "Application nmnist-horo-418-18-10-24-05-13-49: Releasing  Application " \
                   "nmnist-horo-418-18-10-24-05-13-49: Releasing   Application nmnist-horo-418-18-10-24-05-13-49 " \
                   ": Releasing Application -\\nmnist-horo-418-18-10-24-05-13-49: Releasing Application: "


@pytest.fixture()
def config_mock(mocker):
    config_class_mock = mocker.patch('commands.experiment.common.Config')
    config_instance_mock = config_class_mock.return_value
    config_instance_mock.config_path = FAKE_CLI_CONFIG_DIR_PATH
    return config_instance_mock


def test_delete_environment(config_mock, mocker):
    sh_rmtree_mock = mocker.patch("shutil.rmtree")

    delete_environment(EXPERIMENT_FOLDER)

    assert sh_rmtree_mock.call_count == 1, "folder wasn't deleted."


def test_create_environment_success(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs")
    mocker.patch("os.chmod")
    sem_file_creation_mock = mocker.patch("commands.experiment.common.Path.touch")
    sh_copy_mock = mocker.patch("shutil.copy2")
    sh_copytree_mock = mocker.patch("commands.experiment.common.copy_tree")

    experiment_path = create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert sem_file_creation_mock.call_count == 1, "semaphore file wasn't created"
    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert sh_copytree_mock.call_count == 1, "additional folder wan't copied"
    assert sh_copy_mock.call_count == 1, "files weren't copied"
    assert experiment_path == FAKE_CLI_EXPERIMENT_PATH


def test_create_environment_makedir_error(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs", side_effect=Exception("Test exception"))
    sh_copy_mock = mocker.patch("shutil.copy2")
    copytree_mock = mocker.patch("commands.experiment.common.copy_tree")

    with pytest.raises(SubmitExperimentError):
        create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert copytree_mock.call_count == 0, "additional folder was copied"
    assert sh_copy_mock.call_count == 0, "files were copied"


def test_create_environment_lack_of_home_folder_error(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    os_mkdirs_mock = mocker.patch("os.makedirs", side_effect=RuntimeError())
    sh_copy_mock = mocker.patch("shutil.copy2")

    with pytest.raises(SubmitExperimentError):
        create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert os_mkdirs_mock.call_count == 1, "experiment's folder was created"
    assert sh_copy_mock.call_count == 0, "files were copied"


def test_create_environment_copy_error(config_mock, mocker):
    os_pexists_mock = mocker.patch("os.path.exists", side_effect=[False])
    mocker.patch("os.makedirs")
    sh_copy_mock = mocker.patch("shutil.copy2", side_effect=Exception("Test exception"))
    copytree_mock = mocker.patch("commands.experiment.common.copy_tree")
    mocker.patch("commands.experiment.common.Path.touch")

    with pytest.raises(SubmitExperimentError):
        create_environment(EXPERIMENT_NAME, SCRIPT_LOCATION, EXPERIMENT_FOLDER)

    assert copytree_mock.call_count == 0, "additional folder was copied"
    assert os_pexists_mock.call_count == 1, "existence of an experiment's folder wasn't checked"
    assert sh_copy_mock.call_count == 1, "files were copied"


def test_get_run_environment_path(config_mock):
    assert get_run_environment_path(EXPERIMENT_NAME) == os.path.join(FAKE_CLI_EXPERIMENT_PATH)


class SubmitExperimentMocks:
    def __init__(self, mocker) -> None:
        self.mocker = mocker
        self.get_namespace = mocker.patch("commands.experiment.common.get_kubectl_current_context_namespace",
                                          side_effect=[EXPERIMENT_NAMESPACE])
        self.gen_exp_name = mocker.patch("platform_resources.experiments.generate_exp_name_and_labels",
                                         side_effect=[(EXPERIMENT_NAME, {})])
        self.add_exp = mocker.patch("platform_resources.experiments.add_experiment")
        self.update_experiment = mocker.patch('platform_resources.experiments.update_experiment')
        self.add_run = mocker.patch("platform_resources.runs.add_run")
        self.update_run = mocker.patch("platform_resources.runs.update_run")
        self.cmd_create = mocker.patch("draft.cmd.create", side_effect=[("", 0, "")])
        self.submit_one = mocker.patch("commands.experiment.common.submit_draft_pack")
        self.update_conf = mocker.patch("commands.experiment.common.update_configuration", side_effect=[0])
        self.create_env = mocker.patch("commands.experiment.common.create_environment",
                                       side_effect=[(EXPERIMENT_FOLDER, "")])
        self.check_run_env = mocker.patch("commands.experiment.common.check_run_environment",
                                          side_effect=[(EXPERIMENT_FOLDER, "")])
        self.del_env = mocker.patch("commands.experiment.common.delete_environment")

        self.k8s_proxy = mocker.patch("commands.experiment.common.K8sProxy")
        self.k8s_proxy.return_value.__enter__.return_value.tunnel_port = FAKE_NODE_PORT

        self.k8s_get_node_port = mocker.patch("commands.experiment.common.get_app_service_node_port")
        self.k8s_get_node_port.return_value = FAKE_NODE_PORT

        self.socat = mocker.patch("commands.experiment.common.socat") \
            if get_current_os() in (OS.WINDOWS, OS.MACOS) else None
        self.isdir = mocker.patch("os.path.isdir", return_value=True)
        self.isfile = mocker.patch("os.path.isfile", return_value=True)

        self.config_mock = mocker.patch('commands.experiment.common.Config')
        self.config_mock.return_value.config_path = FAKE_CLI_CONFIG_DIR_PATH
        self.delete_k8s_object_mock = mocker.patch('commands.experiment.common.delete_k8s_object')
        self.get_pod_count_mock = mocker.patch('commands.experiment.common.get_pod_count', return_value=1)
        self.remove_files = mocker.patch('os.remove')


@pytest.fixture
def prepare_mocks(mocker) -> SubmitExperimentMocks:
    return SubmitExperimentMocks(mocker=mocker)


def check_asserts(prepare_mocks: SubmitExperimentMocks, get_namespace_count=1, get_exp_name_count=1, create_env_count=1,
                  cmd_create_count=1, update_conf_count=1, k8s_proxy_count=1, add_exp_count=1, add_run_count=1,
                  update_run_count=0, submit_one_count=1, del_env_count=0, socat_start_count=1,
                  delete_k8s_object_count=0):
    assert prepare_mocks.get_namespace.call_count == get_namespace_count, "current user namespace was not fetched"
    assert prepare_mocks.gen_exp_name.call_count == get_exp_name_count, "experiment name wasn't created"
    assert prepare_mocks.create_env.call_count == create_env_count, "environment wasn't created"
    assert prepare_mocks.cmd_create.call_count == cmd_create_count, "deployment wasn't created"
    assert prepare_mocks.update_conf.call_count == update_conf_count, "configuration wasn't updated"
    assert prepare_mocks.k8s_proxy.call_count == k8s_proxy_count, "port wasn't forwarded"
    assert prepare_mocks.add_exp.call_count == add_exp_count, "experiment model was not created"
    assert prepare_mocks.add_run.call_count == add_run_count, "run model was not created"
    assert prepare_mocks.update_run.call_count == update_run_count, "run model status was not updated"
    assert prepare_mocks.submit_one.call_count == submit_one_count, "training wasn't deployed"
    assert prepare_mocks.del_env.call_count == del_env_count, "environment folder was deleted"
    assert prepare_mocks.delete_k8s_object_mock.call_count == delete_k8s_object_count, "experiment was not deleted"
    if get_current_os() in (OS.WINDOWS, OS.MACOS):
        assert prepare_mocks.socat.start.call_count == socat_start_count, "socat wasn't started"
        if socat_start_count > 0:
            prepare_mocks.socat.start.assert_called_with(FAKE_NODE_PORT)


def test_submit_success(prepare_mocks: SubmitExperimentMocks):
    submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, template=None,
                      name=None, parameter_range=[], parameter_set=[], script_parameters=[], pack_params=[],
                      run_kind=RunKinds.TRAINING)
    check_asserts(prepare_mocks)


def test_submit_fail(prepare_mocks: SubmitExperimentMocks):
    prepare_mocks.create_env.side_effect = SubmitExperimentError

    with pytest.raises(SubmitExperimentError) as exe:
        submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, template='',
                          name='', parameter_range=[], parameter_set=(), script_parameters=(), pack_params=[],
                          run_kind=RunKinds.TRAINING)
        assert Texts.ENV_CREATION_ERROR_MSG in str(exe)

    check_asserts(prepare_mocks, cmd_create_count=0, update_conf_count=0, add_exp_count=0, add_run_count=0,
                  submit_one_count=0, socat_start_count=1, del_env_count=1)


def test_submit_depl_fail(prepare_mocks: SubmitExperimentMocks):
    prepare_mocks.cmd_create.side_effect = [("error message", 1)]
    with pytest.raises(SubmitExperimentError) as exe:
        submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                          template=None, name=None, parameter_range=[], parameter_set=(), script_parameters=(),
                          run_kind=RunKinds.TRAINING)

    assert Texts.ENV_CREATION_ERROR_MSG in str(exe)
    check_asserts(prepare_mocks, update_conf_count=0, add_exp_count=0, submit_one_count=0, socat_start_count=1,
                  del_env_count=1, add_run_count=0)


def test_submit_env_update_fail(prepare_mocks: SubmitExperimentMocks):
    prepare_mocks.update_conf = prepare_mocks.mocker.patch("commands.experiment.common.update_configuration",
                                                           side_effect=[SubmitExperimentError])

    with pytest.raises(SubmitExperimentError) as exe:
        submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                          template=None, name=None, parameter_range=[], parameter_set=(), script_parameters=(),
                          run_kind=RunKinds.TRAINING)

    assert Texts.ENV_CREATION_ERROR_MSG in str(exe)
    check_asserts(prepare_mocks, add_exp_count=0, add_run_count=0,
                  submit_one_count=0, socat_start_count=1, del_env_count=1)


def test_submit_start_depl_fail(prepare_mocks: SubmitExperimentMocks):
    prepare_mocks.submit_one.side_effect = SubmitExperimentError()

    runs_list, _ = submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                                     template=None, name=None, parameter_range=[], parameter_set=(),
                                     script_parameters=(), run_kind=RunKinds.TRAINING)

    assert runs_list[0].state == RunStatus.FAILED
    check_asserts(prepare_mocks, del_env_count=1, update_run_count=1)


def test_submit_start_depl_and_updrun_fail(prepare_mocks: SubmitExperimentMocks):
    prepare_mocks.submit_one.side_effect = SubmitExperimentError()
    prepare_mocks.update_run.side_effect = RuntimeError()

    runs_list, _ = submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                                     template=None, name=None, parameter_range=[], parameter_set=(),
                                     script_parameters=(), run_kind=RunKinds.TRAINING)

    assert runs_list[0].state == RunStatus.FAILED
    check_asserts(prepare_mocks, del_env_count=1, update_run_count=1)


def test_submit_two_experiment_success(prepare_mocks: SubmitExperimentMocks, capsys, caplog):
    import logging
    caplog.set_level(logging.CRITICAL)
    prepare_mocks.mocker.patch("click.confirm", return_value=True)
    prepare_mocks.create_env.side_effect = [(EXPERIMENT_FOLDER), (EXPERIMENT_FOLDER)]
    prepare_mocks.cmd_create.side_effect = [("", 0, ""), ("", 0, "")]
    prepare_mocks.update_conf.side_effect = [0, 0]
    prepare_mocks.check_run_env.side_effect = [None, None]

    parameters = [SCRIPT_LOCATION]
    parameters.extend(PR_PARAMETER)
    parameters.extend(PS_PARAMETER)

    submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                      template=None, name=None, parameter_range=PR_PARAMETER, parameter_set=PS_PARAMETER,
                      script_parameters=[], run_kind=RunKinds.TRAINING)

    check_asserts(prepare_mocks, create_env_count=2, cmd_create_count=2, update_conf_count=2, submit_one_count=2,
                  add_run_count=2)
    out, _ = capsys.readouterr()
    assert "param1=1" in out
    assert "param1=2" in out
    assert "param2=3" in out


def test_submit_with_name_success(prepare_mocks: SubmitExperimentMocks):
    submit_experiment(script_location=SCRIPT_LOCATION, script_folder_location=None, pack_params=[],
                      template=None, name=EXPERIMENT_NAME, parameter_range=[],
                      parameter_set=[], script_parameters=[], run_kind=RunKinds.TRAINING)

    check_asserts(prepare_mocks)


def test_values_range_int():
    list_to_check_1 = ["1", "3", "5", "7", "9"]
    list_to_check_2 = ["2", "4", "6", "8", "10"]

    ret_list = values_range("1...10:2")
    assert list_to_check_1 == ret_list

    ret_list = values_range("2...10:2")
    assert list_to_check_2 == ret_list


def test_values_range_float():
    list_to_check_1 = ["0.1", "0.2", "0.3", "0.4", "0.5"]
    list_to_check_2 = ["1.0", "2.0", "3.0", "4.0", "5.0"]
    list_to_check_3 = ["0.125", "0.25", "0.375", "0.5", "0.625"]

    ret_list = values_range("0.1...0.5:0.1")
    assert list_to_check_1 == ret_list

    ret_list = values_range("1.0...5.0:1.0")
    assert list_to_check_2 == ret_list

    ret_list = values_range("0.125...0.725:0.125")
    assert list_to_check_3 == ret_list


def test_prepare_list_of_values():
    list_of_params = ['param1=1', 'param1=2', 'param1=3']
    ret_list = prepare_list_of_values("param1", "{1 ,2, 3}")
    assert ret_list == list_of_params

    range_of_params = ["param2=0.1", "param2=0.2", "param2=0.3", "param2=0.4", "param2=0.5", ]
    ret_list = prepare_list_of_values("param2", "{0.1...0.5:0.1}")
    assert ret_list == range_of_params


def test_analyze_pr_parameters_list_success():
    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    two_params_list_result = [("param1=0", "param2=0"), ("param1=0", "param2=1"), ("param1=0", "param2=2"),
                              ("param1=1", "param2=0"), ("param1=1", "param2=1"), ("param1=1", "param2=2")]
    ret_list = analyze_pr_parameters_list(two_params_list)
    assert ret_list == two_params_list_result


def test_analyze_pr_parameters_list_ambiguosly_defined():
    identical_param_list = [("param1", "{0, 1}"), ("param1", "{0...2:1}")]
    with pytest.raises(ValueError) as exe:
        analyze_pr_parameters_list(identical_param_list)
    assert str(exe.value) == Texts.PARAM_AMBIGUOUSLY_DEFINED.format(param_name="param1")


def test_analyze_pr_parameters_list_missing_brackets():
    two_params_list = [("param1", "1, 2, 3"), ("param2", "{0...2:1}")]
    with pytest.raises(ValueError) as exe:
        analyze_pr_parameters_list(two_params_list)
    assert str(exe.value) == Texts.INCORRECT_PARAM_FORMAT_ERROR_MSG.format(param_name="param1")


def test_analyze_pr_parameters_list_wrong_format():
    two_params_list = [("param1", "1, 2, 3"), ("param2", "{a...b:1}")]
    with pytest.raises(ValueError) as exe:
        analyze_pr_parameters_list(two_params_list)
    assert str(exe.value) == Texts.INCORRECT_PARAM_FORMAT_ERROR_MSG.format(param_name="param1")


def test_analyze_ps_parameters_list_success():
    three_params = ("{param1:value1, param2:value2, param3:value3}",)
    three_params_output = [("param1=value1", "param2=value2", "param3=value3")]
    output = analyze_ps_parameters_list(three_params)
    assert output == three_params_output

    one_param = ("{param1: value2}",)
    one_param_output = [("param1= value2",)]
    output = analyze_ps_parameters_list(one_param)
    assert output == one_param_output

    multiple_two_params = ("{param1: value2, param2:value3}", "{param1:value4,param3:value5}")
    multiple_two_params_output = [("param1= value2", "param2=value3"),
                                  ("param1=value4", "param3=value5")]
    output = analyze_ps_parameters_list(multiple_two_params)
    assert output == multiple_two_params_output


def test_analyze_ps_parameters_wrong_format():
    three_params = ("{param1:value1, param2:value2, param3:value3",)
    with pytest.raises(ValueError) as exe:
        analyze_ps_parameters_list(three_params)
    assert str(exe.value) == Texts.PARAM_SET_INCORRECT_FORMAT_ERROR_MSG


def test_check_enclosing_brackets():
    success = "{correct value}"
    assert check_enclosing_brackets(success)

    wrong_format = "wrong format}"
    assert not check_enclosing_brackets(wrong_format)

    missing_value = ""
    assert not check_enclosing_brackets(missing_value)


def test_create_list_of_runs_pr_only(mocker):
    experiment_name = "experiment_name"
    template_name = "template_name"
    mocker.patch("platform_resources.experiments.generate_exp_name_and_labels", side_effect=[(experiment_name, {})])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    two_params_list_result = \
        [RunSubmission(name=experiment_name + "-1", experiment_name=experiment_name,
                       parameters=("param1=0", "param2=0")),
         RunSubmission(name=experiment_name + "-2", experiment_name=experiment_name,
                       parameters=("param1=0", "param2=1")),
         RunSubmission(name=experiment_name + "-3", experiment_name=experiment_name,
                       parameters=("param1=0", "param2=2")),
         RunSubmission(name=experiment_name + "-4", experiment_name=experiment_name,
                       parameters=("param1=1", "param2=0")),
         RunSubmission(name=experiment_name + "-5", experiment_name=experiment_name,
                       parameters=("param1=1", "param2=1")),
         RunSubmission(name=experiment_name + "-6", experiment_name=experiment_name,
                       parameters=("param1=1", "param2=2"))]

    output = prepare_list_of_runs(parameter_range=two_params_list, experiment_name=experiment_name,
                                  parameter_set=(), template_name=template_name)
    assert len(output) == 6
    for expected_run, result_run in zip(two_params_list_result, output):
        assert expected_run.parameters == result_run.parameters


def test_create_list_of_runs_ps_only(mocker):
    experiment_name = "experiment_name"
    template_name = "template_name"
    mocker.patch("platform_resources.experiments.generate_exp_name_and_labels", side_effect=[(experiment_name, {})])

    multiple_two_params = ("{param1:0, param2:1}", "{param1:2,param3:3}")
    multiple_two_params_list_result = \
        [RunSubmission(name=experiment_name + "-1", experiment_name=experiment_name,
                       parameters=("param1=0", "param2=1")),
         RunSubmission(name=experiment_name + "-2", experiment_name=experiment_name,
                       parameters=("param1=2", "param3=3"))]
    output = prepare_list_of_runs(parameter_range=[], experiment_name=experiment_name,
                                  parameter_set=multiple_two_params, template_name=template_name)
    assert len(output) == 2
    for expected_run, result_run in zip(multiple_two_params_list_result, output):
        assert expected_run.parameters == result_run.parameters


def test_create_list_of_runs_pr_and_ps(mocker):
    experiment_name = "experiment_name"
    template_name = "template_name"
    mocker.patch("platform_resources.experiments.generate_exp_name_and_labels", side_effect=[(experiment_name, {})])

    two_params_list = [("param1", "{0, 1}"), ("param2", "{0...2:1}")]
    multiple_two_params = ("{param3:0, param4:1}", "{param3:2,param4:3}")

    expected_result = [RunSubmission(name=experiment_name + "-1", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=0", "param2=0")),
                       RunSubmission(name=experiment_name + "-2", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=0", "param2=1")),
                       RunSubmission(name=experiment_name + "-3", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=0", "param2=2")),
                       RunSubmission(name=experiment_name + "-4", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=1", "param2=0")),
                       RunSubmission(name=experiment_name + "-5", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=1", "param2=1")),
                       RunSubmission(name=experiment_name + "-6", experiment_name=experiment_name,
                                     parameters=("param3=0", "param4=1", "param1=1", "param2=2")),
                       RunSubmission(name=experiment_name + "-7", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=0", "param2=0")),
                       RunSubmission(name=experiment_name + "-8", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=0", "param2=1")),
                       RunSubmission(name=experiment_name + "-9", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=0", "param2=2")),
                       RunSubmission(name=experiment_name + "-10", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=1", "param2=0")),
                       RunSubmission(name=experiment_name + "-11", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=1", "param2=1")),
                       RunSubmission(name=experiment_name + "-12", experiment_name=experiment_name,
                                     parameters=("param3=2", "param4=3", "param1=1", "param2=2"))]

    output = prepare_list_of_runs(two_params_list, experiment_name, multiple_two_params, template_name=template_name)
    assert len(output) == 12

    for expected_run, result_run in zip(expected_result, output):
        assert expected_run.parameters == result_run.parameters


def test_submit_experiment_without_file(prepare_mocks: SubmitExperimentMocks):
    runs_list, _ = submit_experiment(script_location=None, script_folder_location=None,
                                     template='', name='', parameter_range=[],
                                     parameter_set=(), script_parameters=(), pack_params=[], run_kind=RunKinds.TRAINING)
    assert len(runs_list) == 1
    assert runs_list[0].name == "experiment_name"

    check_asserts(prepare_mocks)


def test_check_run_environment(mocker):
    del_env = mocker.patch("commands.experiment.common.delete_environment")
    mocker.patch("click.confirm", return_value=True)

    mocker.patch('os.path.isdir').return_value = False
    mocker.patch('os.listdir').return_value = False

    check_run_environment(FAKE_CLI_EXPERIMENT_PATH)

    assert del_env.call_count == 0


def test_check_run_environment_clear(mocker):
    del_env = mocker.patch("commands.experiment.common.delete_environment")
    mocker.patch("click.confirm", return_value=True)
    mocker.patch("commands.experiment.common.Path.touch")
    mocker.patch('os.path.isdir').return_value = True
    mocker.patch('os.listdir').return_value = True

    check_run_environment(FAKE_CLI_EXPERIMENT_PATH)

    assert del_env.call_count == 1


def test_check_run_environment_clear_not_confirmed(mocker):
    mocker.patch("click.confirm", return_value=False)

    mocker.patch('os.path.isdir').return_value = True
    mocker.patch('os.listdir').return_value = True

    with pytest.raises(SystemExit):
        check_run_environment(FAKE_CLI_EXPERIMENT_PATH)


def test_validate_pack_params_names_valid(mocker):
    try:
        validate_pack_params_names(None, None, [(EXAMPLE_PACK_PARAM_KEY, EXAMPLE_PACK_PARAM_VALUE)])
    except Exception:
        pytest.fail("Exception should not be thrown when validating example pack params.")


def test_validate_pack_params_names_invalid(mocker):
    with pytest.raises(SystemExit):
        validate_pack_params_names(None, None, [(INVALID_PACK_PARAM_KEY, EXAMPLE_PACK_PARAM_VALUE)])


def test_get_log_filename_log_found():
    log_filename = get_log_filename(LOG_WITH_FILE)

    assert log_filename == LOG_FILENAME


def test_get_log_filename_log_not_found():
    log_filename = get_log_filename(LOG_WITHOUT_FILE)

    assert not log_filename
