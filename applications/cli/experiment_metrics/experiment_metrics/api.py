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

try:
    from http import HTTPStatus  # python3.5+ import
except ImportError:
    import httplib as HTTPStatus  # python2.7 import
import logging
import os

from kubernetes import config, client
from kubernetes.client.rest import ApiException


API_GROUP_NAME = 'aggregator.aipg.intel.com'
RUN_PLURAL = 'runs'
RUN_VERSION = 'v1'

MAX_RETRIES_COUNT = 3

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger = logging.getLogger('metrics')
logger.setLevel(logging.INFO)
logger.addHandler(ch)

run_k8s_name = os.getenv('RUN_NAME')

if run_k8s_name:
    config.load_incluster_config()
    api = client.CustomObjectsApi(client.ApiClient())


def publish(metrics, raise_exception=False):
    """
    Update metrics in specific Run object
    :param metrics Dict[str,str] of a data to apply
    :param raise_exception raise exception if any error occurs during metrics publishing, e.g. key conflict
    :return: with raise_exception=True in case of any problems during update it throws an exception
    """
    if not run_k8s_name:
        logger.info('[no-persist mode] Metrics: {}'.format(metrics))
        return

    with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r') as ns_file:
        namespace = ns_file.read()

    body = {
        "spec": {
            "metrics": metrics
        }
    }

    for i in range(MAX_RETRIES_COUNT):
        try:
            api.patch_namespaced_custom_object(group='aggregator.aipg.intel.com', namespace=namespace, body=body,
                                               plural=RUN_PLURAL, version=RUN_VERSION, name=run_k8s_name)
            break
        except ApiException as e:
            if e.status != HTTPStatus.CONFLICT or i == MAX_RETRIES_COUNT-1:
                logger.exception("Exception during saving metrics. All {} retries failed!".format(MAX_RETRIES_COUNT), e)
                if raise_exception:
                    raise e
