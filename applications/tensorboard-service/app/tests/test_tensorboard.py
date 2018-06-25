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
from unittest import mock
import pytest

from kubernetes.client import V1Deployment, V1ObjectMeta

from tensorboard import TensorboardManager

FAKE_NAMESPACE = "fake-namespace"


@pytest.fixture
def tensorboard_manager_mocked() -> TensorboardManager:
    # noinspection PyTypeChecker
    mgr = TensorboardManager(api_client=mock.MagicMock(), namespace=FAKE_NAMESPACE)

    return mgr


# noinspection PyShadowingNames
def test_create(tensorboard_manager_mocked: TensorboardManager):
    tensorboard_manager_mocked.create("fake-run")

    tensorboard_manager_mocked.client.create_deployment.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                                           body=mock.ANY)
    tensorboard_manager_mocked.client.create_service.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                                body=mock.ANY)
    tensorboard_manager_mocked.client.create_ingress.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                                body=mock.ANY)


# noinspection PyShadowingNames
def test_list(tensorboard_manager_mocked: TensorboardManager):
    tensorboard_manager_mocked.list()

    tensorboard_manager_mocked.client.list_deployments.\
        assert_called_once_with(namespace=FAKE_NAMESPACE, label_selector='type=dls4e-tensorboard')


# noinspection PyShadowingNames
def test_delete(tensorboard_manager_mocked: TensorboardManager):
    fake_deployment = mock.MagicMock()

    # noinspection PyTypeChecker
    tensorboard_manager_mocked.delete(tensorboard_deployment=fake_deployment)

    tensorboard_manager_mocked.client.delete_deployment.assert_called_once_with(name=mock.ANY,
                                                                                namespace=FAKE_NAMESPACE)

    tensorboard_manager_mocked.client.delete_service.assert_called_once_with(name=mock.ANY,
                                                                                namespace=FAKE_NAMESPACE)

    tensorboard_manager_mocked.client.delete_ingress.assert_called_once_with(name=mock.ANY,
                                                                                namespace=FAKE_NAMESPACE)


# noinspection PyShadowingNames
@pytest.mark.parametrize("current_datetime,delete_count", [
    (datetime(year=2018, month=6, day=19, hour=12, minute=0), 0),
    (datetime(year=2018, month=6, day=19, hour=12, minute=29, second=59), 0),
    (datetime(year=2018, month=6, day=19, hour=12, minute=30, second=0), 1),
    (datetime(year=2018, month=6, day=19, hour=13, minute=0), 1)
])
def test_delete_garbage(mocker, tensorboard_manager_mocked: TensorboardManager,
                        current_datetime: datetime, delete_count: int):
    mocker.patch.object(TensorboardManager, '_get_current_datetime').return_value = current_datetime
    mocker.patch.object(tensorboard_manager_mocked, 'list').return_value = [
        V1Deployment(metadata=V1ObjectMeta(creation_timestamp=datetime(year=2018, month=6, day=19, hour=12, minute=0)))
    ]
    mocker.patch.object(tensorboard_manager_mocked, 'delete')
    tensorboard_manager_mocked.delete_garbage()

    assert tensorboard_manager_mocked.delete.call_count == delete_count
