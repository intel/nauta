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
from typing import List, Optional

from kubernetes import client, config
from kubernetes.client import V1DeploymentList, V1Deployment, V1ObjectMeta, V1Service, V1beta1Ingress, V1DeleteOptions
from kubernetes.client.rest import ApiException

import models


class K8SAPIClient:
    def __init__(self):
        self.apps_api_client = client.AppsV1Api()
        self.extensions_v1beta1_api_client = client.ExtensionsV1beta1Api()
        self.v1_api_client = client.CoreV1Api()

    def create_deployment(self, namespace: str, body: V1Deployment, **kwargs):
        self.apps_api_client.create_namespaced_deployment(namespace=namespace, body=body, **kwargs)

    def list_deployments(self, namespace: str, label_selector: str = None, **kwargs) -> List[V1Deployment]:
        deployments: V1DeploymentList = self.apps_api_client.list_namespaced_deployment(
            namespace=namespace,
            label_selector=label_selector,
            **kwargs
        )
        deployments_list: List[V1Deployment] = deployments.items
        return deployments_list

    def get_deployment(self, name: str, namespace: str, **kwargs) -> Optional[V1Deployment]:

        try:
            deployment = self.apps_api_client.read_namespaced_deployment(name=name, namespace=namespace, **kwargs)
        except ApiException as ex:
            log.warning("deployment not found!")
            if ex.status == 404:
                return None
            raise ex

        return deployment

    def delete_deployment(self, name: str, namespace: str, **kwargs):
        self.apps_api_client.delete_namespaced_deployment(name=name, namespace=namespace, body=V1DeleteOptions(),
                                                          **kwargs)

    def create_service(self, namespace: str, body: V1Service, **kwargs):
        self.v1_api_client.create_namespaced_service(namespace=namespace, body=body, **kwargs)

    def get_service(self, name: str, namespace: str, **kwargs) -> V1Service:
        return self.v1_api_client.read_namespaced_service(name=name, namespace=namespace, **kwargs)

    def delete_service(self, name: str, namespace: str, **kwargs):
        self.v1_api_client.delete_namespaced_service(name=name, namespace=namespace, body=V1DeleteOptions(), **kwargs)

    def create_ingress(self, namespace: str, body: V1beta1Ingress, **kwargs):
        self.extensions_v1beta1_api_client.create_namespaced_ingress(namespace=namespace, body=body, **kwargs)

    def get_ingress(self, name: str, namespace: str, **kwargs) -> V1beta1Ingress:
        return self.extensions_v1beta1_api_client.read_namespaced_ingress(name=name, namespace=namespace, **kwargs)

    def delete_ingress(self, name: str, namespace: str, **kwargs):
        self.extensions_v1beta1_api_client.delete_namespaced_ingress(name=name,
                                                                     namespace=namespace,
                                                                     body=V1DeleteOptions(),
                                                                     **kwargs)


class TensorboardManager:
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

    def create(self, run_name: str) -> str:
        """
        :param run_name:
        :return: URL postfix fo accessing Tensorboard instance
        """
        k8s_tensorboard_model = models.K8STensorboardInstance.from_run_name(run_name)

        self.client.create_deployment(namespace=self.namespace, body=k8s_tensorboard_model.deployment)
        self.client.create_service(namespace=self.namespace, body=k8s_tensorboard_model.service)
        self.client.create_ingress(namespace=self.namespace, body=k8s_tensorboard_model.ingress)

        return k8s_tensorboard_model.ingress.spec.rules[0].http.paths[0].path

    def list(self) -> List[V1Deployment]:
        return self.client.list_deployments(namespace=self.namespace, label_selector='type=dls4e-tensorboard')

    def get(self, run_name: str) -> Optional[V1Deployment]:
        name = 'tensorboard-' + run_name
        return self.client.get_deployment(name=name, namespace=self.namespace)

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