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
