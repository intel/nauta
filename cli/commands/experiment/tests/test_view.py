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
from unittest.mock import MagicMock
from kubernetes.client import V1Pod, V1PodStatus, V1Event, V1ObjectReference, V1ObjectMeta

from commands.experiment import view
from platform_resources.run_model import Run, RunStatus
from cli_text_consts import ExperimentViewCmdTexts as Texts
from util.k8s.k8s_statistics import ResourceUsage
from util.k8s.k8s_info import PodStatus


TEST_RUNS = [
    Run(
        name='test-experiment',
        parameters=['a 1', 'b 2'],
        creation_timestamp='2018-04-26T13:43:01Z',
        submitter='namespace-1',
        state=RunStatus.RUNNING,
        template_name='test-ex-template',
        metrics={'any metrics': 'a'},
        experiment_name='experiment_name',
        pod_count=1,
        pod_selector={}),
    Run(
        name='test-experiment-2',
        parameters=['a 1', 'b 2'],
        creation_timestamp='2018-05-08T13:05:04Z',
        submitter='namespace-2',
        state=RunStatus.COMPLETE,
        template_name='test-ex-template',
        metrics={'any metrics': 'a'},
        experiment_name='experiment_name',
        pod_count=1,
        pod_selector={})
]

QUEUED_RUN = [
    Run(
        name='test-experiment',
        parameters=['a 1', 'b 2'],
        creation_timestamp='2018-04-26T13:43:01Z',
        submitter='namespace-1',
        state=RunStatus.QUEUED,
        template_name='test-ex-template',
        metrics={'any metrics': 'a'},
        experiment_name='experiment_name',
        pod_count=1,
        pod_selector={})
]

TEST_PODS = [MagicMock(spec=V1Pod)]

pending_pod = MagicMock(spec=V1Pod)
pending_pod.status = V1PodStatus(phase=PodStatus.PENDING.value, conditions=[])
PENDING_POD = [pending_pod]

TOP_USERS = [ResourceUsage(user_name="user_name", cpu_usage=2, mem_usage=1000)]

EVENTS = [MagicMock(spec=V1Event(message="Insufficient cpu",
                                 involved_object=V1ObjectReference(name="test-experiment"),
                                 metadata=V1ObjectMeta(name="test-experiment")))]


class ViewMocks:
    def __init__(self, mocker):
        self.get_run = mocker.patch('commands.experiment.view.runs_api.get_run')
        self.get_run.return_value = TEST_RUNS[0]
        self.get_pods = mocker.patch('commands.experiment.view.get_namespaced_pods')
        self.get_pods.return_value = TEST_PODS
        self.get_namespace = mocker.patch('commands.experiment.view.get_kubectl_current_context_namespace')
        self.format_timestamp = mocker.patch('platform_resources.run_model.format_timestamp_for_cli')
        self.format_timestamp.return_value = '2018-04-26 13:43:01'
        self.sum_cpu_resources = mocker.patch("commands.experiment.view.sum_cpu_resources")
        self.sum_cpu_resources.return_value = "100m"
        self.sum_mem_resources = mocker.patch("commands.experiment.view.sum_mem_resources")
        self.sum_mem_resources.return_value = "1Gi"


@pytest.fixture
def prepare_mocks(mocker) -> ViewMocks:
    return ViewMocks(mocker=mocker)


def test_view_experiment_success(prepare_mocks: ViewMocks):
    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name], catch_exceptions=False)

    assert prepare_mocks.get_run.call_count == 1, "Run was not retrieved"

    assert TEST_RUNS[0].name in result.output, "Bad output."
    assert TEST_RUNS[0].submitter in result.output, "Bad output."
    assert "2018-04-26 13:43:01" in result.output, result.output
    assert "100m" in result.output, "Bad output"
    assert "1Gi" in result.output, "Bad output"

    assert result.exit_code == 0


def test_view_experiment_cpu_resources_parse_fail(prepare_mocks: ViewMocks):
    prepare_mocks.sum_cpu_resources.side_effect = ValueError("error")

    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name], catch_exceptions=False)

    assert Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(error_msg="error") in result.output, "Bad output"

    assert result.exit_code == 1


def test_view_experiment_mem_resources_parse_fail(prepare_mocks: ViewMocks):
    prepare_mocks.sum_mem_resources.side_effect = ValueError("error")

    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name], catch_exceptions=False)

    assert Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(error_msg="error") in result.output, "Bad output"

    assert result.exit_code == 1


def test_view_experiments_not_found(prepare_mocks: ViewMocks):
    prepare_mocks.get_run.return_value = None
    runner = CliRunner()
    result = runner.invoke(view.view, ["missing"])

    assert prepare_mocks.get_run.call_count == 1, "Run retrieval was not called"
    assert result.exit_code == 2
    assert Texts.EXPERIMENT_NOT_FOUND_ERROR_MSG.format(experiment_name="missing") in result.output, "Bad output."


