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
