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

import time

from marshmallow import ValidationError

from git_repo_manager.client import GitRepoManagerClient
from platform_resources.user import User
import platform_resources.user as model
from util.k8s.k8s_info import find_namespace, NamespaceStatus
from util.k8s.kubectl import UserState, logger

from util.logger import initialize_logger
from util.k8s import k8s_proxy_context_manager
from util.exceptions import K8sProxyCloseError, KubernetesError
from util.app_names import NAUTAAppNames
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from platform_resources.custom_object_meta_model import validate_kubernetes_name
from cli_text_consts import PlatformResourcesUsersTexts as Texts
from cli_text_consts import UserDeleteCmdTexts as TextsDel
from util.spinner import spinner

logger = initialize_logger(__name__)

# Samba users must match system users, therefore there is a need to blacklist some names.
# This list is genetated by running shell on samba containers and listing all users
# and groups (/etc/passwd and /etc/groups)
SAMBA_USERNAME_BLACKLIST = [ 'root', 'bin', 'daemon', 'adm', 'lp', 'sync', 'shutdown',
                             'halt', 'mail', 'operator', 'games', 'ftp', 'nobody',
                             'systemd-network', 'dbus',
                             'root', 'bin', 'daemon', 'sys', 'adm', 'tty', 'disk', 'lp',
                             'mem', 'kmem', 'wheel', 'cdrom', 'mail', 'man', 'dialout',
                             'floppy', 'games', 'tape', 'video', 'ftp', 'lock', 'audio',
                             'nobody', 'users', 'utmp', 'utempter', 'input',
                             'systemd-journal', 'systemd-network', 'dbus', 'printadmin' ]


def purge_user(username: str):
    """
    Removes all system's artifacts that belong to a removed user.
    K8s objects are removed during removal of a namespace.
    :param username: name of a user for which artifacts should be removed
    It throws exception in case of any problems detected during removal of a user
    """
    try:
        # remove data from elasticsearch
        with k8s_proxy_context_manager.K8sProxy(NAUTAAppNames.ELASTICSEARCH) as proxy,\
            spinner(text=TextsDel.DELETION_DELETING_USERS_EXPERIMENTS):
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            es_client.delete_logs_for_namespace(username)

        # remove data from git repo manager
        with k8s_proxy_context_manager.K8sProxy(NAUTAAppNames.GIT_REPO_MANAGER) as proxy,\
                spinner(text=TextsDel.DELETION_DELETING_USERS_REPOSITORY):
            grm_client = GitRepoManagerClient(host='127.0.0.1', port=proxy.tunnel_port)
            grm_client.delete_nauta_user(username=username)
    except K8sProxyCloseError as exe:
        logger.exception("Error during closing of a proxy.")
        raise exe
    except Exception as exe:
        logger.exception(f"Error during removal of {username} user data")
        raise exe


def validate_user_name(username: str) -> None:
    """
    Verifies whether a name given as a parameter is a value
    accepted by the NAUTA system.

    :param username: - name of a user
    :return: throws a ValueError in case when username cannot be accepted by
    the NAUTA system. Message in error describes a detected problem
    """
    # name cannot be longer than 32 and shorter than 1 character - due to lmitations
    # of a mechanism responsible for creating user/public shares
    if not username:
        raise ValueError(Texts.USERNAME_CANNOT_BE_EMPTY_ERROR_MSG)

    if len(username) > 32:
        raise ValueError(Texts.USERNAME_TOO_LONG_ERROR_MSG)

    # name must be a correct k8s name
    try:
        validate_kubernetes_name(username)
    except ValidationError:
        raise ValueError(Texts.INCORRECT_K8S_USERNAME_ERROR_MSG)

    if username in SAMBA_USERNAME_BLACKLIST:
        raise ValueError(Texts.USERNAME_IS_RESERVED_FOR_SYSTEM_USE)


def is_user_created(username: str, timeout: int = 1) -> bool:
    """
    Waits until a user has been created (got CREATED status). If during a given timeout user hasn't been created
    it returns False. Otherwise - it return True.
    :param username: name of a user to be checked
    :param timeout: timeout expressed in second, default value = 1. If 0 is passed as timeout - the function
           doesn't wait for setting CREATED status - it just checks the current status of a given user
    :return: True if user has received CREATED status, False otherwise
    It raises an exception in case of any unexpected situation.
    """
    user = User.get(username)
    if user and model.UserStatus.CREATED == user.state:
        return True

    for i in range(timeout):
        time.sleep(1)
        user = User.get(username)
        logger.debug(f"Users state : {user.state}")
        if user and model.UserStatus.CREATED == user.state:
            return True

    return False


def check_users_presence(username: str) -> UserState:
    """
    Checks whether a user with a given name exists. It searches also for a namespace
    with a name equal to the given username

    :param username: username
    :return: returns a current state of user - as an item for UserState enum
    In case of problems during gathering user's data - it raises an exception.
    """
    namespace = find_namespace(username)

    if namespace != NamespaceStatus.NOT_EXISTS:
        logger.debug("Namespace {} already exists.".format(username))
        return UserState(namespace.value)

    try:
        user_data = User.get(username)

        if user_data and user_data.name == username:
            return UserState.ACTIVE
        else:
            return UserState.NOT_EXISTS

    except Exception as exe:
        error_message = Texts.USER_PRESENCE_CHECK_ERROR_MSG
        logger.error(error_message)
        raise KubernetesError(error_message) from exe
