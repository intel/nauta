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
from kubernetes.client.models import V1PodList, V1Pod, V1ObjectMeta, V1OwnerReference, V1DeploymentList, V1Deployment, \
    V1ServiceList, V1Service
import pytest
from unittest.mock import DEFAULT

from platform_resources.run_model import Run, RunStatus
from commands.experiment import cancel
from platform_resources.tests.test_experiments import TEST_EXPERIMENTS

EXPERIMENT_NAME = "experiment"

RUN_QUEUED = Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                 parameters=['mnist_single_node.py', '--data_dir', '/app'],
                 state=RunStatus.QUEUED,
                 metrics={'accuracy': 52.322},
                 experiment_name="experiment-1",
                 pod_count=1,
                 pod_selector={'matchLabels': {'app': 'tf-training',
                                               'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                                               'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'}},
                 submitter="mciesiel-dev", creation_timestamp="2018-05-17T14:05:52Z",
                 template_name="tf-training")
RUN_CANCELLED = Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training",
                    parameters=['mnist_single_node.py', '--data_dir', '/app'],
                    state=RunStatus.CANCELLED,
                    metrics={'accuracy': 52.322},
                    experiment_name="experiment-name-will-be-added-soon",
                    pod_count=1,
                    pod_selector={'matchLabels': {'app': 'tf-training',
                                                  'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                                                  'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'}},
                    submitter="mciesiel-dev", creation_timestamp="2018-05-17T14:05:52Z",
                    template_name="tf-training")
RUN_COMPLETE = Run(name="exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training",
                   parameters=['mnist_single_node.py', '--data_dir', '/app'],
                   state=RunStatus.COMPLETE,
                   metrics={'accuracy': 52.322},
                   experiment_name="experiment-2",
                   pod_count=1,
                   pod_selector={'matchLabels': {'app': 'tf-training',
                                                 'draft': 'exp-mnist-single-node.py-18.05.17-16.05.45-1',
                                                 'release': 'exp-mnist-single-node.py-18.05.17-16.05.45-1'}},
                   submitter="mciesiel-dev", creation_timestamp="2018-05-17T14:05:52Z",
                   template_name="tf-training")

TEST_RUNS_CORRECT = [RUN_COMPLETE, RUN_QUEUED]

TEST_RUNS_MIXED = [RUN_COMPLETE, RUN_CANCELLED]

TEST_RUNS_CANCELLED = [RUN_CANCELLED]


class CancelMocks:
    def __init__(self, mocker) -> None:
        self.mocker = mocker
        self.get_current_namespace = mocker.patch("commands.experiment.cancel.get_current_namespace",
                                                  return_value="namespace")
        self.list_runs = mocker.patch("commands.experiment.cancel.list_runs",
                                      return_value=[])
        self.cancel_experiment = mocker.patch("commands.experiment.cancel.cancel_experiment",
                                              return_value=([([RUN_COMPLETE], []), ([RUN_COMPLETE], [])]))
        self.load_kube_config = mocker.patch("kubernetes.config.load_kube_config")
        self.k8s_core_api = mocker.patch('kubernetes.client.CoreV1Api')
        self.k8s_es_client = mocker.patch('commands.experiment.cancel.K8sElasticSearchClient')
        self.k8s_proxy = mocker.patch('commands.experiment.cancel.K8sProxy')
        self.get_experiment = mocker.patch('commands.experiment.cancel.get_experiment')


@pytest.fixture
def prepare_command_mocks(mocker) -> CancelMocks:
    return CancelMocks(mocker=mocker)


def check_command_asserts(prepare_mocks: CancelMocks, gcn_count=1, lor_count=1, cne_count=1,
                          lkc_count=1, acl_count=1, gex_count=1):
    assert prepare_mocks.get_current_namespace.call_count == gcn_count, "namespace wasn't taken"
    assert prepare_mocks.list_runs.call_count == lor_count, "list of runs wasn't gathered"
    assert prepare_mocks.cancel_experiment.call_count == cne_count, "experiment wasn't cancelled"
    assert prepare_mocks.load_kube_config.call_count == lkc_count, "kube config wasn't loaded"
    assert prepare_mocks.k8s_core_api.call_count == acl_count, "kubernetes api wasn't created"
    assert prepare_mocks.get_experiment.call_count == gex_count, "experiment data wasn't gathered"


def test_cancel_lack_of_experiments(prepare_command_mocks: CancelMocks):
    CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME])
    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)


def test_cancel_all_exp_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CANCELLED
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME])

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert "Experiments fulfilling given criteria have been cancelled already." in result.output


