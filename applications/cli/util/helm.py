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

import os

from util.config import Config
from util.spinner import spinner
from util.system import execute_system_command
from util.k8s.k8s_info import delete_namespace
from util.logger import initialize_logger
from cli_text_consts import UtilHelmTexts as Texts
from cli_text_consts import UserDeleteCmdTexts as TextsDel

logger = initialize_logger(__name__)


def delete_user(username: str):
    """
    Removes a user with all his/her objects

    :param username: name of a user to be deleted
    Throws an excpetion in case of any errors
    """
    with spinner(text=TextsDel.DELETION_DELETING_NAMESPACE):
        delete_namespace(username)

    with spinner(text=TextsDel.DELETION_DELETING_USERS_OBJECTS):
        delete_helm_release(username, purge=True)


def delete_helm_release(release_name: str, purge=False, namespace: str = None):
    """
    Deletes release of a helm's chart.

    :param release_name: name of a release to be removed
    :param purge: if True, helm release will be purged
    In case of any problems it throws an exception
    """
    if purge:
        delete_release_command = ["helm", "delete", "--purge", release_name]
    else:
        delete_release_command = ["helm", "delete", release_name]

    if namespace:
        delete_release_command += ["--tiller-namespace", namespace]
    env = os.environ.copy()
    env['PATH'] = Config().config_path + os.pathsep + env['PATH']
    output, err_code, log_output = execute_system_command(' '.join(delete_release_command), env=env, shell=True)

    if (f"release \"{release_name}\" deleted" not in output and
            f"release: \"{release_name}\" not found" not in output):
        logger.error(log_output)
        raise RuntimeError(Texts.HELM_RELEASE_REMOVAL_ERROR_MSG.format(release_name=release_name))


def install_helm_chart(chart_dirpath: str, release_name: str = None, tiller_namespace: str = None):
    command = ["helm", "install", chart_dirpath]
    if release_name:
        command.extend(["--name", release_name])
    if tiller_namespace:
        command.extend(["--tiller-namespace", tiller_namespace])

    env = os.environ.copy()
    env['PATH'] = f"{Config().config_path}{os.pathsep}{env['PATH']}"
    output, err_code, log_output = execute_system_command(command, env=env)
    logger.debug(f"helm exit code: {err_code} returned: {output}")

    if err_code != 0:
        raise RuntimeError(f"helm returned with non-zero code: {err_code}")
