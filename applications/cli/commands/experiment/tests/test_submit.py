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

from click.testing import CliRunner
import pytest

from commands.experiment.submit import submit, DEFAULT_SCRIPT_NAME, validate_script_location, \
    validate_script_folder_location, get_default_script_location, clean_script_parameters, validate_pack_params, \
    check_duplicated_params
from commands.experiment.common import RunSubmission, RunStatus
from util.exceptions import SubmitExperimentError
from cli_text_consts import ExperimentSubmitCmdTexts as Texts
from cli_text_consts import ExperimentCommonTexts as CommonTexts


SCRIPT_LOCATION = "training_script.py"
SCRIPT_FOLDER = "/a/b/c"

SUBMITTED_RUNS = [RunSubmission(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                                experiment_name='test-experiment',
                                state=RunStatus.QUEUED)]

FAILED_RUNS = [RunSubmission(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                             experiment_name='test-experiment',
                             state=RunStatus.QUEUED),
               RunSubmission(name="exp-mnist-single-node.py-18.05.18-16.05.45-1-tf-training",
                             experiment_name='test-experiment',
                             state=RunStatus.FAILED)
               ]


class SubmitMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.submit_experiment = mocker.patch("commands.experiment.submit.submit_experiment",
                                              return_value=(SUBMITTED_RUNS, ""))
        self.isfile = mocker.patch("os.path.isfile", return_value=True)
        self.isdir = mocker.patch("os.path.isdir", return_value=False)
        self.check_duplicated_params = mocker.patch("commands.experiment.submit.check_duplicated_params")
        self.validate_pack_params = mocker.patch("commands.experiment.submit.validate_pack_params")
        self.validate_experiment_name = mocker.patch("commands.experiment.submit.validate_experiment_name")
        self.validate_script_location = mocker.patch("commands.experiment.submit.validate_script_location")
        self.validate_script_folder_location = mocker.patch(
            "commands.experiment.submit.validate_script_folder_location")
        self.get_default_script_location = mocker.patch(
            "commands.experiment.submit.get_default_script_location")
        self.clean_script_parameters = mocker.patch("commands.experiment.submit.clean_script_parameters")
        self.get_list_of_packs = mocker.patch("commands.experiment.common.get_list_of_packs",
                                              return_value=["tf-training-tfjob"])
        self.validate_pack = mocker.patch("commands.experiment.submit.validate_pack")


@pytest.fixture
def prepare_mocks(mocker) -> SubmitMocks:
    return SubmitMocks(mocker=mocker)


def test_missing_file(prepare_mocks: SubmitMocks):
    prepare_mocks.validate_script_location.side_effect = SystemExit(2)

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])
    assert result.exit_code == 2


def test_missing_folder(prepare_mocks: SubmitMocks):
    prepare_mocks.validate_script_folder_location.side_effect = SystemExit(2)

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, "-sfl", SCRIPT_FOLDER])
    assert result.exit_code == 2


def test_invalid_pack_param_arguments(prepare_mocks: SubmitMocks):
    prepare_mocks.validate_pack_params.side_effect = SystemExit(2)

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, "--pack-param", "arg1", "val1", "--pack-param", "arg1",
                                         "val2", "-sfl", SCRIPT_FOLDER])
    assert result.exit_code == 2


def test_submit_experiment_failure(prepare_mocks: SubmitMocks):
    exe_message = "error message"
    prepare_mocks.submit_experiment.side_effect = SubmitExperimentError(exe_message)

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])

    assert Texts.SUBMIT_ERROR_MSG.format(exception_message=exe_message) in result.output
    assert result.exit_code == 1


def test_submit_experiment_success(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])

    assert SUBMITTED_RUNS[0].name in result.output
    assert SUBMITTED_RUNS[0].state.value in result.output


def test_submit_with_incorrect_name_fail(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, '-n', 'Wrong_&name'])
    assert 'name must consist of lower case alphanumeric characters' in result.output
    assert result.exit_code == 2


def test_submit_default_script_name(prepare_mocks: SubmitMocks):
    script_location = 'some-dir/'
    prepare_mocks.get_default_script_location.return_value = os.path.join(script_location,
                                                                          DEFAULT_SCRIPT_NAME)

    runner = CliRunner()
    parameters = [script_location]

    result = runner.invoke(submit, parameters, input="y")

    assert result.exit_code == 0


