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
    result = runner.invoke(batch.batch, ['--model-location', model_location, '--data', data_location])

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
                                         '--local_model_location', local_model_location])

    assert batch.validate_local_model_location.call_count == 1
    assert result.exit_code == 2


# noinspection PyUnusedLocal,PyUnresolvedReferences
def test_validate_local_model_location(mocker):

    mocker.patch('os.path.isdir', return_value=False)

    with pytest.raises(SystemExit):
        batch.validate_local_model_location('/bla')
