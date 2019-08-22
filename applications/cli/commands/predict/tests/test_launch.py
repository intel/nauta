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
from unittest.mock import MagicMock
from kubernetes.client import V1Pod, V1PodStatus, V1ContainerStatus

from commands.predict import launch


mocked_test_pod = MagicMock(spec=V1Pod)
mocked_test_pod.status = V1PodStatus(container_statuses=[V1ContainerStatus(ready=True, image="image",
                                                                           image_id="image_id", name="name",
                                                                           restart_count=0)], phase='Running')
TEST_PODS = [mocked_test_pod]


class LaunchPredictMocks:
    def __init__(self, mocker):
        self.generate_name_mock = mocker.patch('commands.predict.launch.generate_name')
        self.start_inference_instance_mock = mocker.patch('commands.predict.launch.start_inference_instance')
        self.get_inference_instance_url_mock = mocker.patch('commands.predict.launch.get_inference_instance_url')
        self.get_authorization_header_mock = mocker.patch('commands.predict.launch.get_authorization_header')
        self.get_namespace_mock = mocker.patch('commands.predict.launch.get_kubectl_current_context_namespace')
        self.validate_local_model_location = mocker.patch(
            'commands.predict.launch.validate_local_model_location')
        self.get_namespaced_pods = mocker.patch('commands.predict.launch.get_namespaced_pods')
        self.get_namespaced_pods.return_value = TEST_PODS


@pytest.fixture
def launch_mocks(mocker):
    mocks = LaunchPredictMocks(mocker=mocker)
    return mocks


def test_launch(launch_mocks: LaunchPredictMocks):
    model_location = '/fake/model/location'
    name = 'fake-model-name'

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--model-location', model_location, '--name', name])

    assert launch_mocks.generate_name_mock.call_count == 0
    assert launch_mocks.start_inference_instance_mock.call_count == 1
    assert launch_mocks.get_namespace_mock.call_count == 1
    assert launch_mocks.get_inference_instance_url_mock.call_count == 1
    assert launch_mocks.get_authorization_header_mock.call_count == 1
    assert result.exit_code == 0


def test_launch_generate_name(launch_mocks: LaunchPredictMocks):
    model_location = '/fake/model/location'

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--model-location', model_location])

    assert launch_mocks.generate_name_mock.call_count == 1
    assert launch_mocks.start_inference_instance_mock.call_count == 1
    assert launch_mocks.get_namespace_mock.call_count == 1
    assert launch_mocks.get_inference_instance_url_mock.call_count == 1
    assert launch_mocks.get_authorization_header_mock.call_count == 1
    assert result.exit_code == 0


def test_launch_fail(launch_mocks: LaunchPredictMocks):
    launch_mocks.start_inference_instance_mock.side_effect = RuntimeError

    model_location = '/fake/model/location'

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--model-location', model_location])

    assert launch_mocks.generate_name_mock.call_count == 1
    assert launch_mocks.start_inference_instance_mock.call_count == 1
    assert launch_mocks.get_namespace_mock.call_count == 0
    assert launch_mocks.get_inference_instance_url_mock.call_count == 0
    assert launch_mocks.get_authorization_header_mock.call_count == 0
    assert result.exit_code == 1


def test_launch_pod_fail(launch_mocks: LaunchPredictMocks):
    failed_pod_mock = MagicMock(spec=V1Pod)
    failed_pod_mock.status = V1PodStatus(container_statuses=[V1ContainerStatus(ready=True, image="image",
                                                                               image_id="image_id", name="name",
                                                                               restart_count=0)], phase='Failed')
    launch_mocks.get_namespaced_pods.return_value = [failed_pod_mock]

    model_location = '/fake/model/location'

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--model-location', model_location])

    assert launch_mocks.generate_name_mock.call_count == 1
    assert launch_mocks.start_inference_instance_mock.call_count == 1
    assert launch_mocks.get_namespace_mock.call_count == 1
    assert launch_mocks.get_inference_instance_url_mock.call_count == 1
    assert launch_mocks.get_authorization_header_mock.call_count == 1
    assert launch_mocks.get_namespaced_pods.call_count == 1
    assert result.exit_code == 1


def test_launch_url_fail(launch_mocks: LaunchPredictMocks):
    launch_mocks.get_inference_instance_url_mock.side_effect = RuntimeError

    model_location = '/fake/model/location'

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--model-location', model_location])

    assert launch_mocks.get_authorization_header_mock.call_count == 1
    assert result.exit_code == 1


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_batch_missing_model_location(launch_mocks):
    runner = CliRunner()
    result = runner.invoke(launch.launch, [])

    assert launch_mocks.generate_name_mock.call_count == 0
    assert launch_mocks.start_inference_instance_mock.call_count == 0
    assert launch_mocks.get_namespace_mock.call_count == 0
    assert launch_mocks.get_inference_instance_url_mock.call_count == 0
    assert launch_mocks.get_authorization_header_mock.call_count == 0

    assert result.exit_code == 1


def test_missing_file(mocker, launch_mocks):
    local_model_location = '/non_existing_path'
    mocker.patch.object(launch, 'validate_local_model_location').side_effect = SystemExit(2)

    runner = CliRunner()
    result = runner.invoke(launch.launch, ['--local-model-location', local_model_location])

    assert launch_mocks.generate_name_mock.call_count == 0
    assert launch_mocks.start_inference_instance_mock.call_count == 0
    assert launch_mocks.get_namespace_mock.call_count == 0
    assert launch_mocks.get_inference_instance_url_mock.call_count == 0
    assert launch_mocks.get_authorization_header_mock.call_count == 0

    assert result.exit_code == 2


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_validate_local_model_location(mocker):

    mocker.patch('os.path.isdir', return_value=False)

    with pytest.raises(SystemExit):
        launch.validate_local_model_location('/bla')
