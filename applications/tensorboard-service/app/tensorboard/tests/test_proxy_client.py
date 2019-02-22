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
