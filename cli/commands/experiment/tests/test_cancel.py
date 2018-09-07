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
from unittest.mock import DEFAULT

from platform_resources.run_model import Run, RunStatus
from commands.experiment import cancel
from commands.experiment.cancel import experiment_name, experiment_name_plural
from platform_resources.tests.test_experiments import TEST_EXPERIMENTS
from util.k8s.pods import K8SPod
from util.k8s.k8s_info import PodStatus

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
    assert prepare_mocks.get_experiment.call_count == gex_count, "experiment data wasn't gathered"


def test_cancel_lack_of_experiments(prepare_command_mocks: CancelMocks):
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME])

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert f"Lack of {experiment_name_plural} fulfilling given criteria." \
           f" Name or match string parameters do not match any existing {experiment_name}." \
           f" Run 'dlsctl exp list' to find out what are the names of existing {experiment_name_plural}." \
           in result.output


def test_cancel_all_exp_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CANCELLED
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME])

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert f"{experiment_name_plural} fulfilling given criteria have been cancelled already." in result.output


def test_cancel_some_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_MIXED
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert f"The following {experiment_name_plural} have been cancelled already:" in result.output
    assert f"The following {experiment_name_plural} can still be cancelled:" in result.output


def test_cancel_none_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert f"The following {experiment_name_plural} will be cancelled:" in result.output


def test_cancel_user_break(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="n")

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)
    assert f"Operation of cancellation of {experiment_name_plural} was aborted." in result.output


def test_cancel_all_cancelled_successfully(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT

    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")
    check_command_asserts(prepare_command_mocks, cne_count=2, lkc_count=1, acl_count=1)

    assert f"The following {experiment_name_plural} were cancelled successfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_some_not_cancelled(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_command_mocks.cancel_experiment.side_effect = ([([RUN_COMPLETE], []), ([], [RUN_QUEUED])])
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")

    check_command_asserts(prepare_command_mocks, cne_count=2, lkc_count=1, acl_count=1)

    assert f"The following {experiment_name_plural} were cancelled successfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert f"The following {experiment_name_plural} weren't cancelled properly:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_list_of_runs_failure(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.side_effect = RuntimeError()
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")
    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0)

    assert f"Problems during loading a list of {experiment_name_plural}." in result.output


def test_exception_during_exp_cancellation(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_command_mocks.cancel_experiment.side_effect = [([RUN_COMPLETE], []), RuntimeError()]
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME], input="y")

    check_command_asserts(prepare_command_mocks, cne_count=2)
    assert f"The following {experiment_name_plural} were cancelled successfully:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-1-tf-training" in result.output
    assert f"The following {experiment_name_plural} weren't cancelled properly:" in result.output
    assert "exp-mnist-single-node.py-18.05.17-16.05.45-2-tf-training" in result.output


def test_cancel_missing_parameters(prepare_command_mocks: CancelMocks):
    result = CliRunner().invoke(cancel.cancel)
    check_command_asserts(prepare_command_mocks, gcn_count=0, lor_count=0, cne_count=0, lkc_count=0,
                          acl_count=0, gex_count=0)

    assert "Name, -m or at least one of [--pod-ids, --pod-status] option must be given. Please pass one of them." \
           in result.output


def test_cancel_too_many_parameters(prepare_command_mocks: CancelMocks):
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME, "-m", EXPERIMENT_NAME])
    check_command_asserts(prepare_command_mocks, gcn_count=0, lor_count=0, cne_count=0, lkc_count=0,
                          acl_count=0, gex_count=0)

    assert "Both name and -m option cannot be given. Please choose one of them." in result.output


def test_cancel_all_exp_cancelled_m_option(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CANCELLED
    result = CliRunner().invoke(cancel.cancel, ["-m", EXPERIMENT_NAME])

    check_command_asserts(prepare_command_mocks, cne_count=0, lkc_count=0, acl_count=0, gex_count=0)
    assert f"{experiment_name_plural} fulfilling given criteria have been cancelled already." in result.output


class CancelExperimentMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.list_runs = mocker.patch("commands.experiment.cancel.list_runs", return_value=[])
        self.update_experiment = mocker.patch("commands.experiment.cancel.update_experiment")
        self.update_run = mocker.patch("commands.experiment.cancel.update_run")
        self.delete_k8s_object = mocker.patch("commands.experiment.cancel.kubectl.delete_k8s_object")
        self.delete_helm_release = mocker.patch("commands.experiment.cancel.delete_helm_release")
        self.get_experiment = mocker.patch("commands.experiment.cancel.get_experiment",
                                           return_value=None)
        self.k8s_es_client = mocker.patch('commands.experiment.cancel.K8sElasticSearchClient')
        self.delete_images_for_experiment = mocker.patch('commands.experiment.cancel.'
                                                         'delete_images_for_experiment')


@pytest.fixture
def prepare_cancel_experiment_mocks(mocker) -> CancelExperimentMocks:
    mocks = CancelExperimentMocks(mocker=mocker)
    return mocks


def check_cancel_experiment_asserts(prepare_cancel_experiment_mocks: CancelExperimentMocks,
                                    list_runs_count=1,
                                    update_experiment_count=1,
                                    delete_k8s_object_count=0,
                                    delete_helm_release_count=1,
                                    update_run_count=1,
                                    get_experiment_count=1,
                                    delete_images_for_experiment_count=0):
    assert prepare_cancel_experiment_mocks.list_runs.call_count == list_runs_count, \
        "list of runs wasn't taken"
    assert prepare_cancel_experiment_mocks.update_experiment.call_count == update_experiment_count, \
        "experiment wasn't updated"
    assert prepare_cancel_experiment_mocks.delete_k8s_object.call_count == delete_k8s_object_count, \
        "experiment object wasn't deleted"
    assert prepare_cancel_experiment_mocks.delete_helm_release.call_count == delete_helm_release_count, \
        "helm release wasn't deleted"
    assert prepare_cancel_experiment_mocks.update_run.call_count == update_run_count, \
        "run wasn't updated"
    assert prepare_cancel_experiment_mocks.get_experiment.call_count == get_experiment_count, \
        "experiment wasn't taken"
    assert prepare_cancel_experiment_mocks.delete_images_for_experiment.call_count == \
        delete_images_for_experiment_count, "incorrect number of calls of deleting images"


def test_cancel_experiment_set_cancelling_state_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks, caplog):
    import logging
    caplog.set_level(logging.CRITICAL)
    prepare_cancel_experiment_mocks.update_experiment.side_effect = RuntimeError()
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    with pytest.raises(RuntimeError):
        cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED], namespace="namespace")
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_helm_release_count=0, update_run_count=0)


