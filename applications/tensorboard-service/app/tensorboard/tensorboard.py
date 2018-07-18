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

from datetime import datetime, timedelta, timezone
import logging as log
from os import path
from typing import List, Optional
from uuid import uuid4

from kubernetes import config
from kubernetes.client import V1Deployment, V1ObjectMeta

from k8s.client import K8SAPIClient, K8SPodPhase
import k8s.models
from tensorboard.models import Tensorboard, TensorboardStatus, Run


class TensorboardManager:
    OUTPUT_PUBLIC_MOUNT_PATH = '/mnt/output'

    def __init__(self, namespace: str, api_client: K8SAPIClient):
        self.client = api_client
        self.namespace = namespace

    @classmethod
    def incluster_init(cls):
        config.load_incluster_config()

        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
            my_current_namespace = file.read()

        return cls(namespace=my_current_namespace, api_client=K8SAPIClient())

    @staticmethod
    def _get_current_datetime() -> datetime:
        return datetime.now(timezone.utc)

    def create(self, runs: List[Run]) -> Tensorboard:
        new_tensorboard = Tensorboard(id=str(uuid4()))

        k8s_tensorboard_model = k8s.models.K8STensorboardInstance.from_runs(runs=runs, id=new_tensorboard.id)

        self.client.create_deployment(namespace=self.namespace, body=k8s_tensorboard_model.deployment)
        self.client.create_service(namespace=self.namespace, body=k8s_tensorboard_model.service)
        self.client.create_ingress(namespace=self.namespace, body=k8s_tensorboard_model.ingress)

        new_tensorboard.url = k8s_tensorboard_model.ingress.spec.rules[0].http.paths[0].path

        return new_tensorboard

    def list(self) -> List[V1Deployment]:
        return self.client.list_deployments(namespace=self.namespace, label_selector='type=dls4e-tensorboard')

    @staticmethod
    def _convert_str_pod_phase_to_tensorboard_status(pod_phase_str: str) -> TensorboardStatus:
        try:
            pod_status = K8SPodPhase[pod_phase_str.upper()]
        except KeyError:
            pod_status = K8SPodPhase.UNKNOWN

        if pod_status == K8SPodPhase.RUNNING:
            tensorboard_status = TensorboardStatus.RUNNING
        else:
            tensorboard_status = TensorboardStatus.CREATING

        return tensorboard_status

    def get_by_id(self, id: str) -> Optional[Tensorboard]:
        name = 'tensorboard-' + id
        deployment = self.client.get_deployment(name=name, namespace=self.namespace)

        if deployment is None:
            return None

        ingress = self.client.get_ingress(name=name, namespace=self.namespace)

        pod = self.client.get_pod(namespace=self.namespace, label_selector=f'name={name},type=dls4e-tensorboard')

        # there might be some time when Kubernetes deployment has been created in cluster,
        # but pod is not present yet in cluster
        if pod is None:
            return Tensorboard(id=id, status=TensorboardStatus.CREATING, url=ingress.spec.rules[0].http.paths[0].path)

        pod_phase_str: str = pod.status.phase

        tensorboard_status = self._convert_str_pod_phase_to_tensorboard_status(pod_phase_str)

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

        pod = self.client.get_pod(namespace=self.namespace, label_selector=f'id={id},type=dls4e-tensorboard')

        if pod is None:
            return Tensorboard(id=id, status=TensorboardStatus.CREATING, url=ingress.spec.rules[0].http.paths[0].path)

        pod_phase_str: str = pod.status.phase

        tensorboard_status = self._convert_str_pod_phase_to_tensorboard_status(pod_phase_str)

        return Tensorboard(id=id, status=tensorboard_status, url=ingress.spec.rules[0].http.paths[0].path)

    def delete(self, tensorboard_deployment: V1Deployment):
        common_name = tensorboard_deployment.metadata.name

        self.client.delete_service(name=common_name, namespace=self.namespace)

        self.client.delete_ingress(name=common_name, namespace=self.namespace)

        self.client.delete_deployment(name=common_name, namespace=self.namespace)

    def delete_garbage(self):
        log.debug("searching for garbage...")
        tensorboards = self.list()

        for deployment in tensorboards:
            meta: V1ObjectMeta = deployment.metadata
            creation_timestamp: datetime = meta.creation_timestamp
            delta = TensorboardManager._get_current_datetime() - creation_timestamp
            if delta >= timedelta(seconds=1800):
                log.debug(f'garbage detected: {meta.name} , removing...')
                self.delete(deployment)
                log.debug(f'garbage removed: {meta.name}')

    def validate_runs(self, runs: List[Run]) -> (List[Run], List[Run]):
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
