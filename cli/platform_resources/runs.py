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

from functools import partial
import re
import sre_constants
from typing import List

from kubernetes import config, client

from platform_resources.run_model import Run, RunStatus
from platform_resources.resource_filters import filter_by_name_regex, filter_by_state
from util.logger import initialize_logger
from util.exceptions import InvalidRegularExpressionError


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aggregator.aipg.intel.com'
RUN_PLURAL = 'runs'
RUN_VERSION = 'v1'


def list_runs(namespace: str = None, state: RunStatus = None, name_filter: str = None) -> List[Run]:
    """
    Return list of experiment runs.
    :param namespace: If provided, only runs from this namespace will be returned
    :param state: If provided, only runs with given state will be returned
    :param name_filter: If provided, only runs matching name_filter regular expression will be returned
    :return: List of Run objects
    In case of problems during getting a list of runs - throws an error
    """
    logger.debug('Listing runs.')
    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    if namespace:
        raw_runs = api.list_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                            plural=RUN_PLURAL, version=RUN_VERSION)
    else:
        raw_runs = api.list_cluster_custom_object(group=API_GROUP_NAME, plural=RUN_PLURAL, version=RUN_VERSION)

    try:
        name_regex = re.compile(name_filter) if name_filter else None
    except sre_constants.error as e:
        error_msg = f'Failed to compile regular expresssion: {name_filter}'
        logger.exception(error_msg)
        raise InvalidRegularExpressionError(error_msg) from e

    run_filters = [partial(filter_by_name_regex, name_regex=name_regex, spec_location=False),
                   partial(filter_by_state, state=state)]

    runs = [Run.from_k8s_response_dict(run_dict)
            for run_dict in raw_runs['items']
            if all(f(run_dict) for f in run_filters)]

    return runs
