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
from http import HTTPStatus
import json
from unittest.mock import MagicMock

from flask.testing import FlaskClient
import pytest

import database


@pytest.fixture
def flask_client(mocker):
    mocker.patch('database.init_db')
    from proxy import app
    client = app.test_client()
    yield client


@pytest.mark.parametrize('url', ['/', '/random/url'])
# noinspection PyShadowingNames
def test_proxy(mocker, flask_client: FlaskClient, url):
    fake_upstream_response = 'hello world!'
    fake_upstream_response_status_code = HTTPStatus.OK
    mocker.patch('requests.request').return_value = MagicMock(content=fake_upstream_response.encode('utf-8'),
                                                              headers={'Content-Type': 'text/html'},
                                                              status_code=fake_upstream_response_status_code.value)
    mocker.patch('database.update_timestamp')

    response = flask_client.get(url)

    response_body = response.data.decode('utf-8')

    assert response_body == 'hello world!'
    assert response.status_code == HTTPStatus.OK
    # noinspection PyUnresolvedReferences
    assert database.update_timestamp.call_count == 1


def test_inactivity(mocker, flask_client: FlaskClient):
    fake_timestamp = datetime(2018, 7, 26, 12, 19, 34, 867831)
    mocker.patch('database.get_timestamp').return_value = fake_timestamp
    response = flask_client.get('/inactivity')

    response_body = response.data.decode('utf-8')
    response_json = json.loads(response_body)

    assert response_json['lastRequestDatetime'] == fake_timestamp.isoformat()
    assert response.status_code == HTTPStatus.OK
    # noinspection PyUnresolvedReferences
    assert database.get_timestamp.call_count == 1


def test_healthz(mocker, flask_client: FlaskClient):
    fake_upstream_response_status_code = HTTPStatus.OK
    mocker.patch('requests.get').return_value = MagicMock(status_code=fake_upstream_response_status_code.value)

    response = flask_client.get('/healthz')

    assert response.status_code == fake_upstream_response_status_code
