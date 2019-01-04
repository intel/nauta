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

from util import network
from requests import ConnectionError


FAKE_URL = 'http://url.com'


class MockedResponse(object):

    def __init__(self, status_code):
        self.status_code = status_code


def test_wait_for_connection_success(mocker):
    req_mock = mocker.patch("util.network.requests.get", side_effect=[MockedResponse(status_code=200)])
    ready = network.wait_for_connection(FAKE_URL)
    assert ready, 'correct connection marked as fail'
    assert req_mock.call_count == 1, 'more than one request: expected one'


def test_wait_for_connection_fail(mocker):
    req_mock = mocker.patch("util.network.requests.get", side_effect=[MockedResponse(status_code=500)])
    ready = network.wait_for_connection(FAKE_URL)
    assert not ready, 'incorrect connection marked as success'
    assert req_mock.call_count == 1, 'more than one request: expected one'


def test_wait_for_connection_should_retry_when_conn_refused(mocker):
    req_mock = mocker.patch("util.network.requests.get", side_effect=ConnectionError)
    expected_retries = 10
    ready = network.wait_for_connection(FAKE_URL, timeout=0)
    assert not ready, 'incorrect connection marked as success'
    assert req_mock.call_count == expected_retries, 'more than one request: expected one'
