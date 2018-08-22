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

from platform_resources.experiment_model import Experiment, ExperimentStatus
from commands.experiment import interact
from util.exceptions import SubmitExperimentError
from commands.experiment.common import RunDescription, RunStatus
from cli_text_consts import EXPERIMENT_INTERACT_CMD_TEXTS as TEXTS


INCORRECT_INTERACT_NAME = "interact_experiment"
TOO_LONG_INTERACT_NAME = "interact-experiment-interact-experiment-interact-experiment"
CORRECT_INTERACT_NAME = "interact-experiment"

EXPERIMENT_NAMESPACE = "namespace"

JUPYTER_EXPERIMENT = Experiment(name='test-experiment', parameters_spec=['a 1', 'b 2'],
                                creation_timestamp='2018-04-26T13:43:01Z', submitter='namespace-1',
                                state=ExperimentStatus.CREATING, template_name='jupyter',
                                template_namespace='test-ex-namespace')

NON_JUPYTER_EXPERIMENT = Experiment(name='test-experiment-2', parameters_spec=['a 1', 'b 2'],
                                    creation_timestamp='2018-05-08T13:05:04Z', submitter='namespace-2',
                                    state=ExperimentStatus.SUBMITTED, template_name='test-ex-template',
                                    template_namespace='test-ex-namespace')
SUBMITTED_RUNS = [RunDescription(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                                 status=RunStatus.QUEUED)]


class InteractMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.get_namespace = mocker.patch("commands.experiment.interact.get_kubectl_current_context_namespace",
                                          side_effect=[EXPERIMENT_NAMESPACE, EXPERIMENT_NAMESPACE])
        self.get_experiment = mocker.patch("commands.experiment.interact.get_experiment",
                                           return_value=None)
        self.submit_experiment = mocker.patch("commands.experiment.interact.submit_experiment",
                                              return_value=(SUBMITTED_RUNS, ""))
        self.launch_app = mocker.patch("commands.experiment.interact.launch_app")
        self.check_pods_status = mocker.patch("commands.experiment.interact.check_pods_status", return_value=True)


@pytest.fixture
def prepare_mocks(mocker) -> InteractMocks:
    return InteractMocks(mocker=mocker)


def check_asserts(prepare_mocks: InteractMocks, get_namespace_count=1, get_experiment_count=1,
                  submit_experiment_count=1, launch_app_count=1):
    assert prepare_mocks.get_namespace.call_count == get_namespace_count, "Namespace wasn't gathered."
    assert prepare_mocks.get_experiment.call_count == get_experiment_count, "Experiment wasn't gathered."
    assert prepare_mocks.submit_experiment.call_count == submit_experiment_count, "Experiment wasn't submitted."
    assert prepare_mocks.launch_app.call_count == launch_app_count, "App wasn't launched."


def test_interact_incorrect_name(prepare_mocks: InteractMocks):
    result = CliRunner().invoke(interact.interact, ["-n", INCORRECT_INTERACT_NAME], input="y")

    assert "name must consist of lower case alphanumeric characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)

    result = CliRunner().invoke(interact.interact, ["-n", TOO_LONG_INTERACT_NAME], input="y")

    assert "Name given by a user cannot be longer than 30 characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=2, get_experiment_count=2, submit_experiment_count=0,
                  launch_app_count=0)


def test_error_when_listing_experiments(prepare_mocks: InteractMocks):
    prepare_mocks.get_experiment.side_effect = RuntimeError("error")

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert TEXTS["experiment_get_error_msg"] in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_incorrect_experiment_type(prepare_mocks: InteractMocks):
    prepare_mocks.get_experiment.return_value = NON_JUPYTER_EXPERIMENT

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert TEXTS["name_already_used"].format(name=CORRECT_INTERACT_NAME) in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_dont_continue_if_exp_doesnt_exist(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME], input="n")

    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_launch_app_only(prepare_mocks: InteractMocks):
    prepare_mocks.get_experiment.return_value = JUPYTER_EXPERIMENT
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=1)


def test_full_interact_success(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME], input="y")

    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=1,
                  launch_app_count=1)


def test_full_interact_without_name(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact)

    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=1,
                  launch_app_count=1)
    assert prepare_mocks.submit_experiment.call_args[1]['name'].startswith('jup')


def test_interact_pods_not_created(prepare_mocks: InteractMocks):
    interact.JUPYTER_CHECK_POD_READY_TRIES = 1
    prepare_mocks.check_pods_status.return_value = False

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME], input="y")

    assert TEXTS["notebook_not_ready_error_msg"] in result.output


def test_interact_error_when_submitting(prepare_mocks: InteractMocks):

    prepare_mocks.submit_experiment.side_effect = SubmitExperimentError("error")
    result = CliRunner().invoke(interact.interact)
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=1,
                  launch_app_count=0)
    assert TEXTS["submit_error_msg"].format(exception_message="error") in result.output


def test_interact_other_error_when_submitting(prepare_mocks: InteractMocks):

    prepare_mocks.submit_experiment.side_effect = RuntimeError("error")
    result = CliRunner().invoke(interact.interact)
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=1,
                  launch_app_count=0)
    assert TEXTS["submit_other_error_msg"] in result.output
