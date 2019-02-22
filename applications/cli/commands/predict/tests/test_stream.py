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

from commands.predict import stream
from commands.predict.common import InferenceVerb
from platform_resources.run import RunStatus
from cli_text_consts import PredictStreamCmdTexts as Texts


TEST_DATA = '{"instances": [1.0, 2.0, 5.0]}'
TEST_RESPONSE = '{"predictions": [3.5, 4.0, 5.5]}'
TEST_URL = 'https://nauta.com:8443/api/v1/namespaces/test/services/inf/proxy/v1/models/saved_model_half_plus_three'
TEST_API_KEY = 'Bearer blablebla'


class StreamPredictMocks:
    def __init__(self, mocker):
        self.get_namespace_mock = mocker.patch('commands.predict.stream.get_kubectl_current_context_namespace')
        self.get_run_mock = mocker.patch('commands.predict.stream.Run.get')
        self.get_run_mock.return_value.state = RunStatus.RUNNING
        self.get_inference_instance_url_mock = mocker.patch('commands.predict.stream.get_inference_instance_url')
        self.get_inference_instance_url_mock.return_value = TEST_URL
        self.get_api_key_mock = mocker.patch('commands.predict.stream.get_api_key')
        self.get_api_key_mock.return_value = TEST_API_KEY
        self.inference_post_mock = mocker.patch('commands.predict.stream.requests.post')
        self.inference_post_mock.return_value.text = TEST_RESPONSE


@pytest.fixture
def stream_mocks(mocker):
    mocks = StreamPredictMocks(mocker=mocker)
    return mocks


def test_stream(stream_mocks: StreamPredictMocks):
    data_location = 'data.json'
    name = 'fake-inference-instance'
    verb = InferenceVerb.CLASSIFY.value

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write(TEST_DATA)
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name, '--method-verb', verb],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 1
    assert stream_mocks.get_api_key_mock.call_count == 1

    stream_mocks.inference_post_mock.assert_called_with(f'{TEST_URL}:{verb}', data=TEST_DATA, verify=False,
                                                        headers={'Authorization': TEST_API_KEY,
                                                                 'Accept': 'application/json',
                                                                 'Content-Type': 'application/json'})

    assert TEST_RESPONSE in result.output
    assert result.exit_code == 0


def test_stream_get_run_fail(stream_mocks: StreamPredictMocks):
    stream_mocks.get_run_mock.return_value = None

    data_location = 'data.json'
    name = 'fake-inference-instance'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write(TEST_DATA)
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 0
    assert stream_mocks.get_api_key_mock.call_count == 0

    assert Texts.INSTANCE_NOT_EXISTS_ERROR_MSG.format(name=name) in result.output
    assert result.exit_code == 1


def test_stream_instance_not_running_fail(stream_mocks: StreamPredictMocks):
    stream_mocks.get_run_mock.return_value.state = RunStatus.QUEUED

    data_location = 'data.json'
    name = 'fake-inference-instance'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write(TEST_DATA)
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 0
    assert stream_mocks.get_api_key_mock.call_count == 0

    assert Texts.INSTANCE_NOT_RUNNING_ERROR_MSG.format(name=name, running_code=RunStatus.RUNNING.value) \
        in result.output
    assert result.exit_code == 1


def test_stream_get_run_url_fail(stream_mocks: StreamPredictMocks):
    stream_mocks.get_inference_instance_url_mock.side_effect = RuntimeError

    data_location = 'data.json'
    name = 'fake-inference-instance'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write(TEST_DATA)
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 1
    assert stream_mocks.get_api_key_mock.call_count == 0

    assert Texts.INSTANCE_GET_FAIL_ERROR_MSG.format(name=name) in result.output
    assert result.exit_code == 1


def test_stream_data_load_fail(stream_mocks: StreamPredictMocks):
    data_location = 'data.json'
    name = 'fake-inference-instance'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write('')
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 1
    assert stream_mocks.get_api_key_mock.call_count == 0

    assert Texts.JSON_LOAD_ERROR_MSG.format(data=data_location) in result.output
    assert result.exit_code == 1


def test_stream_inference_fail(stream_mocks: StreamPredictMocks):
    request_error = '403'
    stream_mocks.inference_post_mock.return_value.raise_for_status.side_effect = RuntimeError(request_error)
    data_location = 'data.json'
    name = 'fake-inference-instance'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(data_location, 'w') as data_file:
            data_file.write(TEST_DATA)
        result = runner.invoke(stream.stream, ['--data', data_location, '--name', name],
                               catch_exceptions=False)

    assert stream_mocks.get_namespace_mock.call_count == 1
    assert stream_mocks.get_run_mock.call_count == 1
    assert stream_mocks.get_inference_instance_url_mock.call_count == 1
    assert stream_mocks.get_api_key_mock.call_count == 1

    assert Texts.INFERENCE_OTHER_ERROR_MSG.format(exception=request_error) in result.output
    assert result.exit_code == 1