def test_cancel_experiment_success(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED], namespace="namespace")
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, update_experiment_count=2)


def test_cancel_experiment_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.delete_helm_release.side_effect = RuntimeError()
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    del_list, not_del_list = cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=[RUN_QUEUED],
                                                      namespace="namespace")

    assert len(del_list) == 0
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, update_run_count=0)


def test_cancel_experiment_success_with_purge(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.mocker.patch('commands.experiment.cancel.cancel_experiment_runs').return_value \
        = [RUN_QUEUED], []
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    cancel.purge_experiment(exp_name="experiment-1", runs_to_purge=[RUN_QUEUED], namespace="namespace",
                            k8s_es_client=prepare_cancel_experiment_mocks.k8s_es_client)
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_helm_release_count=1, update_run_count=0,
                                    delete_images_for_experiment_count=1, delete_k8s_object_count=2)


def test_cancel_experiment_purge_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.mocker.patch('commands.experiment.cancel.cancel_experiment_runs').return_value \
        = [RUN_QUEUED], []
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.delete_helm_release.side_effect = [RuntimeError]

    del_list, not_del_list = cancel.purge_experiment(exp_name="experiment-1", runs_to_purge=[RUN_QUEUED],
                                                     namespace="namespace",
                                                     k8s_es_client=prepare_cancel_experiment_mocks.k8s_es_client)

    assert len(del_list) == 0
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_helm_release_count=1, update_run_count=0)


def test_cancel_experiment_with_purge_delete_failure(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.mocker.patch('commands.experiment.cancel.cancel_experiment_runs').return_value \
        = [RUN_QUEUED], []
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]
    prepare_cancel_experiment_mocks.list_runs.return_value = [RUN_QUEUED]
    prepare_cancel_experiment_mocks.delete_images_for_experiment.side_effect = RuntimeError()
    cancel.purge_experiment(exp_name="experiment-1", runs_to_purge=[RUN_QUEUED], namespace="namespace",
                            k8s_es_client=prepare_cancel_experiment_mocks.k8s_es_client)
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_helm_release_count=1, update_run_count=0,
                                    delete_k8s_object_count=2, delete_images_for_experiment_count=1)


def test_cancel_experiment_one_cancelled_one_not(prepare_cancel_experiment_mocks: CancelExperimentMocks):
    prepare_cancel_experiment_mocks.delete_helm_release.side_effect = [DEFAULT, RuntimeError(), DEFAULT, DEFAULT]
    prepare_cancel_experiment_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    prepare_cancel_experiment_mocks.get_experiment.return_value = TEST_EXPERIMENTS[0]

    del_list, not_del_list = cancel.cancel_experiment(exp_name="experiment-1", runs_to_cancel=TEST_RUNS_CORRECT,
                                                      namespace="namespace")

    assert len(del_list) == 1
    assert len(not_del_list) == 1
    check_cancel_experiment_asserts(prepare_cancel_experiment_mocks, delete_helm_release_count=2)


def test_cancel_match_and_name(prepare_command_mocks: CancelMocks):
    prepare_command_mocks.list_runs.return_value = TEST_RUNS_CORRECT
    result = CliRunner().invoke(cancel.cancel, [EXPERIMENT_NAME, "-m", EXPERIMENT_NAME])

    assert "Both name and -m option cannot be given. Please choose one of them." in result.output


def test_cancel_pods(mocker):
    fake_user_namespace_name = 'shawn'
    fake_k8s_pods = [
        K8SPod(
            namespace=fake_user_namespace_name,
            name='podid1',
            status=PodStatus.RUNNING,
            labels={
                'runName': 'fake-name'
            }
        )
    ]
    mocker.patch.object(cancel, 'k8s_pods').list_pods.return_value = fake_k8s_pods
    for fake_pod in fake_k8s_pods:
        mocker.patch.object(fake_pod, 'delete')

    mocker.patch.object(cancel.click, 'confirm')

    cancel.cancel_pods_mode(fake_user_namespace_name, 'fake-name', 'podid1,podid2', pod_status='running')

    assert fake_k8s_pods[0].delete.call_count == 1
