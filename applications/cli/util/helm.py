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
        delete_release_command = [os.path.join(Config().config_path, 'helm'), "delete", "--purge", release_name]
    else:
        delete_release_command = [os.path.join(Config().config_path, 'helm'), "delete", release_name]

    if namespace:
        delete_release_command += ["--tiller-namespace", namespace]

    output, err_code, log_output = execute_system_command(' '.join(delete_release_command), shell=True)

    if (f"release \"{release_name}\" deleted" not in output and
            f"release: \"{release_name}\" not found" not in output):
        logger.error(log_output)
        raise RuntimeError(Texts.HELM_RELEASE_REMOVAL_ERROR_MSG.format(release_name=release_name))


def install_helm_chart(chart_dirpath: str, release_name: str = None, tiller_namespace: str = None):
    command = [os.path.join(Config().config_path, 'helm'), "install", chart_dirpath]
    if release_name:
        command.extend(["--name", release_name])
    if tiller_namespace:
        command.extend(["--tiller-namespace", tiller_namespace])

    output, err_code, log_output = execute_system_command(command)
    logger.debug(f"helm exit code: {err_code} returned: {output}")

    if err_code != 0:
        raise RuntimeError(f"helm returned with non-zero code: {err_code}")
