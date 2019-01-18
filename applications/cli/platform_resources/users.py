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

import time

from typing import List

from kubernetes import config, client

from kubernetes.client.rest import ApiException
from marshmallow import ValidationError

from platform_resources.user_model import User
from platform_resources.runs import list_runs
import platform_resources.user_model as model

from util.logger import initialize_logger
from util.k8s import k8s_proxy_context_manager
from util.exceptions import K8sProxyCloseError
from util.app_names import NAUTAAppNames
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from platform_resources.custom_object_meta_model import validate_kubernetes_name
from cli_text_consts import PlatformResourcesUsersTexts as Texts
from cli_text_consts import UserDeleteCmdTexts as TextsDel
from util.spinner import spinner

logger = initialize_logger(__name__)

API_GROUP_NAME = 'aipg.intel.com'
USERS_PLURAL = 'users'
USERS_VERSION = 'v1'

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
        if user_map.get(run.submitter):
            user_map[run.submitter].experiment_runs.append(run)
        else:
            logger.error(f"Run exists for nonexisting user {run.submitter}")

    return users


def purge_user(username: str):
    """
    Removes all system's artifacts that belong to a removed user.
    K8s objects are removed during removal of a namespace.
    :param username: name of a user for which artifacts should be removed
    It throws exception in case of any problems detected during removal of a user
    """
    # remove data from elasticsearch
    try:
        with k8s_proxy_context_manager.K8sProxy(NAUTAAppNames.ELASTICSEARCH) as proxy,\
            spinner(text=TextsDel.DELETION_DELETING_USERS_EXPERIMENTS):
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            es_client.delete_logs_for_namespace(username)
    except K8sProxyCloseError as exe:
        logger.exception("Error during closing of a proxy for elasticsearch.")
        raise exe
    except Exception as exe:
        logger.exception("Error during removal of data from elasticsearch")
        raise exe


def get_user_data(username: str) -> model.User:
    """
    Return users data.
    :param username: name of a user
    :return: User object with users data. If user doesn't exist - it returns None
    In case of any problems during gathering users data it throws an exception
    """
    try:
        config.load_kube_config()
        api = client.CustomObjectsApi(client.ApiClient())

        user_data = api.get_cluster_custom_object(group=API_GROUP_NAME, version=USERS_VERSION,
                                                 plural=USERS_PLURAL, name=username)
    except ApiException as exe:
        if exe.status == 404:
            logger.debug(f"User {username} not found")
            return None
        raise exe

    return User.from_k8s_response_dict(user_data)


def validate_user_name(username: str) -> bool:
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
    user = get_user_data(username)
    if user and model.UserStatus.CREATED == user.state:
        return True

    for i in range(timeout):
        time.sleep(1)
        user = get_user_data(username)
        logger.debug(f"Users state : {user.state}")
        if user and model.UserStatus.CREATED == user.state:
            return True

    return False
