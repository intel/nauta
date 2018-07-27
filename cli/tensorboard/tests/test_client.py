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


from http import HTTPStatus
import json
from unittest.mock import MagicMock

import pytest

from tensorboard.client import TensorboardServiceClient, TensorboardStatus, TensorboardServiceAPIException, \
    TensorboardRun, build_tensorboard_run_list


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

    assert f'There is no data for the following experiments : {fake_owner}/{fake_exp_name}' in str(exe.value)

    content['invalidRuns'] = []
    content_bytes = json.dumps(content).encode('utf-8')

    mocker.patch('requests.post').return_value = MagicMock(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                           content=content_bytes)

    client = TensorboardServiceClient(address='fake-address')

    with pytest.raises(TensorboardServiceAPIException) as exe:
        client.create_tensorboard(runs=fake_runs_list)

    assert 'Experiments given as paramaters of the command don\'t exist.' in str(exe.value)