def test_cancel_some_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_MIXED
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert "The following experiments have been cancelled already:" in result.output
    assert "The following experiments can still be cancelled:" in result.output


def test_cancel_none_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert "The following experiments will be cancelled:" in result.output


def test_cancel_user_break(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert "Operation of cancellation of experiments was aborted." in result.output


def test_cancel_all_cancelled_successfully(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT

    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")
    check_command_asserts(prepare_command_mocks, cne_count=2, lkc_count=1, acl_count=1)

    assert "The following experiments were cancelled succesfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_some_not_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_command_mocks.cancel_experiment.side_effect = ([([RUN_COMPLETE], []), ([], [RUN_QUEUED])])
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")

    check_command_asserts(prepare_command_mocks, cne_count=2, lkc_count=1, acl_count=1)

    assert "The following experiments were cancelled succesfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert "The following experiments weren't cancelled properly:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_list_of_runs_failure(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.side_effect = RuntimeError()
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")
    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)

    assert "Problems during loading a list of experiments." in result.output


def test_exception_during_exp_cancellation(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_command_mocks.cancel_experiment.side_effect = [([RUN_COMPLETE], []), RuntimeError()]
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")

    check_command_asserts(prepare_command_mocks, cne_count=2)
    assert "The following experiments were cancelled succesfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert "The following experiments weren't cancelled properly:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_missing_parameters(prepare_command_mocks: CancelMocks):
    result = CliRunner().invoke(cancel.cancel)
    check_command_asserts(prepare_command_mocks, gcn_count=0, lor_count=0, cne_count=0, lkc_count=0,
                          acl_count=0, gex_count=0)

    assert "Name or -m option must be given. Please pass one of them." in result.output


def test_cancel_too_many_parameters(prepare_command_mocks: CancelMocks):
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME, "-m", EXPERIMENT_NAME])
    check_command_asserts(prepare_command_mocks, gcn_count=0, lor_count=0, cne_count=0, lkc_count=0,
                          acl_count=0, gex_count=0)

    assert "Both name and -m option cannot be given. Please choose one of them." in result.output


def test_cancel_all_exp_cancelled_m_option(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CANCELLED
    result = CliRunner().invoke(cancel.cancel, ["-m", EXPERIMENT_NAME])

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0, gex_count=0)
    assert "Experiments fulfilling given criteria have been cancelled already." in result.output


class CancelExperimentMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.list_runs = mocker.patch("commands.experiment.cancel.list_runs",
                                      return_value=[])
        self.update_experiment = mocker.patch("commands.experiment.cancel.update_experiment")
        self.delete_k8s_object = mocker.patch("commands.experiment.cancel.kubectl.delete_k8s_object")
        self.update_run = mocker.patch("commands.experiment.cancel.update_run")
        self.k8s_core_api_client = mocker.patch('kubernetes.client.CoreV1Api')

        self.k8s_apps_api_client_instance = mocker.patch('kubernetes.client.AppsV1Api').return_value
        self.k8s_apps_api_client_instance.list_namespaced_deployment.return_value.items = []

        self.load_kube_config = mocker.patch("kubernetes.config.load_kube_config")
        self.get_experiment = mocker.patch("commands.experiment.cancel.get_experiment",
                                           return_value=None)
        self.k8s_es_client = mocker.patch('commands.experiment.cancel.K8sElasticSearchClient')


@pytest.fixture
def prepare_cancel_experiment_mocks(mocker) -> CancelExperimentMocks:
    mocks = CancelExperimentMocks(mocker=mocker)

    owner_reference = V1OwnerReference(name="test-job", kind="Job", api_version="v1", uid="1")
    object_meta = V1ObjectMeta(owner_references=[owner_reference])
    pod = V1Pod(metadata=object_meta)
    pod_list = V1PodList(items=[pod])
    mocks.k8s_core_api_client.list_namespaced_pod.return_value = pod_list

    return mocks


def check_cancel_experiment_asserts(prepare_cancel_experiment_mocks: CancelExperimentMocks,
                                    list_runs_count=1,
                                    update_experiment_count=1,
                                    delete_k8s_object_count=1,
                                    update_run_count=1,
                                    get_experiment_count=1):
    assert prepare_cancel_experiment_mocks.list_runs.call_count == list_runs_count, \
        "list of runs wasn't taken"
    assert prepare_cancel_experiment_mocks.update_experiment.call_count == update_experiment_count, \
        "experiment wasn't updated"
    assert prepare_cancel_experiment_mocks.delete_k8s_object.call_count == delete_k8s_object_count, \
        "k8s object wasn't deleted"
    assert prepare_cancel_experiment_mocks.update_run.call_count == update_run_count, \
        "run wasn't updated"
    assert prepare_cancel_experiment_mocks.get_experiment.call_count == get_experiment_count, \
        "experiment wasn't taken"


