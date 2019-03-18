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

import dateutil

from commands import common
from platform_resources.run import Run, RunStatus
from platform_resources.experiment import Experiment

TEST_RUNS = [Run(name='test-experiment', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                 creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                 state=RunStatus.QUEUED, experiment_name='test-experiment', pod_count=0, pod_selector={}),
             Run(name='test-experiment-2', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                 creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                 state=RunStatus.COMPLETE, experiment_name='test-experiment', pod_count=0, pod_selector={})]


TEST_RUNS_CREATING = [Run(name='test-experiment-1', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                          state=RunStatus.QUEUED, experiment_name='test-experiment-1', pod_count=0, pod_selector={}),
                      Run(name='test-experiment-2', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                          state=RunStatus.COMPLETE, experiment_name='test-experiment-1', pod_count=0, pod_selector={}),
                      Run(name='test-experiment-3', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                          state=None, experiment_name='test-experiment-2', pod_count=0, pod_selector={}),
                      Run(name='test-experiment-4', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                          state=None, experiment_name='test-experiment-3', pod_count=0, pod_selector={}),
                      Run(name='test-experiment-5', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-04-26T13:43:01Z', namespace='namespace-1',
                          state=None, experiment_name='test-experiment-2', pod_count=0, pod_selector={}),
                      Run(name='test-experiment-6', parameters=['a 1', 'b 2'], metrics={'acc': 52.2, 'loss': 1.62345},
                          creation_timestamp='2018-05-08T13:05:04Z', namespace='namespace-2',
                          state=RunStatus.COMPLETE, experiment_name='test-experiment-4', pod_count=0, pod_selector={})]


TEST_EXPERIMENT = Experiment(name="test-experiment", parameters_spec=["param1"],
                             namespace="submitter", creation_timestamp="2018-05-08T13:05:04Z",
                             template_name="template_name", template_namespace="template_namespace")

TEST_NONINITIALIZED_EXPERIMENTS = [Experiment(name="noninit-test-experiment", parameters_spec=["param1"],
                                              namespace="submitter", creation_timestamp="2018-05-08T13:05:04Z",
                                              template_name="template_name", template_namespace="template_namespace"),
                                   Experiment(name="noninit2-test-experiment", parameters_spec=["param1"],
                                              namespace="submitter", creation_timestamp="2018-05-08T13:05:04Z",
                                              template_name="template_name", template_namespace="template_namespace")]

TEST_RUN = Run(name="test-experiment", experiment_name="test-experiment", metrics={},
               parameters=["param1"], pod_count=0, pod_selector={}, state=RunStatus.CREATING,
               namespace="submitter", creation_timestamp="2018-05-08T13:05:04Z",
               template_name="template_name")

TEST_LIST_HEADERS = ["Name", "Parameters", "Metrics", "Submission date", "Owner", "Status", "Template name"]


def test_list_unitialized_experiments_in_cli_success(mocker, capsys):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.return_value = TEST_RUNS

    api_list_experiments_mock = mocker.patch("commands.common.Experiment.list")
    api_list_experiments_mock.return_value = TEST_NONINITIALIZED_EXPERIMENTS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    common.list_unitialized_experiments_in_cli(verbosity_lvl=0, all_users=False, name="", listed_runs_kinds=[],
                                               headers=TEST_LIST_HEADERS, brief=False)

    captured = capsys.readouterr()

    assert "noninit-test-experiment" in captured.out
    assert "noninit2-test-experiment" in captured.out

    assert get_namespace_mock.call_count == 1
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"
    assert api_list_experiments_mock.call_count == 1, "Experiments weren't retrieved"


