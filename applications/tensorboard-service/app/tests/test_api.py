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

from flask.testing import FlaskClient
from http import HTTPStatus
import json
from unittest.mock import MagicMock


import pytest
from pytest_mock import MockFixture

import api
from tensorboard.models import Tensorboard, TensorboardStatus


@pytest.fixture
def flask_client():
    client = api.app.test_client()
    yield client


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class ManagerMock:
    def create(self, run_names):
        return Tensorboard(
            id='1ba42a59-993f-4874-9854-a808bc941728',
            url='/test/url'
        )

    def get_by_run_names(self, run_name):
        return None

    @classmethod
    def incluster_init(cls):
        return cls()


# noinspection PyShadowingNames
def test_create(mocker, flask_client: FlaskClient):
    mocker.patch.object(api, 'TensorboardManager', new=ManagerMock)
    response = flask_client.post('/create/some-run')

    response_body = response.data.decode('utf-8')

    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == '1ba42a59-993f-4874-9854-a808bc941728'
    assert response_body_json['status'] == 'CREATING'
    assert response_body_json['url'] == '/test/url'


def test_create_conflict(mocker, flask_client: FlaskClient):
    fake_id = '025eb0bc-b219-437d-9974-8a5e871885f8'
    fake_url = '/test/url'

    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_run_names=lambda *args, **kwargs: Tensorboard(id=fake_id,
                                                                 url=fake_url,
                                                                 status=TensorboardStatus.RUNNING)
        )
    )
    mocker.patch.object(api, 'TensorboardManager', new=tensorboard_mgr)
    response = flask_client.post('/create/some-run')

    response_body = response.data.decode('utf-8')

    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == fake_id
    assert response_body_json['status'] == 'RUNNING'
    assert response_body_json['url'] == fake_url


# noinspection PyShadowingNames
def test_create_v2(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_run_names=lambda *args, **kwargs: None,
            create=lambda *args, **kwargs: Tensorboard(id='0c13c567-378e-4582-9ae3-3a40f2ca7e21',
                                                       url='/test/url')
        )
    )
    mocker.patch.object(api, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': ['run-name-1', 'run-name-2', 'run-name-3']
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.ACCEPTED

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == '0c13c567-378e-4582-9ae3-3a40f2ca7e21'
    assert response_body_json['status'] == 'CREATING'
    assert response_body_json['url'] == '/test/url'


# noinspection PyShadowingNames
@pytest.mark.parametrize('request_body', [
    {},
    {'runNames': []},
    {'badValue': 'badvalue'}
])
def test_create_v2_bad_request(flask_client: FlaskClient, request_body: dict):
    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_v2_conflict(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_run_names=lambda *args, **kwargs: Tensorboard(id='3cf769b5-436e-42ca-9710-c0a61b6c075d',
                                                                 url='/test/url',
                                                                 status=TensorboardStatus.RUNNING)
        )
    )
    mocker.patch.object(api, 'TensorboardManager', new=tensorboard_mgr)
    request_body = {
        'runNames': ['run-name-1']
    }

    response = flask_client.post('/tensorboard', data=json.dumps(request_body))

    assert response.status_code == HTTPStatus.CONFLICT

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == '3cf769b5-436e-42ca-9710-c0a61b6c075d'
    assert response_body_json['status'] == 'RUNNING'
    assert response_body_json['url'] == '/test/url'


# noinspection PyShadowingNames
def test_get_v2(mocker: MockFixture, flask_client: FlaskClient):
    fake_tensorboard = Tensorboard(id='3cf769b5-436e-42ca-9710-c0a61b6c075d',
                                   url='/test/url',
                                   status=TensorboardStatus.RUNNING)

    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_id=lambda *args, **kwargs: fake_tensorboard
        )
    )
    mocker.patch.object(api, 'TensorboardManager', new=tensorboard_mgr)

    response = flask_client.get(f'/tensorboard/{fake_tensorboard.id}')

    assert response.status_code == HTTPStatus.OK

    response_body = response.data.decode('utf-8')
    response_body_json = json.loads(response_body)

    assert response_body_json['id'] == fake_tensorboard.id
    assert response_body_json['status'] == fake_tensorboard.status.value
    assert response_body_json['url'] == fake_tensorboard.url


# noinspection PyShadowingNames
def test_get_v2_not_found(mocker: MockFixture, flask_client: FlaskClient):
    tensorboard_mgr = MagicMock(
        incluster_init=lambda *args, **kwargs: MagicMock(
            get_by_id=lambda *args, **kwargs: None
        )
    )
    mocker.patch.object(api, 'TensorboardManager', new=tensorboard_mgr)

    response = flask_client.get(f'/tensorboard/some-id')

    assert response.status_code == HTTPStatus.NOT_FOUND
