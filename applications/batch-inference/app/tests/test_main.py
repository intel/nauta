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

import main

from grpc._channel import _Rendezvous
import pytest


def test_make_prediction_retrying(mocker):
    mocker.patch('builtins.open')
    mocker.patch('tensorflow_serving.apis.predict_pb2.PredictRequest')
    predict_stub_mock = mocker.MagicMock()
    grpc_exception = _Rendezvous(mocker.MagicMock(), None, None, mocker.MagicMock())

    mocker.patch.object(predict_stub_mock, 'Predict').side_effect = [grpc_exception,
                                                                     grpc_exception,
                                                                     mocker.MagicMock(
                                                                         SerializeToString=lambda: b'result')]
    result = main.make_prediction(b'', predict_stub_mock)

    assert result == b'result'


def test_make_prediction_too_much_retrying(mocker):
    mocker.patch('builtins.open')
    mocker.patch('tensorflow_serving.apis.predict_pb2.PredictRequest')
    predict_stub_mock = mocker.MagicMock()
    grpc_exception = _Rendezvous(mocker.MagicMock(), None, None, mocker.MagicMock())

    mocker.patch.object(predict_stub_mock, 'Predict').side_effect = grpc_exception

    with pytest.raises(_Rendezvous):
        main.make_prediction(b'', predict_stub_mock)


def test_input_dir_does_not_exist(mocker):
    mocker.patch('os.getenv').return_value = 'fake_run_name'
    mocker.patch('os.path.isdir').return_value = False
    mocker.patch('argparse.ArgumentParser')

    with pytest.raises(RuntimeError):
        main.main()


def test_input_dir_is_empty(mocker):
    mocker.patch('os.getenv').return_value = 'fake_run_name'
    mocker.patch('os.path.isdir').return_value = True
    mocker.patch('os.listdir').return_value = []
    mocker.patch('argparse.ArgumentParser')

    with pytest.raises(RuntimeError):
        main.main()
