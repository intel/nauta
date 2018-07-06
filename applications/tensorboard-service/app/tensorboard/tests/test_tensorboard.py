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

from kubernetes.client import V1Deployment, V1ObjectMeta, V1beta1Ingress, V1Pod, V1beta1IngressSpec, \
    V1beta1IngressRule, V1beta1HTTPIngressRuleValue, V1beta1HTTPIngressPath, V1PodStatus, V1beta1IngressBackend
import pytest
from pytest_mock import MockFixture

from k8s.models import K8STensorboardInstance
from tensorboard.tensorboard import TensorboardManager
from tensorboard.models import TensorboardStatus

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
@pytest.mark.parametrize(['fake_tensorboard_pod_phase', 'expected_tensorboard_status'],
                         [('RUNNING', TensorboardStatus.RUNNING),
                          ('running', TensorboardStatus.RUNNING),  # check if case-insensitive
                          ('Pending', TensorboardStatus.CREATING),
                          ('PENDING', TensorboardStatus.CREATING),
                          ('FAILED', TensorboardStatus.CREATING),
                          ('SUCCEEDED', TensorboardStatus.CREATING),
                          ('UNKNOWN', TensorboardStatus.CREATING),
                          ('invalid_phase', TensorboardStatus.CREATING)]
                         )
def test_get_by_id(mocker: MockFixture,
                   tensorboard_manager_mocked: TensorboardManager,
                   fake_tensorboard_pod_phase: str,
                   expected_tensorboard_status: TensorboardStatus):
    fake_tensorboard_id = 'cda7ad77-c499-4ef7-8f73-be7ce254be6a'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id

    fake_deployment = V1Deployment()
    fake_ingress = V1beta1Ingress(spec=V1beta1IngressSpec(
        rules=[
            V1beta1IngressRule(
                http=V1beta1HTTPIngressRuleValue(
                    paths=[V1beta1HTTPIngressPath(
                        backend=V1beta1IngressBackend(service_name='fake-service', service_port=80),
                        path=fake_tensorboard_path)]
                )
            )
        ]
    ))
    fake_pod = V1Pod(
        status=V1PodStatus(
            phase=fake_tensorboard_pod_phase
        )
    )

    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = fake_deployment
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_ingress').return_value = fake_ingress
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = fake_pod

    tensorboard = tensorboard_manager_mocked.get_by_id(id=fake_tensorboard_id)

    assert tensorboard.id == fake_tensorboard_id
    assert tensorboard.status == expected_tensorboard_status
    assert tensorboard.url == fake_tensorboard_path


# noinspection PyShadowingNames
def test_get_by_id_not_found(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = None

    tensorboard = tensorboard_manager_mocked.get_by_id(id='296ef39e-d4d8-48cd-bc6e-e27bc8fc1c2d')

    assert tensorboard is None


# there might be some time when Kubernetes deployment has been created in cluster, but pod is not present yet in cluster
# here we check if Tensorboard manager returns Tensorboard object in 'CREATING' state when such event occurrs
# noinspection PyShadowingNames
def test_get_by_id_pod_not_created_yet(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    fake_tensorboard_id = '72a5cabc-548c-4a66-8ea9-645736569dfd'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id

    fake_deployment = V1Deployment()
    fake_ingress = V1beta1Ingress(spec=V1beta1IngressSpec(
        rules=[
            V1beta1IngressRule(
                http=V1beta1HTTPIngressRuleValue(
                    paths=[V1beta1HTTPIngressPath(
                        backend=V1beta1IngressBackend(service_name='fake-service', service_port=80),
                        path=fake_tensorboard_path)]
                )
            )
        ]
    ))

    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = fake_deployment
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_ingress').return_value = fake_ingress
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = None

    tensorboard = tensorboard_manager_mocked.get_by_id(id=fake_tensorboard_id)

    assert tensorboard.id == fake_tensorboard_id
    assert tensorboard.status == TensorboardStatus.CREATING
    assert tensorboard.url == fake_tensorboard_path


# noinspection PyShadowingNames
def test_get_by_run_names(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    fake_tensorboard_id = '5c0b46de-4017-4062-9ac8-94698cc0c513'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id
    fake_tensorboard_pod_phase = 'RUNNING'
    expected_tensorboard_status = TensorboardStatus.RUNNING
    run_names = ['run-name-1', 'run-name-2', 'run-name-3']

    k8s_tensorboard = K8STensorboardInstance.from_run_name(id=fake_tensorboard_id, run_names_list=run_names)

    # mocking manually this method is done because we want to mock Kubernetes behaviour to check, if our code
    # requests Kubernetes API server for deployment with proper label_selector. If label_selector matches
    # created deployment, this mocked method will return it. Our code should pass the same label_selector regardless of
    # order of run_names in get_by_run_names parameter. That's why we create below get_run_names with other order to
    # check if returned deployment would still be the same.
    # noinspection PyUnusedLocal
    def _fake_list_deployments(namespace: str, label_selector: str):
        deployments = [k8s_tensorboard.deployment]

        splitted_label_selector = label_selector.split('=')
        label_selector_key = splitted_label_selector[0]
        label_selector_value = splitted_label_selector[1]

        if deployments[0].metadata.labels[label_selector_key] == label_selector_value:
            return deployments

    fake_pod = V1Pod(
        status=V1PodStatus(
            phase=fake_tensorboard_pod_phase
        )
    )

    mocker.patch.object(tensorboard_manager_mocked.client, 'list_deployments', new=_fake_list_deployments)
    mocker.patch.object(tensorboard_manager_mocked.client, 'list_ingresses').return_value = [k8s_tensorboard.ingress]
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = fake_pod

    get_run_names = ['run-name-3', 'run-name-1', 'run-name-2']

    tensorboard = tensorboard_manager_mocked.get_by_run_names(get_run_names)

    assert tensorboard.id == fake_tensorboard_id
    assert tensorboard.status == expected_tensorboard_status
    assert tensorboard.url == fake_tensorboard_path


# noinspection PyShadowingNames
def test_get_by_run_names_not_found(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = None

    tensorboard = tensorboard_manager_mocked.get_by_run_names(run_names=['run-name-3', 'run-name-1', 'run-name-2'])

    assert tensorboard is None


def test_get_by_run_names_not_created_yet(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    fake_tensorboard_id = '72a5cabc-548c-4a66-8ea9-645736569dfd'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id
    run_names = ['run-name-3', 'run-name-1', 'run-name-2']

    k8s_tensorboard = K8STensorboardInstance.from_run_name(id=fake_tensorboard_id, run_names_list=run_names)

    mocker.patch.object(tensorboard_manager_mocked.client, 'list_deployments').return_value = \
        [k8s_tensorboard.deployment]
    mocker.patch.object(tensorboard_manager_mocked.client, 'list_ingresses').return_value = [k8s_tensorboard.ingress]
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = None

    tensorboard = tensorboard_manager_mocked.get_by_run_names(run_names=['run-name-3', 'run-name-1', 'run-name-2'])

    assert tensorboard.id == fake_tensorboard_id
    assert tensorboard.status == TensorboardStatus.CREATING
    assert tensorboard.url == fake_tensorboard_path


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

    # noinspection PyUnresolvedReferences
    assert tensorboard_manager_mocked.delete.call_count == delete_count
