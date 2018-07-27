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

from datetime import datetime
from unittest.mock import MagicMock

import pytest
import requests.exceptions

import tensorboard.proxy_client


def test_try_get_last_request_datetime(mocker):
    resp = b'{"lastRequestDatetime": "2018-07-25T15:39:47"}'

    mocker.patch('requests.get').return_value = MagicMock(content=resp)

    last_request_datetimestamp = tensorboard.proxy_client.try_get_last_request_datetime(proxy_address='fake')

    assert last_request_datetimestamp == datetime(year=2018, month=7, day=25, hour=15, minute=39, second=47)


def test_try_get_last_request_datetime_raise_known_ex(mocker):
    mocker.patch('requests.get').side_effect = requests.exceptions.ConnectionError

    last_request_datetimestamp = tensorboard.proxy_client.try_get_last_request_datetime(proxy_address='fake')

    assert last_request_datetimestamp is None


def test_try_get_last_request_datetime_raise_unknown_ex(mocker):
    mocker.patch('requests.get').side_effect = TypeError

    with pytest.raises(TypeError):
        tensorboard.proxy_client.try_get_last_request_datetime(proxy_address='fake')
