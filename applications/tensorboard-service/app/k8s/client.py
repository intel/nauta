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

from enum import Enum
import logging as log
from http import HTTPStatus
from typing import List, Optional

from kubernetes import client
from kubernetes.client import V1DeploymentList, V1Deployment, V1Service, V1beta1Ingress, V1DeleteOptions, V1Pod, \
    V1beta1IngressList, V1PodList
from kubernetes.client.rest import ApiException


# taken from https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
class K8SPodPhase(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    UNKNOWN = 'UNKNOWN'


class K8SAPIClient:
    def __init__(self):
        self.apps_api_client = client.AppsV1Api()
        self.extensions_v1beta1_api_client = client.ExtensionsV1beta1Api()
        self.v1_api_client = client.CoreV1Api()
        self.custom_objects_client = client.CustomObjectsApi()

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
            if ex.status == HTTPStatus.NOT_FOUND:
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

    def list_ingresses(self, namespace: str, label_selector: str = None, **kwargs) -> List[V1beta1Ingress]:
        ingresses: V1beta1IngressList = self.extensions_v1beta1_api_client.list_namespaced_ingress(
            namespace=namespace,
            label_selector=label_selector,
            **kwargs
        )

        ingresses_list: List[V1beta1Ingress] = ingresses.items
        return ingresses_list

    def delete_ingress(self, name: str, namespace: str, **kwargs):
        self.extensions_v1beta1_api_client.delete_namespaced_ingress(name=name,
                                                                     namespace=namespace,
                                                                     body=V1DeleteOptions(),
                                                                     **kwargs)

    def get_pod(self, namespace: str, label_selector: str = None, **kwargs) -> Optional[V1Pod]:
        try:
            pods: V1PodList = self.v1_api_client.list_namespaced_pod(namespace=namespace,
                                                                     label_selector=label_selector,
                                                                     **kwargs)
        except ApiException as ex:
            if ex.status == HTTPStatus.NOT_FOUND:
                return None
            raise ex

        pods_list: List[V1Pod] = pods.items

        if len(pods_list) < 1:
            return None

        return pods_list[0]