def test_cancel_experiment_set_cancelling_state_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks, caplog):
    import logging
    caplog.set_level(logging.CRITICAL)
    prepare_cancel_experiment_mocks.update_experiment.side_effect = RuntimeError()
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    with pytest.raises(RuntimeError):
        cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED], namespace="namespace",
                                 k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                                 k8s_apps_api=prepare_cancel_experiment_mocks.k8s_apps_api_client_instance)
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_k8s_object_count=0, update_run_count=0)


def test_cancel_experiment_success(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED], namespace="namespace",
                             k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                             k8s_apps_api=prepare_cancel_experiment_mocks.k8s_apps_api_client_instance)
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, update_experiment_count=2)


def test_cancel_experiment_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.delete_k8s_object.side_effect = RuntimeError()
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    del_list, not_del_list = cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED],
                                                      namespace="namespace",
                                                      k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                                                      k8s_apps_api=prepare_cancel_experiment_mocks.
                                                      k8s_apps_api_client_instance)

    assert len(del_list) == 0
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, update_run_count=0)


def test_cancel_experiment_success_with_purge(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.mocker.patch('commands.experiment.cancel.cancel_experiment_runs').return_value \
        = [RUN_QUEUED], []
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    cancel.purge_experiment(exp_name="experiment-1", runs_to_purge=[RUN_QUEUED], namespace="namespace",
                            k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                            k8s_es_client=prepare_cancel_experiment_mocks.k8s_es_client,
                            k8s_apps_api=prepare_cancel_experiment_mocks.k8s_apps_api_client_instance)
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_k8s_object_count=2, update_run_count=0)


def test_cancel_experiment_purge_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.mocker.patch('commands.experiment.cancel.cancel_experiment_runs').return_value \
        = [RUN_QUEUED], []
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.delete_k8s_object.side_effect = [RuntimeError]

    del_list, not_del_list = cancel.purge_experiment(exp_name="experiment-1", runs_to_purge=[RUN_QUEUED],
                                                     namespace="namespace",
                                                     k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                                                     k8s_es_client=prepare_cancel_experiment_mocks.k8s_es_client,
                                                     k8s_apps_api=prepare_cancel_experiment_mocks.
                                                     k8s_apps_api_client_instance)

    assert len(del_list) == 0
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_k8s_object_count=1, update_run_count=0)


def test_cancel_experiment_one_cancelled_one_not(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.delete_k8s_object.side_effect = [DEFAULT, RuntimeError(), DEFAULT, DEFAULT]
    prepare_cancel_experiment_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]

    del_list, not_del_list = cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=TEST_RUNS_CORRECT,
                                                      namespace="namespace",
                                                      k8s_api=prepare_cancel_experiment_mocks.k8s_core_api_client,
                                                      k8s_apps_api=prepare_cancel_experiment_mocks.
                                                      k8s_apps_api_client_instance)

    assert len(del_list) == 1
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_k8s_object_count=2)


def test_cancel_match_and_name(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME, "-m", EXPERIMENT_NAME])

    assert "Both name and -m option cannot be given. Please choose one of them." in result.output


def test_cancel_jupyter_notebook_experiment(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_COMPLETE]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]

    meta = V1ObjectMeta(name="Deployment")

    deployment = V1Deployment(metadata=meta)
    deploymentList = V1DeploymentList(items=[deployment])
    prepare_cancel_experiment_mocks.k8s_apps_api_client_instance.\
        list_namespaced_deployment.return_value = deploymentList

    service = V1Service(metadata=meta)
    serviceList = V1ServiceList(items=[service])
    k8s_core_api_client_instance = prepare_cancel_experiment_mocks.k8s_core_api_client.return_value
    k8s_core_api_client_instance.list_namespaced_service.return_value = serviceList

    del_list, not_del_list = cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_COMPLETE],
                                                      namespace="namespace",
                                                      k8s_api=k8s_core_api_client_instance,
                                                      k8s_apps_api=prepare_cancel_experiment_mocks.
                                                      k8s_apps_api_client_instance)

    assert len(del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_k8s_object_count=2,
                                    update_experiment_count=2)