def test_submit_default_script_name_wrong_dir(prepare_mocks: SubmitMocks):
    script_location = 'wrong-dir/'
    prepare_mocks.isdir.return_value = True
    prepare_mocks.get_default_script_location.side_effect = SystemExit(2)

    runner = CliRunner()
    parameters = [script_location]

    result = runner.invoke(submit, parameters, input="y")

    assert result.exit_code == 2


def test_duplicated_pack_params(prepare_mocks: SubmitMocks):
    pack_params = [('arg1', 'val1'), ('arg2', 'val1'), ('arg1', 'val3'), ('arg3', 'val6')]
    with pytest.raises(SystemExit):
        check_duplicated_params(pack_params)


def test_validate_pack_params(prepare_mocks: SubmitMocks):
    prepare_mocks.check_duplicated_params.side_effect = SystemExit(2)

    with pytest.raises(SystemExit):
        validate_pack_params([('arg1', 'val1'), ('arg1', 'val2')])


def test_submit_invalid_script_folder_location(prepare_mocks: SubmitMocks):
    prepare_mocks.isdir.return_value = True
    prepare_mocks.validate_script_folder_location.side_effect = SystemExit(2)

    script_folder_location = '/wrong-directory'

    runner = CliRunner()
    parameters = [SCRIPT_LOCATION, '--script-folder-location', script_folder_location]

    result = runner.invoke(submit, parameters, input="y")
    assert result.exit_code == 2


def test_validate_script_location(prepare_mocks: SubmitMocks):
    prepare_mocks.isdir.return_value = False
    prepare_mocks.isfile.return_value = False

    with pytest.raises(SystemExit):
        validate_script_location('bla.py')


def test_validate_script_folder_location(prepare_mocks: SubmitMocks):
    prepare_mocks.isdir.return_value = False

    with pytest.raises(SystemExit):
        validate_script_folder_location('/bla')


def test_get_default_script_location_missing_file(prepare_mocks: SubmitMocks):
    prepare_mocks.isfile.return_value = False
    with pytest.raises(SystemExit):
        get_default_script_location('/bla')


def test_get_default_script_location(prepare_mocks: SubmitMocks):
    prepare_mocks.isfile.return_value = True

    test_dir = '/bla'

    assert get_default_script_location(test_dir) == os.path.join(test_dir, DEFAULT_SCRIPT_NAME)


def test_submit_experiment_one_failed(prepare_mocks: SubmitMocks):
    prepare_mocks.submit_experiment.return_value = (FAILED_RUNS, "")
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])

    assert FAILED_RUNS[0].name in result.output
    assert FAILED_RUNS[0].state.value in result.output
    assert FAILED_RUNS[1].name in result.output
    assert FAILED_RUNS[1].state.value in result.output

    assert result.exit_code == 1


def test_clean_script_parameters_empty(prepare_mocks: SubmitMocks):
    assert () == clean_script_parameters(None, None, ())


def test_clean_script_parameters_with_backslash(prepare_mocks: SubmitMocks):
    assert ("aaa", "bbb", "ccc") == clean_script_parameters(None, None, ("\\aaa", "bbb", "ccc"))


def test_submit_experiment_wrong_template(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, "-t", "wrong_template"])

    assert CommonTexts.INCORRECT_TEMPLATE_NAME in result.output


def test_submit_requirements(prepare_mocks: SubmitMocks, tmpdir):
    experiment_dir = tmpdir.mkdir("text-exp")
    fake_requirements_file = experiment_dir.join("requirements.txt")
    fake_requirements_file.write('fake-dependency==0.0.1')

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, '--requirements', fake_requirements_file.strpath])

    _, submit_experiment_kwargs = prepare_mocks.submit_experiment.call_args
    assert submit_experiment_kwargs.get('requirements_file') == fake_requirements_file.strpath
    assert result.exit_code == 0


def test_submit_requirements_wrong_path(prepare_mocks: SubmitMocks, tmpdir):
    empty_dir = tmpdir.mkdir("text-exp")
    wrong_requirements_file_path = os.path.join(empty_dir.strpath, 'requirements.txt')
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, '--requirements', wrong_requirements_file_path])

    assert wrong_requirements_file_path in result.output
    assert result.exit_code == 2
