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


class InteractMocks:
    def __init__(self, mocker, get_namespace, list_experiments, submit_experiment, launch_app) -> None:
        self.mocker = mocker
        self.get_namespace = get_namespace
        self.list_experiments = list_experiments
        self.submit_experiment = submit_experiment
        self.launch_app = launch_app


@pytest.fixture
def prepare_mocks(mocker) -> InteractMocks:
    get_namespace_mock = mocker.patch("commands.experiment.interact.get_kubectl_current_context_namespace",
                                      side_effect=[EXPERIMENT_NAMESPACE])
    list_experiments_mock = mocker.patch("commands.experiment.interact.list_experiments",
                                         return_value=[])
    submit_experiment_mock = mocker.patch("commands.experiment.interact.submit_experiment")
    launch_app_mock = mocker.patch("commands.experiment.interact.launch_app")

    return InteractMocks(mocker=mocker, get_namespace=get_namespace_mock, list_experiments=list_experiments_mock,
                         submit_experiment=submit_experiment_mock, launch_app=launch_app_mock)


def check_asserts(prepare_mocks: InteractMocks, get_namespace_count=1, list_experiments_count=1,
                  submit_experiment_count=1, launch_app_count=1):
    assert prepare_mocks.get_namespace.call_count == get_namespace_count, "Namespace wasn't gathered."
    assert prepare_mocks.list_experiments.call_count == list_experiments_count, "Experiments weren't listed."
    assert prepare_mocks.submit_experiment.call_count == submit_experiment_count, "Experiment wasn't submitted."
    assert prepare_mocks.launch_app.call_count == launch_app_count, "App wasn't launched."


def test_interact_incorrect_name(prepare_mocks: InteractMocks):
    result = CliRunner().invoke(interact.interact, ["-n", INCORRECT_INTERACT_NAME])

    assert "name must consist of lower case alphanumeric characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=0, list_experiments_count=0, submit_experiment_count=0,
                  launch_app_count=0)

    result = CliRunner().invoke(interact.interact, ["-n", TOO_LONG_INTERACT_NAME])

    assert "Name cannot be longer than 30 characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=0, list_experiments_count=0, submit_experiment_count=0,
                  launch_app_count=0)


def test_error_when_listing_experiments(prepare_mocks: InteractMocks):
    prepare_mocks.list_experiments.side_effect = RuntimeError("error")

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert "Problems during loading a list of experiments" in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_incorrect_experiment_type(prepare_mocks: InteractMocks):
    prepare_mocks.list_experiments.return_value = [NON_JUPYTER_EXPERIMENT]

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert "is already used by an experiment other than Jupyter Notebook." in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_dont_continue_if_exp_doesnt_exist(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME], input="n")

    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_launch_app_only(prepare_mocks: InteractMocks):
    prepare_mocks.list_experiments.return_value = [JUPYTER_EXPERIMENT]
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=1, submit_experiment_count=0,
                  launch_app_count=1)


def test_full_interact_success(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME], input="y")

    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=1, submit_experiment_count=1,
                  launch_app_count=1)


def test_full_interact_without_name(prepare_mocks: InteractMocks):
    CliRunner().invoke(interact.interact)

    check_asserts(prepare_mocks, get_namespace_count=1, list_experiments_count=0, submit_experiment_count=1,
                  launch_app_count=1)
