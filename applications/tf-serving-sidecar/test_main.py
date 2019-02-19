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

from kubernetes.client import V1Job, V1JobStatus
from pytest import fixture, raises

from main import main


@fixture
def main_mock(mocker):
    mocker.patch('os.path.isfile').return_value = False
    kubernetes_config_load = mocker.patch('kubernetes.config.load_incluster_config')
    mocker.patch('main.getenv').return_value = "fake_job_name"
    file_mock = mocker.MagicMock(read=lambda: 'fake-namespace')
    open_mock = mocker.MagicMock(__enter__=lambda x: file_mock)
    builtins_open = mocker.patch('builtins.open')
    builtins_open.return_value = open_mock
    main_sleep = mocker.patch('main.sleep')

    fake_k8s_client = mocker.MagicMock()
    mocker.patch('kubernetes.client.BatchV1Api').return_value = fake_k8s_client
    mocker.patch.object(fake_k8s_client, 'read_namespaced_job').return_value = V1Job(
        status=V1JobStatus(active=0, succeeded=1))

    class MainMock:
        kubernetes_config_load_mock = kubernetes_config_load
        builtins_open_mock = builtins_open
        kubernetes_client_mock = fake_k8s_client
        time_sleep_mock = main_sleep

    return MainMock


def test_main(mocker, main_mock):
    job_status_history = [
        V1Job(status=V1JobStatus(active=1, succeeded=1)),
        V1Job(status=V1JobStatus(active=1, succeeded=1)),
        V1Job(status=V1JobStatus(active=0, succeeded=2))
    ]

    mocker.patch.object(main_mock.kubernetes_client_mock, 'read_namespaced_job').side_effect = job_status_history

    main()

    assert main_mock.kubernetes_config_load_mock.call_count == 1
    assert main_mock.builtins_open_mock.call_count == 2
    assert main_mock.time_sleep_mock.call_count == len(job_status_history) - 1


def test_main_failed_pods(mocker, main_mock):
    job_status_history = [
        V1Job(status=V1JobStatus(active=1, succeeded=1)),
        V1Job(status=V1JobStatus(active=1, succeeded=1)),
        V1Job(status=V1JobStatus(active=0, succeeded=1, failed=1))
    ]

    mocker.patch.object(main_mock.kubernetes_client_mock, 'read_namespaced_job').side_effect = job_status_history

    main()

    assert main_mock.kubernetes_config_load_mock.call_count == 1
    assert main_mock.builtins_open_mock.call_count == 2
    assert main_mock.time_sleep_mock.call_count == len(job_status_history) - 1


def test_main_end_hook_already_created(mocker, main_mock):
    mocker.patch('os.path.isfile').return_value = True

    main()

    assert main_mock.kubernetes_config_load_mock.call_count == 0
    assert main_mock.builtins_open_mock.call_count == 0


# noinspection PyUnusedLocal
def test_main_missing_batch_wrapper_job_name(mocker, main_mock):
    mocker.patch('main.getenv').return_value = None

    with raises(RuntimeError):
        main()


def test_main_missing_current_namespace(mocker, main_mock):
    file_mock = mocker.MagicMock(read=lambda: '')
    open_mock = mocker.MagicMock(__enter__=lambda x: file_mock)
    builtins_open = mocker.patch('builtins.open')
    builtins_open.return_value = open_mock

    with raises(RuntimeError):
        main()
