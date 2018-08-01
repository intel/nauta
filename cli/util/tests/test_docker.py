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

import pytest
from http import HTTPStatus

from util.docker import get_tags_list, delete_tag, delete_images_for_experiment

SERVER_ADDRESS = "127.0.0.1:5000"
EXP_NAME = "exp_name"
TAG_NAME = "tag"

JSON_RESPONSE = {"tags": ["tag1", "tag2"]}


def test_tags_list_success(mocker):
    req_mock = mocker.patch('requests.get')
    req_mock.return_value.status_code = HTTPStatus.OK
    req_mock.return_value.json.return_value = JSON_RESPONSE

    list = get_tags_list(server_address=SERVER_ADDRESS, image_name=EXP_NAME)

    assert len(list) == 2


def test_tags_list_failure(mocker):
    req_mock = mocker.patch('requests.get')
    req_mock.return_value.status_code = HTTPStatus.NOT_FOUND
    req_mock.return_value.json = JSON_RESPONSE

    with pytest.raises(RuntimeError):
        get_tags_list(server_address=SERVER_ADDRESS, image_name=EXP_NAME)

    assert req_mock.call_count == 1


def test_delete_tag_success(mocker):
    req_mock_get = mocker.patch('requests.get')
    req_mock_get.return_value.status_code = HTTPStatus.OK
    req_mock_get.return_value.headers = {"Docker-Content-Digest": "digest"}
    req_mock_delete = mocker.patch('requests.delete')
    req_mock_delete.return_value.status_code = HTTPStatus.ACCEPTED

    delete_tag(server_address=SERVER_ADDRESS, image_name=EXP_NAME, tag=TAG_NAME)

    assert req_mock_delete.call_count == 1
    assert req_mock_get.call_count == 1


def test_delete_tag_failure_deletion(mocker):
    req_mock_get = mocker.patch('requests.get')
    req_mock_get.return_value.status_code = HTTPStatus.OK
    req_mock_get.return_value.headers = {"Docker-Content-Digest": "digest"}
    req_mock_delete = mocker.patch('requests.delete')
    req_mock_delete.return_value.status_code = 404

    with pytest.raises(RuntimeError):
        delete_tag(server_address=SERVER_ADDRESS, image_name=EXP_NAME, tag=TAG_NAME)

    assert req_mock_get.call_count == 1
    assert req_mock_delete.call_count == 1


def test_delete_tag_failure_get_digest(mocker):
    req_mock_get = mocker.patch('requests.get')
    req_mock_get.return_value.status_code = HTTPStatus.NOT_FOUND
    req_mock_delete = mocker.patch('requests.delete')

    with pytest.raises(RuntimeError):
        delete_tag(server_address=SERVER_ADDRESS, image_name=EXP_NAME, tag=TAG_NAME)

    assert req_mock_get.call_count == 1
    assert req_mock_delete.call_count == 0


def test_delete_images_for_experiment(mocker):
    mocker.patch("util.docker.K8sProxy")
    gtl_mock = mocker.patch("util.docker.get_tags_list", return_value=JSON_RESPONSE["tags"])
    dtg_mock = mocker.patch("util.docker.delete_tag")

    delete_images_for_experiment(exp_name=EXP_NAME)

    assert gtl_mock.call_count == 1
    assert dtg_mock.call_count == 2
