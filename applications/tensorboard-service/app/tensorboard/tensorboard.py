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

from datetime import datetime, timedelta
from http import HTTPStatus
import logging as log
from os import path
from typing import List, Optional
from uuid import uuid4

from kubernetes import config
from kubernetes.client import V1Deployment, V1ObjectMeta, V1Pod, V1ContainerStatus
from kubernetes.client.rest import ApiException
import requests

from k8s.client import K8SAPIClient, K8SPodPhase
import k8s.models
from tensorboard.models import Tensorboard, TensorboardStatus, Run
from tensorboard.proxy_client import try_get_last_request_datetime
from nauta.config import NautaPlatformConfig


class TensorboardManager:
    OUTPUT_PUBLIC_MOUNT_PATH = '/mnt/output'
    NGINX_INGRESS_ADDRESS = 'nauta-ingress.nauta'

    def __init__(self, namespace: str, api_client: K8SAPIClient,
                 config: NautaPlatformConfig):
        self.client = api_client
        self.namespace = namespace
        self._config = config
        self._tb_timeout = self._config.get_tensorboard_timeout()
        self._last_tb_timeout_load = TensorboardManager._get_current_datetime()

    @classmethod
    def incluster_init(cls):
        config.load_incluster_config()

        nauta_config = NautaPlatformConfig.incluster_init()

        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
            my_current_namespace = file.read()

        return cls(namespace=my_current_namespace, api_client=K8SAPIClient(), config=nauta_config)

    @staticmethod
    def _get_current_datetime() -> datetime:
        return datetime.utcnow()

    def create(self, runs: List[Run]) -> Tensorboard:
        new_tensorboard = Tensorboard(id=str(uuid4()))

        k8s_tensorboard_model = k8s.models.K8STensorboardInstance.from_runs(runs=runs, id=new_tensorboard.id)

        self.client.create_deployment(namespace=self.namespace, body=k8s_tensorboard_model.deployment)
        self.client.create_service(namespace=self.namespace, body=k8s_tensorboard_model.service)
        self.client.create_ingress(namespace=self.namespace, body=k8s_tensorboard_model.ingress)

        new_tensorboard.url = k8s_tensorboard_model.ingress.spec.rules[0].http.paths[0].path

        return new_tensorboard

    def list(self) -> List[V1Deployment]:
        return self.client.list_deployments(namespace=self.namespace, label_selector='type=nauta-tensorboard')

    @staticmethod
    def _check_tensorboard_nginx_reachable(url) -> bool:
        log.debug("Checking if Tensorboard is reachable from Nginx...")
        try:
            response = requests.head(f"http://{TensorboardManager.NGINX_INGRESS_ADDRESS}{url}",
                                     headers={'Host': 'localhost'},
                                     timeout=5.0)
        except Exception:
            log.exception("Checking Tensorboard reachability failed!")
            return False

        if response.status_code == HTTPStatus.OK:
            log.debug("Tensorboard is reachable")
            return True

        log.debug(f"Tensorboard is unreachable. Got: {response.status_code} status code")
        return False

    @staticmethod
    def _check_tensorboard_status(pod: V1Pod, tensorboard_ingress_url: str) -> TensorboardStatus:
        pod_phase: str = pod.status.phase

        try:
            pod_status = K8SPodPhase[pod_phase.upper()]
        except KeyError:
            pod_status = K8SPodPhase.UNKNOWN

        if pod_status != K8SPodPhase.RUNNING:
            return TensorboardStatus.CREATING

        container_statuses: List[V1ContainerStatus] = pod.status.container_statuses

        for status in container_statuses:
            if not status.ready:
                return TensorboardStatus.CREATING

        if not TensorboardManager._check_tensorboard_nginx_reachable(tensorboard_ingress_url):
            return TensorboardStatus.CREATING

        return TensorboardStatus.RUNNING

    def get_by_id(self, id: str) -> Optional[Tensorboard]:
        name = 'tensorboard-' + id
        deployment = self.client.get_deployment(name=name, namespace=self.namespace)

        if deployment is None:
            return None

        ingress = self.client.get_ingress(name=name, namespace=self.namespace)

        pod = self.client.get_pod(namespace=self.namespace, label_selector=f'name={name},type=nauta-tensorboard')

        # there might be some time when Kubernetes deployment has been created in cluster,
        # but pod is not present yet in cluster
        if pod is None:
            return Tensorboard(id=id, status=TensorboardStatus.CREATING, url=ingress.spec.rules[0].http.paths[0].path)

        tensorboard_status = \
            self._check_tensorboard_status(pod, tensorboard_ingress_url=ingress.spec.rules[0].http.paths[0].path)

        return Tensorboard(id=id, status=tensorboard_status, url=ingress.spec.rules[0].http.paths[0].path)

    def get_by_runs(self, runs: List[Run]) -> Optional[Tensorboard]:
        runs_hash = k8s.models.K8STensorboardInstance.generate_run_names_hash(runs)

        deployments = self.client.list_deployments(namespace=self.namespace,
                                                   label_selector=f'runs-hash={runs_hash}')

        if len(deployments) == 0:
            return None

        deployment = deployments[0]
        deployment_metadata: V1ObjectMeta = deployment.metadata
        id = deployment_metadata.labels['id']

        ingresses = self.client.list_ingresses(namespace=self.namespace, label_selector=f'id={id}')

        ingress = ingresses[0]

        pod = self.client.get_pod(namespace=self.namespace, label_selector=f'id={id},type=nauta-tensorboard')

        if pod is None:
            return Tensorboard(id=id, status=TensorboardStatus.CREATING, url=ingress.spec.rules[0].http.paths[0].path)

        tensorboard_status = \
            self._check_tensorboard_status(pod, tensorboard_ingress_url=ingress.spec.rules[0].http.paths[0].path)

        return Tensorboard(id=id, status=tensorboard_status, url=ingress.spec.rules[0].http.paths[0].path)

    def delete(self, tensorboard_deployment: V1Deployment):
        common_name = tensorboard_deployment.metadata.name

        self.client.delete_service(name=common_name, namespace=self.namespace)

        self.client.delete_ingress(name=common_name, namespace=self.namespace)

        self.client.delete_deployment(name=common_name, namespace=self.namespace)

    def refresh_garbage_timeout(self):
        delta = TensorboardManager._get_current_datetime() - self._last_tb_timeout_load

        if delta >= timedelta(seconds=60):
            self._tb_timeout = self._config.get_tensorboard_timeout()
            self._last_tb_timeout_load = TensorboardManager._get_current_datetime()

    def get_garbage_timeout(self):
        try:
            log.debug(f'Garbage collection timeout : {self._tb_timeout}')
            return int(self._tb_timeout)
        except Exception:
            log.exception('Error during getting garbage collection timeout value')
            return 1800

    def delete_garbage(self):
        log.debug("searching for garbage...")

        try:
            tensorboards = self.list()
        except ApiException as ex:
            if ex.status == HTTPStatus.GATEWAY_TIMEOUT:
                log.exception("gateway timeout occurred when searching for garbage")
                return
            raise ex

        self.refresh_garbage_timeout()

        for deployment in tensorboards:
            meta: V1ObjectMeta = deployment.metadata
            deployment_name = meta.name

            last_request_datetime = try_get_last_request_datetime(proxy_address=deployment_name)
            if last_request_datetime is None:
                continue

            delta = TensorboardManager._get_current_datetime() - last_request_datetime
            if delta >= timedelta(seconds=self.get_garbage_timeout()):
                log.debug(f'garbage detected: {meta.name} , removing...')
                self.delete(deployment)
                log.debug(f'garbage removed: {meta.name}')

    @staticmethod
    def validate_runs(runs: List[Run]) -> (List[Run], List[Run]):
        """
        :param runs: runs to validate
        :return: (valid_runs: List[Run], invalid_runs: List[Run])
        """

        valid = []
        invalid = []

        for run in runs:
            expected_output_dir = path.join(TensorboardManager.OUTPUT_PUBLIC_MOUNT_PATH, run.owner, run.name)
            if path.isdir(expected_output_dir):
                valid.append(run)
            else:
                invalid.append(run)

        return valid, invalid
