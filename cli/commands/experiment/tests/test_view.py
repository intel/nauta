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

from commands.experiment import view
from platform_resources.experiment_model import Experiment, ExperimentStatus

TEST_EXPERIMENTS = [
    Experiment(
        name='test-experiment',
        parameters_spec=['a 1', 'b 2'],
        creation_timestamp='2018-04-26T13:43:01Z',
        submitter='namespace-1',
        state=ExperimentStatus.CREATING,
        template_name='test-ex-template',
        template_namespace='test-ex-namespace'),
    Experiment(
        name='test-experiment-2',
        parameters_spec=['a 1', 'b 2'],
        creation_timestamp='2018-05-08T13:05:04Z',
        submitter='namespace-2',
        state=ExperimentStatus.SUBMITTED,
        template_name='test-ex-template',
        template_namespace='test-ex-namespace')
]


class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a,
                        [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)


pod_list = {
    "items": [{
        "metadata": {
            "name": "mocked_name",
            "uid": "mocked_uid"
        },
        "spec": {
            "containers": []
        },
        "status": {
            "conditions": [],
            "container_statuses": []
        }
    }]
}


class KubernetesClientListPodsMock():
    def list_pod_for_all_namespaces(*args, **kwargs):
        return obj(pod_list)


def test_view_experiment_success(mocker):
    api_list_experiments_mock = mocker.patch(
        "commands.experiment.view.experiments_api.list_experiments")
    api_list_experiments_mock.return_value = TEST_EXPERIMENTS

    mocker.patch(
        "commands.experiment.view.get_kubectl_current_context_namespace")

    kubernetes_client_mock = mocker.patch("kubernetes.client.CoreV1Api")
    kubernetes_client_mock.return_value = KubernetesClientListPodsMock()

    kubernetes_config_mock = mocker.patch("kubernetes.config.load_kube_config")
    kubernetes_config_mock.return_value = None

    runner = CliRunner()
    result = runner.invoke(view.view, [TEST_EXPERIMENTS[0].name])

    assert api_list_experiments_mock.call_count == 1, "Experiments were not retrieved"
    assert kubernetes_client_mock.call_count == 1, "Kubernetes client not called"

    assert TEST_EXPERIMENTS[0].name in result.output, "Bad output."
    assert TEST_EXPERIMENTS[0].submitter in result.output, "Bad output."
    assert TEST_EXPERIMENTS[
        0].creation_timestamp in result.output, "Bad output."

    assert result.exit_code == 0


def test_view_experiments_not_found(mocker):
    api_list_experiments_mock = mocker.patch(
        "commands.experiment.view.experiments_api.list_experiments")
    api_list_experiments_mock.return_value = []

    sys_exit_mock = mocker.patch("sys.exit")

    mocker.patch(
        "commands.experiment.view.get_kubectl_current_context_namespace")

    kubernetes_client_mock = mocker.patch("kubernetes.client.CoreV1Api")
    kubernetes_client_mock.return_value = KubernetesClientListPodsMock()

    kubernetes_config_mock = mocker.patch("kubernetes.config.load_kube_config")
    kubernetes_config_mock.return_value = None

    runner = CliRunner()
    result = runner.invoke(view.view, ["missing"])

    assert api_list_experiments_mock.call_count == 1, "Experiments retrieval was not called"
    assert sys_exit_mock.called_once_with(1)
    assert "Experiment not found" in result.output, "Bad output."
    assert result.exit_code == 0


def test_view_experiments_no_argument(mocker):
    api_list_experiments_mock = mocker.patch(
        "commands.experiment.view.experiments_api.list_experiments")
    api_list_experiments_mock.return_value = []

    mocker.patch(
        "commands.experiment.view.get_kubectl_current_context_namespace")

    kubernetes_client_mock = mocker.patch("kubernetes.client.CoreV1Api")
    kubernetes_client_mock.return_value = KubernetesClientListPodsMock()

    kubernetes_config_mock = mocker.patch("kubernetes.config.load_kube_config")
    kubernetes_config_mock.return_value = None

    runner = CliRunner()
    result = runner.invoke(view.view, [])  # missing argument

    assert api_list_experiments_mock.call_count == 0, "Experiments retrieval was not called"
    assert "Usage:" in result.output, "Bad output."


def test_view_experiment_failure(mocker):
    api_list_experiments_mock = mocker.patch(
        "commands.experiment.view.experiments_api.list_experiments")
    api_list_experiments_mock.side_effect = RuntimeError

    mocker.patch(
        "commands.experiment.view.get_kubectl_current_context_namespace")

    sys_exit_mock = mocker.patch("sys.exit")

    runner = CliRunner()
    runner.invoke(view.view, ["missing"])

    assert api_list_experiments_mock.call_count == 1, "Experiments retrieval was not called"
    assert sys_exit_mock.called_once_with(1)
