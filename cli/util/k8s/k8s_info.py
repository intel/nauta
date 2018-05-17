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

import base64

from enum import Enum
from typing import List, Dict
from kubernetes.client.rest import ApiException
from kubernetes import config, client
from kubernetes.client import configuration, V1DeleteOptions
from util.logger import initialize_logger
from util.exceptions import KubectlIntError

logger = initialize_logger('util.kubectl')


class PodStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    UNKNOWN = 'UNKNOWN'


def get_kubectl_host() -> str:
    config.load_kube_config()
    return configuration.Configuration().host.replace('https://', '').replace('http://', '').split(':')[0]


def get_kubectl_port() -> int:
    config.load_kube_config()
    try:
        port = int(configuration.Configuration().host.split(':')[-1])
    except ValueError:
        port = 443

    return port


def get_kubectl_current_context_namespace() -> str:
    config.load_kube_config()
    context_list, current_context = config.list_kube_config_contexts()
    return current_context['context']['namespace']


def get_k8s_api() -> client.CoreV1Api:
    config.load_kube_config()
    return client.CoreV1Api(client.ApiClient())


def get_pod_status(pod_name: str, namespace: str) -> PodStatus:
    api = get_k8s_api()
    return PodStatus(api.read_namespaced_pod(name=pod_name, namespace=namespace).status.phase.upper())


def get_app_services(app_name: str) -> List[client.V1Service]:
    api = get_k8s_api()
    return api.list_service_for_all_namespaces(label_selector='dls4e_app_name={}'.format(app_name)).items


def get_app_namespace(app_name: str) -> str:
    namespace = ""

    app_services = get_app_services(app_name)

    if app_services:
        namespace = app_services[0].metadata.namespace

    return namespace


def find_namespace(namespace: str) -> bool:
    """
    Checks whether a namespace with a given name exists

    :param namespace: name of a namespace to be found
    :return: True if a namespace with a given name exists
    """
    api = get_k8s_api()
    try:
        namespace_def = api.read_namespace(namespace)

        return namespace_def and namespace_def.metadata and namespace_def.metadata.name == namespace
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            error_message = "find_namespace error"
            logger.exception(error_message)
            raise KubectlIntError(error_message)


def delete_namespace(namespace: str):
    """
    Removes a namespace with the given name

    :param namespace: namespace to be deleted
    """
    try:
        api = get_k8s_api()
        body = V1DeleteOptions()

        api.delete_namespace(namespace, body)
    except Exception:
        error_description = f"Error during deleting namespace {namespace}"
        logger.exception(error_description)
        raise KubectlIntError(error_description)


def get_config_map_data(name: str, namespace: str) -> Dict[str, str]:
    """
    Returns a dictionary taken from data section of a config_map with a given name
    located in the given namespace.
    :param name: name of a config map
    :param namespace: name of a namespace
    :return: dictonary created based on data section of a config map. In case
    of any problems it raises an Exception
    """
    try:
        api = get_k8s_api()
        ret_dict = api.read_namespaced_config_map(name, namespace).data
    except Exception:
        error_description = f"Problem during accessing ConfigMap : {name}."
        logger.exception(error_description)
        raise KubectlIntError(error_description)

    return ret_dict


def get_users_token(namespace: str) -> str:
    """
    Gets a default token of a user from a given namespace

    :param namespace: namespace of a user
    :return: encoded token of a user - if it doesn't exist or errors occured during gathering
    the token - function returns an empty string
    """
    ret_token = ""
    try:
        api = get_k8s_api()
        tokens_list = api.list_namespaced_secret(namespace)

        if tokens_list:
            for token in tokens_list.items:
                if "default-token" in token.metadata.name:
                    ret_token = str(base64.b64decode(token.data.get("token")), encoding="utf-8")
                    break
            else:
                raise ValueError("Lack of default-token on a list of tokens.")
        else:
            raise ValueError("Empty list of tokens.")

    except Exception as exe:
        error_message = "Problem during gathering users token."
        logger.exception(error_message)
        raise KubectlIntError(error_message) from exe

    return ret_token
