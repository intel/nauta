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

import logging as log
# noinspection PyProtectedMember
from os import getenv, _exit
from time import sleep
from typing import List

from kubernetes import client, config
from kubernetes.client import V1Pod, V1ObjectMeta, V1PodList, V1PodStatus, V1ContainerStatus, V1ContainerState, V1ContainerStateTerminated


JOB_SUCCESS_CONDITION = "Succeeded"

LOGGING_LEVEL_MAPPING = {"DEBUG": log.DEBUG,
                         "INFO": log.INFO,
                         "WARNING": log.WARNING,
                         "ERROR": log.ERROR,
                         "CRITICAL": log.CRITICAL}


def init_logging_level():
    logging_level_str = getenv("LOGGING_LEVEL")

    if logging_level_str is None:
        raise RuntimeError("LOGGING_LEVEL env var is not defined!")

    if logging_level_str not in LOGGING_LEVEL_MAPPING.keys():
        raise RuntimeError(f"LOGGING_LEVEL env var must be set to one out of {LOGGING_LEVEL_MAPPING.keys()}. "
                           f"Current value: {logging_level_str}")

    log.basicConfig(level=logging_level_str)
    log.critical(f"sidecar log level set to: {logging_level_str}")


def init_kubernetes_config():
    config.load_incluster_config()


def get_my_pod_name() -> str:
    my_pod_name = getenv("MY_POD_NAME")

    if my_pod_name is None:
        raise RuntimeError("MY_POD_NAME env var is not defined!")

    return my_pod_name


def get_my_namespace() -> str:
    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
        my_current_namespace = file.read()

    if not my_current_namespace:
        raise RuntimeError(f"error reading my current namespace {str(my_current_namespace)}")

    return my_current_namespace


def main():
    init_logging_level()
    init_kubernetes_config()
    my_pod_name = get_my_pod_name()
    my_namespace = get_my_namespace()

    v1 = client.CoreV1Api()

    my_pod: V1Pod = v1.read_namespaced_pod(name=my_pod_name, namespace=my_namespace)

    my_pod_metadata: V1ObjectMeta = my_pod.metadata

    my_run_name = my_pod_metadata.labels['runName']

    log.info("initialization succeeded")

    while True:
        my_run_pods: V1PodList = v1.list_namespaced_pod(namespace=my_namespace, label_selector=f"runName={my_run_name}")

        for pod in my_run_pods.items:
            pod_typed: V1Pod = pod
            pod_status: V1PodStatus = pod_typed.status
            container_statuses: List[V1ContainerStatus] = pod_status.container_statuses
            for status in container_statuses:
                container_name: str = status.name
                if container_name != "tensorflow":
                    continue

                container_state: V1ContainerState = status.state
                container_state_terminated: V1ContainerStateTerminated = container_state.terminated
                if container_state_terminated:
                    exit_code = container_state_terminated.exit_code
                    log.info(f"Tensorflow container of pod: {pod_typed.metadata.name} exited with code: {exit_code}, creating END hook")
                    open("/pod-data/END", 'a').close()
                    log.info("exiting...")
                    _exit(exit_code)
        log.info("No exited tensorflow container found")
        sleep(1)


if __name__ == '__main__':
    main()
