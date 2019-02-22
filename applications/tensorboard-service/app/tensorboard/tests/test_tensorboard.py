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
from unittest import mock

from kubernetes.client import V1Deployment, V1ObjectMeta, V1beta1Ingress, V1Pod, V1beta1IngressSpec, \
    V1beta1IngressRule, V1beta1HTTPIngressRuleValue, V1beta1HTTPIngressPath, V1PodStatus, V1beta1IngressBackend, \
    V1ContainerStatus
from kubernetes.client.rest import ApiException
import pytest
from pytest_mock import MockFixture

from k8s.models import K8STensorboardInstance
import tensorboard.tensorboard
from tensorboard.tensorboard import TensorboardManager
from tensorboard.models import TensorboardStatus, Run

FAKE_NAMESPACE = "fake-namespace"


@pytest.fixture
def tensorboard_manager_mocked(mocker) -> TensorboardManager:
    mocker.patch('k8s.models.NautaPlatformConfig')
    # noinspection PyTypeChecker
    mgr = TensorboardManager(api_client=mock.MagicMock(), namespace=FAKE_NAMESPACE, config=mock.MagicMock())

    return mgr


def test_incluster_init(mocker: MockFixture):
    fake_namespace = 'some-namespace'
    mocker.patch.object(tensorboard.tensorboard, 'config')
    mocker.patch('nauta.config.NautaPlatformConfig.incluster_init')
    mocker.patch('builtins.open', new=lambda *args, **kwargs: mock.MagicMock(
        __enter__=lambda *args, **kwargs: mock.MagicMock(
            read=lambda: fake_namespace
        )
    )
    )
    mgr = TensorboardManager.incluster_init()

    assert mgr.namespace == fake_namespace
    assert mgr.client


# noinspection PyShadowingNames
def test_create(tensorboard_manager_mocked: TensorboardManager):
    fake_runs = [
        Run(
            name="some-run-3",
            owner='alice'
        ),
        Run(
            name="some-run-2",
            owner='alice'
        ),
        Run(
            name="some-run-1",
            owner='bob'
        )
    ]
    tensorboard = tensorboard_manager_mocked.create(fake_runs)

    tensorboard_manager_mocked.client.create_deployment.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                                body=mock.ANY)
    tensorboard_manager_mocked.client.create_service.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                             body=mock.ANY)
    tensorboard_manager_mocked.client.create_ingress.assert_called_once_with(namespace=FAKE_NAMESPACE,
                                                                             body=mock.ANY)

    assert tensorboard


# noinspection PyShadowingNames
def test_list(tensorboard_manager_mocked: TensorboardManager):
    tensorboard_manager_mocked.list()

    tensorboard_manager_mocked.client.list_deployments.\
        assert_called_once_with(namespace=FAKE_NAMESPACE, label_selector='type=nauta-tensorboard')


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
            phase=fake_tensorboard_pod_phase,
            container_statuses=[
                V1ContainerStatus(
                    ready=True,
                    image='',
                    image_id='',
                    name='',
                    restart_count=0
                ),
                V1ContainerStatus(
                    ready=True,
                    image='',
                    image_id='',
                    name='',
                    restart_count=0
                )
            ]
        )
    )

    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = fake_deployment
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_ingress').return_value = fake_ingress
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = fake_pod
    mocker.patch('tensorboard.tensorboard.TensorboardManager._check_tensorboard_nginx_reachable').return_value = True
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
def test_get_by_runs(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    fake_tensorboard_id = '5c0b46de-4017-4062-9ac8-94698cc0c513'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id + '/'
    fake_tensorboard_pod_phase = 'RUNNING'
    expected_tensorboard_status = TensorboardStatus.RUNNING
    runs = [
        Run(
            name='run-name-1',
            owner='sigfrid'
        ),
        Run(
            name='run-name-2',
            owner='schreck'
        ),
        Run(
            name='run-name-3',
            owner='jacek'
        )
    ]

    k8s_tensorboard = K8STensorboardInstance.from_runs(id=fake_tensorboard_id, runs=runs)

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
            phase=fake_tensorboard_pod_phase,
            container_statuses=[
                V1ContainerStatus(
                    ready=True,
                    image='',
                    image_id='',
                    name='',
                    restart_count=0
                ),
                V1ContainerStatus(
                    ready=True,
                    image='',
                    image_id='',
                    name='',
                    restart_count=0
                )
            ]
        )
    )

    mocker.patch.object(tensorboard_manager_mocked.client, 'list_deployments', new=_fake_list_deployments)
    mocker.patch.object(tensorboard_manager_mocked.client, 'list_ingresses').return_value = [k8s_tensorboard.ingress]
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = fake_pod
    mocker.patch('tensorboard.tensorboard.TensorboardManager._check_tensorboard_nginx_reachable').return_value = True

    get_runs = [
        Run(
            name='run-name-2',
            owner='schreck'
        ),
        Run(
            name='run-name-3',
            owner='jacek'
        ),
        Run(
            name='run-name-1',
            owner='sigfrid'
        )
    ]

    tensorboard = tensorboard_manager_mocked.get_by_runs(get_runs)

    assert tensorboard.id == fake_tensorboard_id
    assert tensorboard.status == expected_tensorboard_status
    assert tensorboard.url == fake_tensorboard_path


