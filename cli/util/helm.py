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

from util.system import execute_system_command
from util.k8s.k8s_info import delete_namespace
from util.logger import initialize_logger
from cli_text_consts import UTIL_HELM_TEXTS as TEXTS


logger = initialize_logger(__name__)


def delete_user(username: str):
    """
    Removes a user with all his/her objects

    :param username: name of a user to be deleted
    Throws an excpetion in case of any errors
    """
    delete_namespace(username)

    delete_helm_release(username)


def delete_helm_release(release_name: str):
    """
    Deletes release of a helm's chart.

    :param release_name: name of a release to be removed
    In case of any problems it throws an exception
    """
    delete_release_command = ["helm", "delete", "--purge", release_name]

    output, err_code = execute_system_command(delete_release_command)

    if err_code or f"release \"{release_name}\" deleted" not in output:
        logger.error(output)
        raise RuntimeError(TEXTS["helm_release_removal_error_msg"].format(release_name=release_name))
