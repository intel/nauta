#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from click.testing import CliRunner
import pytest

from kubernetes import client

from platform_resources.experiment import Experiment, ExperimentStatus
from commands.experiment import interact
from commands.experiment.common import RunStatus, SubmitExperimentError
from cli_text_consts import ExperimentInteractCmdTexts as Texts
from platform_resources.run import Run, KubernetesObject

INCORRECT_INTERACT_NAME = "interact_experiment"
TOO_LONG_INTERACT_NAME = "interact-experiment-interact-experiment-interact-experiment"
CORRECT_INTERACT_NAME = "interact-experiment"

EXPERIMENT_NAMESPACE = "namespace"

JUPYTER_EXPERIMENT = Experiment(name='test-experiment', parameters_spec=['a 1', 'b 2'],
                                creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                                state=ExperimentStatus.CREATING, template_name='jupyter',
                                template_namespace='test-ex-namespace')

NON_JUPYTER_EXPERIMENT = Experiment(name='test-experiment-2', parameters_spec=['a 1', 'b 2'],
                                    creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                                    state=ExperimentStatus.SUBMITTED, template_name='test-ex-template',
                                    template_namespace='test-ex-namespace')
SUBMITTED_RUNS = [Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                      experiment_name=CORRECT_INTERACT_NAME,
                      state=RunStatus.QUEUED)]

KO_EXPERIMENT = KubernetesObject(spec=JUPYTER_EXPERIMENT, metadata=client.V1ObjectMeta())


class InteractMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.get_namespace = mocker.patch("commands.experiment.interact.get_kubectl_current_context_namespace",
                                          side_effect=[EXPERIMENT_NAMESPACE, EXPERIMENT_NAMESPACE])
        self.get_experiment = mocker.patch("commands.experiment.interact.Experiment.get",
                                           return_value=None)
        self.submit_experiment = mocker.patch("commands.experiment.interact.submit_experiment",
                                              return_value=(SUBMITTED_RUNS, {}, ""))
        self.launch_app = mocker.patch("commands.experiment.interact.launch_app")
        self.check_pods_status = mocker.patch("commands.experiment.interact.check_pods_status", return_value=True)
        self.calc_number = mocker.patch("commands.experiment.interact.calculate_number_of_running_jupyters",
                                        return_value=1)


@pytest.fixture
def prepare_mocks(mocker) -> InteractMocks:
    return InteractMocks(mocker=mocker)


def check_asserts(prepare_mocks: InteractMocks, get_namespace_count=1, get_experiment_count=1,
                  submit_experiment_count=1, launch_app_count=1, calc_number_count=1):
    assert prepare_mocks.get_namespace.call_count == get_namespace_count, "Namespace wasn't gathered."
    assert prepare_mocks.get_experiment.call_count == get_experiment_count, "Experiment wasn't gathered."
    assert prepare_mocks.submit_experiment.call_count == submit_experiment_count, "Experiment wasn't submitted."
    assert prepare_mocks.launch_app.call_count == launch_app_count, "App wasn't launched."
    assert prepare_mocks.calc_number.call_count == calc_number_count, "Experiments weren't counted."


def test_interact_incorrect_name(prepare_mocks: InteractMocks):
    result = CliRunner().invoke(interact.interact, ["-n", INCORRECT_INTERACT_NAME], input="y")

    assert "name must consist of lower case alphanumeric characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)

    result = CliRunner().invoke(interact.interact, ["-n", TOO_LONG_INTERACT_NAME], input="y")

    assert "Name given by a user cannot be longer than 30 characters" in result.output
    check_asserts(prepare_mocks, get_namespace_count=2, get_experiment_count=2, submit_experiment_count=0,
                  launch_app_count=0, calc_number_count=2)


def test_error_when_listing_experiments(prepare_mocks: InteractMocks):
    prepare_mocks.get_experiment.side_effect = RuntimeError("error")

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert Texts.EXPERIMENT_GET_ERROR_MSG in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)


def test_incorrect_experiment_type(prepare_mocks: InteractMocks):
    prepare_mocks.get_experiment.return_value = NON_JUPYTER_EXPERIMENT

    result = CliRunner().invoke(interact.interact, ["-n", CORRECT_INTERACT_NAME])

    assert Texts.NAME_ALREADY_USED.format(name=CORRECT_INTERACT_NAME) in result.output
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

    assert Texts.NOTEBOOK_NOT_READY_ERROR_MSG in result.output


def test_interact_error_when_submitting(prepare_mocks: InteractMocks):

    prepare_mocks.submit_experiment.side_effect = SubmitExperimentError("error")
    result = CliRunner().invoke(interact.interact)
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=1,
                  launch_app_count=0)
    assert Texts.SUBMIT_ERROR_MSG.format(exception_message="error") in result.output


def test_interact_other_error_when_submitting(prepare_mocks: InteractMocks):

    prepare_mocks.submit_experiment.side_effect = RuntimeError("error")
    result = CliRunner().invoke(interact.interact)
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=1,
                  launch_app_count=0)
    assert Texts.SUBMIT_OTHER_ERROR_MSG in result.output


def test_calculate_number_of_running_jupyters(mocker):
    exp_list = mocker.patch("commands.experiment.interact.list_k8s_experiments_by_label", return_value=[KO_EXPERIMENT])

    count = interact.calculate_number_of_running_jupyters()

    assert count == 1
    assert exp_list.call_count == 1


def test_interact_too_much_notebooks(prepare_mocks: InteractMocks):
    prepare_mocks.calc_number.return_value = 4
    result = CliRunner().invoke(interact.interact, input="n")

    assert Texts.INTERACT_ABORT_MSG in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=0, submit_experiment_count=0,
                  launch_app_count=0)


def test_interact_reconnect_to_session_with_filename(prepare_mocks: InteractMocks, tmpdir):
    prepare_mocks.get_experiment.return_value = JUPYTER_EXPERIMENT
    test_dir = tmpdir.mkdir('test-dir')
    test_file = test_dir.join('file.py')
    test_file.write('pass')
    result = CliRunner().invoke(interact.interact, ["-n", JUPYTER_EXPERIMENT.name, "--filename", test_file.strpath],
                                input="y")

    assert Texts.FILENAME_BUT_SESSION_EXISTS in result.output
    check_asserts(prepare_mocks, get_namespace_count=1, get_experiment_count=1, submit_experiment_count=0,
                  launch_app_count=0)
