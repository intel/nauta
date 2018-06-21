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

from click.testing import CliRunner
import pytest

from commands.experiment.submit import submit
from commands.experiment.common import RunDescription, RunStatus
from util.exceptions import SubmitExperimentError

SCRIPT_LOCATION = "training_script.py"
SCRIPT_FOLDER = "/a/b/c"

SUBMITTED_RUNS = [RunDescription(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                                 status=RunStatus.QUEUED)]


class SubmitMocks:
    def __init__(self, mocker, submit_experiment=None, isfile=None,
                 isdir=None) -> None:
        self.mocker = mocker
        self.submit_experiment = submit_experiment
        self.isfile = isfile
        self.isdir = isdir


@pytest.fixture
def prepare_mocks(mocker) -> SubmitMocks:
    submit_experiment_mock = mocker.patch("commands.experiment.submit.submit_experiment",
                                          return_value=SUBMITTED_RUNS)
    isfile_mock = mocker.patch("os.path.isfile", return_value=True)
    isdir_mock = mocker.patch("os.path.isdir", return_value=True)

    return SubmitMocks(mocker=mocker, submit_experiment=submit_experiment_mock, isfile=isfile_mock, isdir=isdir_mock)


def check_asserts(prepare_mocks: SubmitMocks, submit_experiment_count=1, isfile_count=1, isdir_count=1):
    assert prepare_mocks.isfile.call_count == isfile_count, "Script location was not checked"
    assert prepare_mocks.get_namespace.call_count == submit_experiment_count, "Experiment wasn't submitted"
    assert prepare_mocks.isdir.call_count == isdir_count, "Dir wasn't checked"


def test_missing_file(prepare_mocks: SubmitMocks):
    prepare_mocks.isfile.return_value = False

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])
    assert 'Cannot find script:' in result.output


def test_missing_folder(prepare_mocks: SubmitMocks):
    prepare_mocks.isdir.return_value = False

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, "-sfl", SCRIPT_FOLDER])
    assert 'Cannot find script folder:' in result.output


def test_submit_experiment_failure(prepare_mocks: SubmitMocks):
    exe_message = "error message"
    prepare_mocks.submit_experiment.side_effect = SubmitExperimentError(exe_message)

    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])

    assert f"Problems during submitting experiment:{exe_message}" in result.output


def test_submit_experiment_success(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION])

    assert SUBMITTED_RUNS[0].name in result.output
    assert SUBMITTED_RUNS[0].status.value in result.output


def test_submit_with_incorrect_name_fail(prepare_mocks: SubmitMocks):
    result = CliRunner().invoke(submit, [SCRIPT_LOCATION, '-n', 'Wrong_&name'])
    assert 'name must consist of lower case alphanumeric characters' in result.output
