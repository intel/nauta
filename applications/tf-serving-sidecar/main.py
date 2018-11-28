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

import logging as log
from os import getenv, _exit
from time import sleep

from kubernetes import client, config
from kubernetes.client import V1Job, V1JobStatus

log.basicConfig(level=log.DEBUG)

config.load_incluster_config()

batch_wrapper_job_name = getenv("BATCH_WRAPPER_JOB_NAME")

if batch_wrapper_job_name is None:
    raise RuntimeError("BATCH_WRAPPER_JOB_NAME env var is not defined!")

with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
    my_current_namespace = file.read()

if not my_current_namespace:
    raise RuntimeError(f"error reading my current namespace {str(my_current_namespace)}")

# CAN-1237 - by setting level of logs for k8s rest client to INFO I'm removing displaying content of
# every rest request sent by k8s client
k8s_rest_logger = log.getLogger('kubernetes.client.rest')
k8s_rest_logger.setLevel(log.INFO)

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
        open("/pod-data/END", 'a').close()
        log.info("exiting...")
        _exit(0)

    sleep(1)
