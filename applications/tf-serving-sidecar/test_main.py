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
