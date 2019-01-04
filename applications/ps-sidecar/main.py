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
from os import getenv
from sys import exit
from time import sleep

from kubernetes import client, config
from kubernetes.client import V1Pod, V1ObjectMeta


JOB_SUCCESS_CONDITION = "Succeeded"

LOGGING_LEVEL_MAPPING = {"DEBUG": log.DEBUG, "INFO": log.INFO, "WARNING": log.WARNING, "ERROR": log.ERROR,
                         "CRITICAL": log.CRITICAL}

logging_level_str = getenv("LOGGING_LEVEL")

if logging_level_str is None:
    raise RuntimeError("LOGGING_LEVEL env var is not defined!")

if logging_level_str not in LOGGING_LEVEL_MAPPING.keys():
    raise RuntimeError("LOGGING_LEVEL env var must be set to one out of {}. Current value: {}"
                       .format(LOGGING_LEVEL_MAPPING.keys(), logging_level_str))

log.basicConfig(level=logging_level_str)
log.critical("Ps sidecar log level set to: " + logging_level_str)

config.load_incluster_config()

my_pod_name = getenv("MY_POD_NAME")

if my_pod_name is None:
    raise RuntimeError("MY_POD_NAME env var is not defined!")

with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
    my_current_namespace = file.read()

if not my_current_namespace:
    raise RuntimeError(f"error reading my current namespace {str(my_current_namespace)}")


v1 = client.CoreV1Api()

my_pod: V1Pod = v1.read_namespaced_pod(name=my_pod_name, namespace=my_current_namespace)

my_pod_metadata: V1ObjectMeta = my_pod.metadata

try:
    my_tfjob_name = my_pod_metadata.owner_references[0].name
except IndexError:
    raise RuntimeError("couldn't read my pod tf_job_key - no owner reference!")

if my_tfjob_name is None or my_tfjob_name == "":
    raise RuntimeError("my_tfjob_name is not defined!")


coAPI = client.CustomObjectsApi()

log.info("initialization succeeded")

while True:
    log.info(f"fetching tfjob: {my_tfjob_name} ...")
    my_tfjob = coAPI.get_namespaced_custom_object(group="kubeflow.org",
                                                  version="v1alpha2",
                                                  namespace=my_current_namespace,
                                                  plural="tfjobs",
                                                  name=my_tfjob_name)

    job_conditions = my_tfjob["status"]["conditions"]

    for condition in job_conditions:
        if condition.get("type") == JOB_SUCCESS_CONDITION:
            log.info("Job succeeded, creating END hook")
            open("/pod-data/END", 'a').close()
            log.info("exiting...")
            exit(0)

    sleep(1)
