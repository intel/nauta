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
