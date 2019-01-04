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

from commands.predict import batch
from util.exceptions import SubmitExperimentError


@pytest.fixture
def launch_mocks(mocker):
    mocker.patch.object(batch, 'generate_name')
    mocker.patch.object(batch, 'start_inference_instance')
    mocker.patch.object(batch, 'validate_local_model_location')


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_batch(launch_mocks):
    model_location = '/fake/model/location'
    data_location = '/fake/data/location'

    runner = CliRunner()
    result = runner.invoke(batch.batch, ['--model-location', model_location, '--data', data_location,
                                         '-p', 'test.param', '1'])

    assert batch.generate_name.call_count == 1
    assert batch.start_inference_instance.call_count == 1

    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_batch_name_provided(launch_mocks):
    model_location = '/fake/model/location'
    data_location = '/fake/data/location'
    fake_name = 'fake-exp-name'

    runner = CliRunner()
    result = runner.invoke(batch.batch, ['--model-location', model_location,
                                         '--data', data_location,
                                         '--name', fake_name])

    assert batch.generate_name.call_count == 0
    assert batch.start_inference_instance.call_count == 1

    assert result.exit_code == 0


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_batch_exception(mocker, launch_mocks):
    model_location = '/fake/model/location'
    data_location = '/fake/data/location'

    mocker.patch.object(batch, 'start_inference_instance').side_effect = SubmitExperimentError

    runner = CliRunner()
    result = runner.invoke(batch.batch, ['--model-location', model_location,
                                         '--data', data_location])

    assert batch.generate_name.call_count == 1
    assert batch.start_inference_instance.call_count == 1

    assert result.exit_code == 1


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_batch_missing_model_location(launch_mocks):
    data_location = 'data'

    runner = CliRunner()
    result = runner.invoke(batch.batch, ['--data', data_location])

    assert batch.generate_name.call_count == 0
    assert batch.start_inference_instance.call_count == 0
    assert batch.validate_local_model_location.call_count == 0

    assert result.exit_code == 1


def test_missing_file(mocker, launch_mocks):
    data_location = 'data'
    local_model_location = '/non_existing_path'
    mocker.patch.object(batch, 'validate_local_model_location').side_effect = SystemExit(2)

    runner = CliRunner()
    result = runner.invoke(batch.batch, ['--data', data_location,
                                         '--local-model-location', local_model_location])

    assert batch.validate_local_model_location.call_count == 1
    assert result.exit_code == 2


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_validate_local_model_location(mocker):

    mocker.patch('os.path.isdir', return_value=False)

    with pytest.raises(SystemExit):
        batch.validate_local_model_location('/bla')
