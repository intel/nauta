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
