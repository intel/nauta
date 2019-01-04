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

from flask.testing import FlaskClient
from http import HTTPStatus
import json
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockFixture

import api.main
from tensorboard.models import Tensorboard, TensorboardStatus


@pytest.fixture
def flask_client():
    client = api.main.app.test_client()
    yield client


# noinspection PyShadowingNames
def test_create(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_runs=lambda *args, **kwargs: None,
            create=lambda *args, **kwargs: Tensorboard(id='0c13c567-378e-4582-9ae3-3a40f2ca7e21',
                                                       url='/test/url/'),
            validate_runs=lambda runs: (runs, [])
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': [
            {
                'name': 'run-name-1',
                'owner': 'carl'
            },
            {
                'name': 'training-p-18-07-11-17-31-13',
                'owner': 'jay'
            },
            {
                'name': 'training-p-18-07-11-17-30-14',
                'owner': 'jay'
            }
        ]
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.ACCEPTED

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == '0c13c567-378e-4582-9ae3-3a40f2ca7e21'
    assert response_body_json['status'] == 'CREATING'
    assert response_body_json['url'] == '/test/url/'
    assert not response_body_json.get('invalidRuns', None)


# noinspection PyShadowingNames
@pytest.mark.parametrize('request_body', [
    {},
    {'runNames': []},
    {'badValue': 'badvalue'},
    [],
    [{}],
    {'runNames': [{}]},
    {'runNames': [{'name': 'some-run'}]},
    {'runNames': [{'owner': 'jack'}]},
    {'runNames': [{'name': 'some-run', 'owner': 'jack'}, {}]},
    {'runNames': [{'name': 'some-run', 'owner': 'jack'}, {'owner': 'jack'}]}
])
def test_create_bad_request(flask_client: FlaskClient, request_body: dict):
    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.BAD_REQUEST


# noinspection PyShadowingNames
def test_create_conflict(mocker: MockFixture, flask_client: FlaskClient):
    fake_tensorboard_id = '3cf769b5-436e-42ca-9710-c0a61b6c075d'
    fake_tensorboard_url = '/test/url/'
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_runs=lambda *args, **kwargs: Tensorboard(id=fake_tensorboard_id,
                                                            url=fake_tensorboard_url,
                                                            status=TensorboardStatus.RUNNING),
            validate_runs=lambda runs: (runs, [])
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': [
            {
                'name': 'run-name-1',
                'owner': 'carl'
            },
            {
                'name': 'training-p-18-07-11-17-31-13',
                'owner': 'jay'
            },
            {
                'name': 'training-p-18-07-11-17-30-14',
                'owner': 'jay'
            }
        ]
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.CONFLICT

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == fake_tensorboard_id
    assert response_body_json['status'] == 'RUNNING'
    assert response_body_json['url'] == fake_tensorboard_url
    assert not response_body_json.get('invalidRuns', None)


# noinspection PyShadowingNames
def test_get(mocker: MockFixture, flask_client: FlaskClient):
    fake_tensorboard = Tensorboard(id='3cf769b5-436e-42ca-9710-c0a61b6c075d',
                                   url='/test/url/',
                                   status=TensorboardStatus.RUNNING)

    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_id=lambda *args, **kwargs: fake_tensorboard
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)

    response = flask_client.get(f'/tensorboard/{fake_tensorboard.id}')

    assert response.status_code == HTTPStatus.OK

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == fake_tensorboard.id
    assert response_body_json['status'] == fake_tensorboard.status.value
    assert response_body_json['url'] == fake_tensorboard.url


# noinspection PyShadowingNames
def test_get_not_found(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_id=lambda *args, **kwargs: None
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)

    response = flask_client.get(f'/tensorboard/some-id')

    assert response.status_code == HTTPStatus.NOT_FOUND


# noinspection PyShadowingNames
def test_create_all_invalid_runs(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            validate_runs=lambda runs: ([], runs),
            get_by_runs=lambda *args, **kwargs: None
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': [
            {
                'name': 'run-name-1',
                'owner': 'carl'
            },
            {
                'name': 'training-p-18-07-11-17-31-13',
                'owner': 'jay'
            },
            {
                'name': 'training-p-18-07-11-17-30-14',
                'owner': 'jay'
            }
        ]
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['code'] == HTTPStatus.UNPROCESSABLE_ENTITY.value
    assert response_body_json['invalidRuns'] == request_body['runNames']


# noinspection PyShadowingNames
def test_create_partial_invalid_runs(mocker: MockFixture, flask_client: FlaskClient):
    fake_tensorboard_id = '3cf769b5-436e-42ca-9710-c0a61b6c075d'
    fake_tensorboard_url = '/test/url/'

    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            validate_runs=lambda runs: ([runs[0], runs[1]], [runs[2]]),
            create=lambda *args, **kwargs: Tensorboard(id=fake_tensorboard_id, url=fake_tensorboard_url),
            get_by_runs=lambda *args, **kwargs: None
        )
    )
    mocker.patch.object(api.main, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': [
            {
                'name': 'run-name-1',
                'owner': 'carl'
            },
            {
                'name': 'training-p-18-07-11-17-31-13',
                'owner': 'jay'
            },
            {
                'name': 'training-p-18-07-11-17-30-14',
                'owner': 'jay'
            }
        ]
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.ACCEPTED

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == fake_tensorboard_id
    assert response_body_json['status'] == 'CREATING'
    assert response_body_json['url'] == fake_tensorboard_url
    assert response_body_json['invalidRuns'] == [request_body['runNames'][2]]
