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

import logging
import os

from kubernetes import config, client


API_GROUP_NAME = 'aggregator.aipg.intel.com'
RUN_PLURAL = 'runs'
RUN_VERSION = 'v1'


logger = logging.getLogger()


def publish(metrics):
    """
    Update metrics in specific Run object
    :param metrics Dict[str,str] of a data to apply
    :return: in case of any problems during update it throws an exception
    """
    name = os.getenv("RUN_NAME")
    if not name:
        logger.info('[no-persist mode] Metrics: {}'.format(metrics))
        return

    with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace','r') as ns_file:
        namespace = ns_file.read()

    body = {
        "spec": {
            "metrics": metrics
        }
    }

    config.load_incluster_config()
    api = client.CustomObjectsApi(client.ApiClient())

    raw_run = api.patch_namespaced_custom_object(group='aggregator.aipg.intel.com', namespace=namespace, body=body,
                                                 plural=RUN_PLURAL, version=RUN_VERSION, name=name)
    logger.info('Run patch response : {}'.format(raw_run))
