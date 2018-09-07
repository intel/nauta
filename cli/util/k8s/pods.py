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

from typing import Dict, List

from kubernetes import client, config
from kubernetes.client import V1PodList, V1Pod, V1DeleteOptions

from util.k8s.k8s_info import PodStatus


class K8SPod:
    def __init__(self, namespace: str, name: str, status: PodStatus, labels: Dict[str, str]):
        self._namespace = namespace

        self.name = name
        self.status = status
        self.labels = labels

    def delete(self):
        config.load_kube_config()

        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=self.name, namespace=self._namespace, body=V1DeleteOptions())


def list_pods(namespace: str, label_selector: str = '') -> List[K8SPod]:
    config.load_kube_config()

    v1 = client.CoreV1Api()
    pods_list: V1PodList = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

    pods: List[V1Pod] = pods_list.items

    k8s_pods: List[K8SPod] = []

    for pod in pods:
        pod_name: str = pod.metadata.name
        pod_status: str = pod.status.phase
        k8s_pod_status = PodStatus(pod_status.upper())
        pod_labels = pod.metadata.labels

        k8s_pod = K8SPod(namespace=namespace, name=pod_name, status=k8s_pod_status, labels=pod_labels)

        k8s_pods.append(k8s_pod)

    return k8s_pods
