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
from kubernetes.client import V1Pod

from commands.experiment import view
from platform_resources.run_model import Run, RunStatus

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

TEST_PODS = [MagicMock(spec=V1Pod)]


class ViewMocks:
    def __init__(self, mocker):
        self.get_run = mocker.patch('commands.experiment.view.runs_api.get_run')
        self.get_run.return_value = TEST_RUNS[0]
        self.get_pods = mocker.patch('commands.experiment.view.get_pods')
        self.get_pods.return_value = TEST_PODS
        self.get_namespace = mocker.patch('commands.experiment.view.get_kubectl_current_context_namespace')


@pytest.fixture
def prepare_mocks(mocker) -> ViewMocks:
    return ViewMocks(mocker=mocker)


def test_view_experiment_success(prepare_mocks: ViewMocks):
    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_RUNS[0].name], catch_exceptions=False)

    assert prepare_mocks.get_run.call_count == 1, "Run was not retrieved"

    assert TEST_RUNS[0].name in result.output, "Bad output."
    assert TEST_RUNS[0].submitter in result.output, "Bad output."
    assert TEST_RUNS[0].creation_timestamp in result.output, "Bad output."

    assert result.exit_code == 0


def test_view_experiments_not_found(prepare_mocks: ViewMocks):
    prepare_mocks.get_run.return_value = None
    runner = CliRunner()
    result = runner.invoke(view.view, ["missing"])

    assert prepare_mocks.get_run.call_count == 1, "Run retrieval was not called"
    assert result.exit_code == 2
    assert "Experiment \"missing\" not found" in result.output, "Bad output."


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
    assert "At this moment there are no pods connected with this experiment." in result.output, "Bad output."


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

    assert '- Requests:' in msg
    assert f'cpu: {resources.requests["cpu"]}' in msg
    assert f'mem: {resources.requests["mem"]}' in msg

    assert '- Limits:' in msg
    assert f'cpu: {resources.limits["cpu"]}' in msg
    assert f'mem: {resources.limits["mem"]}' in msg
