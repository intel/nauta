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

from typing import List

from kubernetes import config, client

from platform_resources.user_model import User
from platform_resources.runs import list_runs
from util.logger import initialize_logger


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aipg.intel.com'
USERS_PLURAL = 'users'
USERS_VERSION = 'v1'


def list_users() -> List[User]:
    """
    Return list of users.
    :return: List of User objects
    """
    logger.debug('Listing users.')
    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    raw_users = api.list_cluster_custom_object(group=API_GROUP_NAME, plural=USERS_PLURAL,
                                               version=USERS_VERSION)

    users = [User.from_k8s_response_dict(user_dict) for user_dict in raw_users['items']]

    # Get experiment runs for each user
    # TODO: CHANGE IMPLEMENTATION TO USE AGGREGATED USER DATA AFTER CAN-366
    runs = list_runs()
    user_map = {user.name: user for user in users}
    for run in runs:
        user_map[run.submitter].experiment_runs.append(run)

    return users