def test_list_unitialized_experiments_in_cli_one_row(mocker, capsys):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.return_value = TEST_RUNS

    api_list_experiments_mock = mocker.patch("commands.common.Experiment.list")
    api_list_experiments_mock.return_value = TEST_NONINITIALIZED_EXPERIMENTS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    common.list_unitialized_experiments_in_cli(verbosity_lvl=0, all_users=False, name="", listed_runs_kinds=[],
                                               headers=TEST_LIST_HEADERS, count=1, brief=False)

    captured = capsys.readouterr()

    assert "noninit-test-experiment" not in captured.out
    assert "noninit2-test-experiment" in captured.out

    assert get_namespace_mock.call_count == 1
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"
    assert api_list_experiments_mock.call_count == 1, "Experiments weren't retrieved"


def test_list_experiments_success(mocker):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.return_value = TEST_RUNS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    common.list_runs_in_cli(verbosity_lvl=0, all_users=False, name="", status=None, listed_runs_kinds=[],
                            runs_list_headers=TEST_LIST_HEADERS, with_metrics=False, brief=False)

    assert get_namespace_mock.call_count == 1
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"


def test_list_experiments_all_users_success(mocker):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.return_value = TEST_RUNS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    common.list_runs_in_cli(verbosity_lvl=0, all_users=True, name="", status=None, listed_runs_kinds=[],
                            runs_list_headers=TEST_LIST_HEADERS, with_metrics=False, brief=False)

    assert get_namespace_mock.call_count == 0
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"


def test_list_experiments_failure(mocker):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.side_effect = RuntimeError

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")
    sys_exit_mock = mocker.patch.object(common, "exit")

    common.list_runs_in_cli(verbosity_lvl=0, all_users=False, name="", status=None, listed_runs_kinds=[],
                            runs_list_headers=TEST_LIST_HEADERS, with_metrics=False, brief=False)

    assert get_namespace_mock.call_count == 1
    assert api_list_runs_mock.call_count == 1, "Runs retrieval was not called"
    assert sys_exit_mock.called_once_with(1)


def test_list_experiments_one_user_success(mocker, capsys):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    mocker.patch("dateutil.tz.tzlocal").return_value = dateutil.tz.UTC
    api_list_runs_mock.return_value = TEST_RUNS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    headers = ["Name", "Submission date", "Owner", "Status"]

    common.list_runs_in_cli(verbosity_lvl=0, all_users=True, name="", status=None, listed_runs_kinds=[],
                            runs_list_headers=headers, with_metrics=False, count=1, brief=False)

    captured = capsys.readouterr()

    assert "2018-04-26 01:43:01 PM" not in captured.out
    assert "2018-05-08 01:05:04 PM" in captured.out
    assert "Parameters" not in captured.out
    assert "Owner" in captured.out
    assert get_namespace_mock.call_count == 0
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"


def test_list_experiments_brief_success(mocker, capsys):
    api_list_runs_mock = mocker.patch("commands.common.Run.list")
    api_list_runs_mock.return_value = TEST_RUNS

    get_namespace_mock = mocker.patch("commands.common.get_kubectl_current_context_namespace")

    common.list_runs_in_cli(verbosity_lvl=0, all_users=True, name="", status=None, listed_runs_kinds=[],
                            runs_list_headers=TEST_LIST_HEADERS, with_metrics=False, brief=True)

    captured = capsys.readouterr()

    assert "a 1 b 2" not in captured.out
    assert "test-experiment-2" in captured.out
    assert get_namespace_mock.call_count == 0
    assert api_list_runs_mock.call_count == 1, "Runs were not retrieved"


def test_create_fake_run():
    assert TEST_RUN == common.create_fake_run(TEST_EXPERIMENT)


def test_replace_initalizing_runs_no_changes():
    assert len(common.replace_initializing_runs(TEST_RUNS)) == 2


def test_replace_initializing_runs_two_not_ready(mocker):
    get_experiment_mock = mocker.patch("commands.common.Experiment.get", return_value=TEST_EXPERIMENT)
    assert len(common.replace_initializing_runs(TEST_RUNS_CREATING)) == 5
    assert get_experiment_mock.call_count == 2