# noinspection PyShadowingNames
def test_get_by_run_names_not_found(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_deployment').return_value = None

    get_runs = [
        Run(
            name='run-name-2',
            owner='schreck'
        ),
        Run(
            name='run-name-3',
            owner='jacek'
        ),
        Run(
            name='run-name-1',
            owner='sigfrid'
        )
    ]

    tensorboard = tensorboard_manager_mocked.get_by_runs(runs=get_runs)

    assert tensorboard is None


def test_get_by_runs_not_created_yet(mocker: MockFixture, tensorboard_manager_mocked: TensorboardManager):
    fake_tensorboard_id = '72a5cabc-548c-4a66-8ea9-645736569dfd'
    fake_tensorboard_path = '/tb/' + fake_tensorboard_id + '/'
    runs = [
        Run(
            name='run-name-1',
            owner='sigfrid'
        ),
        Run(
            name='run-name-2',
            owner='schreck'
        ),
        Run(
            name='run-name-3',
            owner='jacek'
        )
    ]

    k8s_tensorboard = K8STensorboardInstance.from_runs(id=fake_tensorboard_id, runs=runs)

    mocker.patch.object(tensorboard_manager_mocked.client, 'list_deployments').return_value = \
        [k8s_tensorboard.deployment]
    mocker.patch.object(tensorboard_manager_mocked.client, 'list_ingresses').return_value = [k8s_tensorboard.ingress]
    mocker.patch.object(tensorboard_manager_mocked.client, 'get_pod').return_value = None

    tensorboard = tensorboard_manager_mocked.get_by_runs(runs)

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
        V1Deployment(metadata=V1ObjectMeta(name='fake-name'))
    ]
    mocker.patch.object(tensorboard_manager_mocked, 'delete')
    mocker.patch.object(tensorboard.tensorboard, 'try_get_last_request_datetime').\
        return_value = datetime(year=2018, month=6, day=19, hour=12, minute=0)
    mocker.patch.object(tensorboard_manager_mocked, 'refresh_garbage_timeout')
    mocker.patch.object(tensorboard_manager_mocked, 'get_garbage_timeout').return_value = 1800
    tensorboard_manager_mocked.delete_garbage()

    # noinspection PyUnresolvedReferences
    assert tensorboard_manager_mocked.delete.call_count == delete_count


def test_delete_garbage_gateway_timeout(mocker, tensorboard_manager_mocked: TensorboardManager):
    mocker.patch.object(tensorboard_manager_mocked, 'list').side_effect = ApiException(
        status=HTTPStatus.GATEWAY_TIMEOUT.value
    )
    mocker.spy(tensorboard_manager_mocked, 'refresh_garbage_timeout')

    tensorboard_manager_mocked.delete_garbage()

    # noinspection PyUnresolvedReferences
    assert tensorboard_manager_mocked.refresh_garbage_timeout.call_count == 0


def test_delete_garbage_other_exception(mocker, tensorboard_manager_mocked: TensorboardManager):
    mocker.patch.object(tensorboard_manager_mocked, 'list').side_effect = ApiException(
        status=HTTPStatus.NOT_FOUND.value
    )

    with pytest.raises(ApiException):
        tensorboard_manager_mocked.delete_garbage()


# noinspection PyShadowingNames
def test_validate_runs(mocker, tensorboard_manager_mocked: TensorboardManager):
    def fake_isdir(path: str):
        return path in (TensorboardManager.OUTPUT_PUBLIC_MOUNT_PATH + '/jeanne/training1',
                        TensorboardManager.OUTPUT_PUBLIC_MOUNT_PATH + '/abbie/training2')

    mocker.patch('os.path.isdir', new=fake_isdir)
    fake_runs = [Run(name='training1', owner='jeanne'),
                 Run(name='training2', owner='abbie'),
                 Run(name='training3', owner='harold')]

    valid, invalid = tensorboard_manager_mocked.validate_runs(fake_runs)

    assert valid == [fake_runs[0], fake_runs[1]]
    assert invalid == [fake_runs[2]]
