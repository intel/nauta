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
