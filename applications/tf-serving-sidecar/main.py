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
from os import getenv, _exit, path
from time import sleep

from kubernetes import client, config
from kubernetes.client import V1Job, V1JobStatus

END_HOOK_FILEPATH = "/pod-data/END"

log.basicConfig(level=log.DEBUG)

# CAN-1237 - by setting level of logs for k8s rest client to INFO I'm removing displaying content of
# every rest request sent by k8s client
k8s_rest_logger = log.getLogger('kubernetes.client.rest')
k8s_rest_logger.setLevel(log.INFO)


def main():
    if path.isfile(END_HOOK_FILEPATH):
        log.info("END hook file already created, exiting...")
        return

    config.load_incluster_config()

    batch_wrapper_job_name = getenv("BATCH_WRAPPER_JOB_NAME")

    if batch_wrapper_job_name is None:
        raise RuntimeError("BATCH_WRAPPER_JOB_NAME env var is not defined!")

    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
        my_current_namespace = file.read()

    if not my_current_namespace:
        raise RuntimeError(f"error reading my current namespace {str(my_current_namespace)}")

    v1 = client.BatchV1Api()

    while True:
        batch_wrapper_job: V1Job = v1.read_namespaced_job(name=batch_wrapper_job_name, namespace=my_current_namespace)

        batch_wrapper_job_status: V1JobStatus = batch_wrapper_job.status

        active_pods = batch_wrapper_job_status.active if batch_wrapper_job_status.active is not None else 0
        succeeded_pods = batch_wrapper_job_status.succeeded if batch_wrapper_job_status.succeeded is not None else 0

        # model server should also be closed when there is failure in batch wrapper job
        if hasattr(batch_wrapper_job_status, 'failed') and batch_wrapper_job_status.failed is not None:
            failed_pods = batch_wrapper_job_status.failed
        else:
            failed_pods = 0

        if active_pods == 0 and (succeeded_pods > 0 or failed_pods > 0):
            log.info(f"active_pods == {active_pods}, succeeded_pods == {succeeded_pods}, failed_pods == {failed_pods}, "
                     f"creating END hook")
            open(END_HOOK_FILEPATH, 'a').close()
            log.info("exiting...")
            return

        sleep(1)


if __name__ == '__main__':
    main()
    _exit(0)