def test_view_experiments_no_argument(prepare_mocks: ViewMocks):
    runner = CliRunner()
    result = runner.invoke(view.view, [])  # missing argument

    assert prepare_mocks.get_run.call_count == 0, "Experiments retrieval was not called"
    assert "Usage:" in result.output, "Bad output."


def test_view_experiment_failure(prepare_mocks: ViewMocks):
    prepare_mocks.get_run.side_effect = RuntimeError
    runner = CliRunner()
    result = runner.invoke(view.view, ["missing"])

    assert prepare_mocks.get_run.call_count == 1, "Experiments retrieval was not called"
    assert result.exit_code == 1


def test_view_experiment_no_pods(prepare_mocks: ViewMocks):
    prepare_mocks.get_pods.return_value = []
    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name])

    assert prepare_mocks.get_run.call_count == 1, "Experiments were not retrieved"
    assert result.output.count("\n") == 17, "Bad output."


def test_container_volume_mounts_to_msg():
    volume_mount = MagicMock()
    volume_mount.name = 'mount_name'
    volume_mount.mount_path = 'mount_path'
    volume_mounts = [volume_mount]

    msg = view.container_volume_mounts_to_msg(volume_mounts=volume_mounts)

    assert f'{volume_mount.name} @ {volume_mount.mount_path}' in msg


def test_container_resources_to_msg():
    resources = MagicMock()
    resources.requests = {'cpu': 1.0, 'mem': '1Gi'}
    resources.limits = {'cpu': 4.0, 'mem': '2gi'}

    msg = view.container_resources_to_msg(resources=resources)

    assert Texts.CONTAINER_REQUESTS_LIST_HEADER.format("") in msg
    assert f'cpu: {resources.requests["cpu"]}' in msg
    assert f'mem: {resources.requests["mem"]}B' in msg

    assert '- Limits:' in msg
    assert f'cpu: {resources.limits["cpu"]}' in msg
    assert f'mem: {resources.limits["mem"]}' in msg


def test_sum_cpu_resources_empty_list():
    cpu_resources = []
    expected_result = "0m"

    result = view.sum_cpu_resources(cpu_resources)

    assert result == expected_result


def test_sum_cpu_resources_example_list():
    cpu_resources = ["30m", "40m", "700m"]
    expected_result = "770m"

    result = view.sum_cpu_resources(cpu_resources)

    assert result == expected_result


def test_sum_cpu_resources_example_list_with_none():
    cpu_resources = ["30m", "40m", "700m", None, "700m", "33m"]
    expected_result = "1503m"

    result = view.sum_cpu_resources(cpu_resources)

    assert result == expected_result


def test_sum_cpu_resources_example_list_with_mixed():
    cpu_resources = ["30m", "40m", "700m", None, "700m", "33m", "1", "2.5"]
    expected_result = "5003m"

    result = view.sum_cpu_resources(cpu_resources)

    assert result == expected_result


def test_sum_mem_resources_empty_list():
    mem_resources = []
    expected_result = "0KiB"

    result = view.sum_mem_resources(mem_resources)

    assert result == expected_result


def test_sum_mem_resources_example_list():
    mem_resources = ["10Gi", "34Mi", "50Mi", "950Mi", "50Ki", "60Ei"]
    expected_result = "60EiB 11GiB 10MiB 50KiB"

    result = view.sum_mem_resources(mem_resources)

    assert result == expected_result


def test_sum_mem_resources_example_with_none():
    mem_resources = [None, "10Gi", "34Mi", None, "50Mi", "950Mi", None, "50Ki", "60Ei"]
    expected_result = "60EiB 11GiB 10MiB 50KiB"

    result = view.sum_mem_resources(mem_resources)

    assert result == expected_result


def test_sum_mem_resources_example_with_mixed():
    mem_resources = ["50Ki", "1000K", "1024", "1000000", "52Ki"]
    expected_result = "2MiB 8KiB"

    result = view.sum_mem_resources(mem_resources)

    assert result == expected_result


def test_displaying_pending_pod(prepare_mocks: ViewMocks, mocker):
    prepare_mocks.get_pods.return_value = PENDING_POD

    highest_usage_mock = mocker.patch("commands.experiment.view.get_highest_usage")
    highest_usage_mock.return_value = TOP_USERS, TOP_USERS

    pod_events_mock = mocker.patch("commands.experiment.view.get_pod_events")
    pod_events_mock.return_value = EVENTS
    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name], catch_exceptions=False)

    assert "Experiment is in PENDING status due to insuffcient amount of memory." in result.output
    assert "Top CPU consumers: user_name" in result.output
    assert "Top memory consumers: user_name" in result.output
