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


from http import HTTPStatus
import json
from unittest.mock import MagicMock

import pytest

from tensorboard.client import TensorboardServiceClient, TensorboardStatus, TensorboardServiceAPIException, \
    TensorboardRun, build_tensorboard_run_list
from cli_text_consts import TensorboardClientTexts as Texts


def test_get_tensorboard(mocker):
    fake_id = "083cac42-4e4b-4225-9eac-5225de87d242"
    fake_url = f'/tb/{fake_id}/'

    content = {
        'id': fake_id,
        'status': 'RUNNING',
        'url': fake_url
    }

    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.get').return_value = MagicMock(status_code=HTTPStatus.OK.value, content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    tensorboard = client.get_tensorboard(tensorboard_id=fake_id)

    assert tensorboard.id == fake_id
    assert tensorboard.status == TensorboardStatus.RUNNING
    assert tensorboard.url == fake_url


def test_get_tensorboard_not_found(mocker):
    fake_id = "083cac42-4e4b-4225-9eac-5225de87d242"

    mocker.patch('requests.get').return_value = MagicMock(status_code=HTTPStatus.NOT_FOUND.value)

    client = TensorboardServiceClient(address='fake-address')

    tensorboard = client.get_tensorboard(tensorboard_id=fake_id)

    assert not tensorboard


def test_get_tensorboard_server_error(mocker):
    fake_id = "083cac42-4e4b-4225-9eac-5225de87d242"

    content = {
        'code': HTTPStatus.INTERNAL_SERVER_ERROR.value,
        'message': 'Unexpected internal error'
    }

    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.get').return_value = MagicMock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                                                          content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    with pytest.raises(TensorboardServiceAPIException):
        client.get_tensorboard(tensorboard_id=fake_id)


@pytest.mark.parametrize('requests_post_return_status_code', [HTTPStatus.ACCEPTED.value, HTTPStatus.CONFLICT.value])
def test_create_tensorboard(mocker, requests_post_return_status_code: int):
    fake_id = "083cac42-4e4b-4225-9eac-5225de87d242"
    fake_url = f'/tb/{fake_id}/'

    content = {
        'id': fake_id,
        'status': 'RUNNING',
        'url': fake_url
    }

    fake_runs_list = [TensorboardRun(name='some-run', owner='c_namespace')]

    content_bytes = json.dumps(content).encode('utf-8')
    mocker.patch('requests.post').return_value = MagicMock(status_code=requests_post_return_status_code,
                                                           content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    tensorboard = client.create_tensorboard(runs=fake_runs_list)

    assert tensorboard.id == fake_id
    assert tensorboard.status == TensorboardStatus.RUNNING
    assert tensorboard.url == fake_url


@pytest.mark.parametrize('requests_post_return_status_code', [HTTPStatus.BAD_REQUEST.value,
                                                              HTTPStatus.INTERNAL_SERVER_ERROR.value,
                                                              HTTPStatus.UNPROCESSABLE_ENTITY])
def test_create_tensorboard_error(mocker, requests_post_return_status_code: int):

    fake_runs_list = [TensorboardRun(name='some-run', owner='c_namespace')]

    content = {
        'code': HTTPStatus.INTERNAL_SERVER_ERROR.value,
        'message': 'Unexpected internal error'
    }

    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.post').return_value = MagicMock(status_code=requests_post_return_status_code,
                                                           content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    with pytest.raises(TensorboardServiceAPIException):
        client.create_tensorboard(runs=fake_runs_list)


def test_tensorboard_runs_list():
    EXP1_NAME = "exp1"
    EXP2_NAME = "exp2"
    CURR_NAMESPACE = "curr_namespace"
    OWN_NAMESPACE = "owner2"

    experiment_list = [EXP1_NAME, f'{OWN_NAMESPACE}/{EXP2_NAME}']

    tensorboard_runs_list = build_tensorboard_run_list(exp_list=experiment_list, current_namespace=CURR_NAMESPACE)

    assert len(tensorboard_runs_list) == 2
    assert tensorboard_runs_list[0].name == EXP1_NAME
    assert tensorboard_runs_list[0].owner == CURR_NAMESPACE
    assert tensorboard_runs_list[1].name == EXP2_NAME
    assert tensorboard_runs_list[1].owner == OWN_NAMESPACE


def test_create_tensorboard_missing_experiments(mocker):

    fake_runs_list = [TensorboardRun(name='some-run', owner='c_namespace')]
    fake_exp_name = 'fake_name'
    fake_owner = 'fake_owner'
    content = {
        'code': HTTPStatus.INTERNAL_SERVER_ERROR.value,
        'message': 'Unexpected internal error',
        'invalidRuns': [{'name': fake_exp_name, 'owner': fake_owner}]
    }

    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                           content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    with pytest.raises(TensorboardServiceAPIException) as exe:
        client.create_tensorboard(runs=fake_runs_list)

    assert Texts.INVALID_RUNS_ERROR_MSG.format(invalid_runs_list=f"{fake_owner}/{fake_exp_name}") in str(exe.value)

    content['invalidRuns'] = []
    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                           content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    with pytest.raises(TensorboardServiceAPIException) as exe:
        client.create_tensorboard(runs=fake_runs_list)

    assert Texts.RUNS_NOT_EXIST_ERROR_MSG in str(exe.value)
