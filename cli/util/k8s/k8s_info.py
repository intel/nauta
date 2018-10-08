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
from kubernetes.client import configuration, V1DeleteOptions, V1Secret, V1ServiceAccount
from util.logger import initialize_logger
from util.exceptions import KubernetesError
from util.app_names import DLS4EAppNames
from cli_text_consts import UtilK8sInfoTexts as Texts

logger = initialize_logger('util.kubectl')

PREFIX_VALUES = {"E": 10 ** 18, "P": 10 ** 15, "T": 10 ** 12, "G": 10 ** 9, "M": 10 ** 6, "K": 10 ** 3}
PREFIX_I_VALUES = {"Ei": 2 ** 60, "Pi": 2 ** 50, "Ti": 2 ** 40, "Gi": 2 ** 30, "Mi": 2 ** 20, "Ki": 2 ** 10}


class PodStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def all_members(cls):
        return str([e.value for e in cls])


class NamespaceStatus(Enum):
    ACTIVE = 'Active'
    TERMINATING = 'Terminating'
    NOT_EXISTS = 'Not_Exists'


def get_kubectl_host(replace_https=True, with_port=True) -> str:
    config.load_kube_config()
    kubectl_host = configuration.Configuration().host
    if replace_https:
        kubectl_host = kubectl_host.replace('https://', '').replace('http://', '')
    if not with_port:
        kubectl_host = kubectl_host.split(':')[0]

    return kubectl_host


def get_api_key() -> str:
    config.load_kube_config()
    return configuration.Configuration().api_key.get('authorization')


def get_kubectl_current_context_namespace() -> str:
    config.load_kube_config()
    context_list, current_context = config.list_kube_config_contexts()
    return current_context['context']['namespace']


def get_k8s_api() -> client.CoreV1Api:
    config.load_kube_config()
    return client.CoreV1Api(client.ApiClient())


def get_service_account(service_account_name: str, namespace: str) -> V1ServiceAccount:
    api = get_k8s_api()
    return api.read_namespaced_service_account(name=service_account_name, namespace=namespace)


def get_secret(secret_name: str, namespace: str) -> V1Secret:
    api = get_k8s_api()
    return api.read_namespaced_secret(name=secret_name, namespace=namespace)


def get_pod_status(pod_name: str, namespace: str) -> PodStatus:
    api = get_k8s_api()
    return PodStatus(api.read_namespaced_pod(name=pod_name, namespace=namespace).status.phase.upper())


def check_pods_status(run_name: str, namespace: str, status: PodStatus, app_name: DLS4EAppNames = None) -> bool:
    """
    Returns true if all pods related to a given run have given status.
    :param run_name: name of a run - obligatory
    :param namespace: namespace where run is located - obligatory
    :param status: status which will be compared with pods' statuses
    :param app_name: name of an app - if None - pods are not limited to any application
    :return: True if all pods related to <run_name> have <status> status. False otherwise
    """
    api = get_k8s_api()

    label_selector = f"runName={run_name}"
    if app_name:
        label_selector = label_selector + f",app={app_name}"

    pods_list = api.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

    if not pods_list:
        return False

    for pod in pods_list.items:
        if PodStatus(pod.status.phase.upper()) != status:
            return False

    return True


def get_pods(label_selector: str) -> List[client.V1Pod]:
    logger.debug(f'Getting pods with label selector: {label_selector}')
    api = get_k8s_api()

    pods = []
    try:
        if label_selector:
            pods_response = api.list_pod_for_all_namespaces(watch=False, label_selector=label_selector)
        else:
            pods_response = api.list_pod_for_all_namespaces(watch=False)
        pods = pods_response.items
    except ApiException as e:
        logger.exception(f'Failed to find pods with label selector: {label_selector}')
        if e.status != 404:
            raise

    return pods


def get_namespaced_pods(label_selector: str, namespace: str) -> List[client.V1Pod]:
    logger.debug(f'Getting namespaced pods with label selector: {label_selector}')
    api = get_k8s_api()

    pods = []
    try:
        if label_selector:
            pods_response = api.list_namespaced_pod(watch=False, label_selector=label_selector, namespace=namespace)
        else:
            pods_response = api.list_namespaced_pod(watch=False, namespace=namespace)
        pods = pods_response.items
    except ApiException as e:
        logger.exception(f'Failed to find namespaced pods with label selector: {label_selector}')
        if e.status != 404:
            raise

    return pods


def get_app_services(dls4e_app_name: DLS4EAppNames, namespace: str = None,
                     app_name: str = None) -> List[client.V1Service]:
    api = get_k8s_api()
    selector = f'dls4e_app_name={dls4e_app_name.value}'
    field_selector = ""
    if app_name:
        field_selector = f'metadata.name={app_name}'

    if namespace:
        return api.list_namespaced_service(namespace=namespace, label_selector=selector,
                                           field_selector=field_selector).items
    else:
        return api.list_service_for_all_namespaces(label_selector=selector, field_selector=field_selector).items


def get_app_service_node_port(dls4e_app_name: DLS4EAppNames, namespace: str = None, app_name: str = None) -> int:
    services = get_app_services(dls4e_app_name=dls4e_app_name, namespace=namespace, app_name=app_name)
    return services[0].spec.ports[0].node_port


def find_namespace(namespace: str) -> NamespaceStatus:
    """
    Checks whether a namespace with a given name exists

    :param namespace: name of a namespace to be found
    :return: value from the NamespaceStatus enum
    """
    api = get_k8s_api()
    try:
        namespace_def = api.read_namespace(namespace)

        if namespace_def and namespace_def.metadata and namespace_def.metadata.name == namespace:
            return NamespaceStatus(namespace_def.status.phase)
    except ApiException as e:
        if e.status == 404:
            return NamespaceStatus.NOT_EXISTS
        else:
            error_message = Texts.OTHER_FIND_NAMESPACE_ERROR
            logger.exception(error_message)
            raise KubernetesError(error_message)

    return NamespaceStatus.NOT_EXISTS


def delete_namespace(namespace: str, propagate: bool = False):
    """
    Removes a namespace with the given name

    :param namespace: namespace to be deleted
    :param propagate: If True - all objects in a namespace will be deleted
    In case of any problems (i.e. lack of privileges) it throws an exception
    """
    try:
        api = get_k8s_api()
        propagation_policy = "Orphan"
        if propagate:
            propagation_policy = "Foreground"
        body = V1DeleteOptions(propagation_policy=propagation_policy)

        response = api.delete_namespace(namespace, body)

        if response.status != "{'phase': 'Terminating'}":
            error_description = Texts.NAMESPACE_DELETE_ERROR_MSG.format(namespace=namespace)
            logger.exception(error_description)
            raise KubernetesError(error_description)

    except Exception:
        error_description = Texts.NAMESPACE_DELETE_ERROR_MSG.format(namespace=namespace)
        logger.exception(error_description)
        raise KubernetesError(error_description)


def get_config_map_data(name: str, namespace: str, request_timeout: int = None) -> Dict[str, str]:
    """
    Returns a dictionary taken from data section of a config_map with a given name
    located in the given namespace.
    :param name: name of a config map
    :param namespace: name of a namespace
    :param request_timeout: optional timeout for k8s request. Defaults inside k8s_api to 120 sec.
    :return: dictonary created based on data section of a config map. In case
    of any problems it raises an Exception
    """
    try:
        api = get_k8s_api()
        ret_dict = api.read_namespaced_config_map(name, namespace, _request_timeout=request_timeout).data
    except Exception:
        error_description = Texts.CONFIG_MAP_ACCESS_ERROR_MSG.format(name=name)
        logger.exception(error_description)
        raise KubernetesError(error_description)

    return ret_dict


def get_users_token(namespace: str) -> str:
    """
    Gets a default token of a user from a given namespace

    :param namespace: namespace of a user
    :return: encoded token of a user - if it doesn't exist or errors occurred during gathering
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
                raise ValueError(Texts.LACK_OF_DEFAULT_TOKEN_ERROR_MSG)
        else:
            raise ValueError(Texts.EMPTY_LIST_OF_TOKENS_ERROR_MSG)

    except Exception as exe:
        error_message = Texts.GATHERING_USERS_TOKEN_ERROR_MSG
        logger.exception(error_message)
        raise KubernetesError(error_message) from exe

    return ret_token


def get_current_user() -> str:
    """
    Returns name of a user from a current kubectl context
    :return: name of a user
    In case of any problems - it raises an exception
    """
    return config.list_kube_config_contexts()[1]["context"]["user"]


def get_current_namespace() -> str:
    """
    Returns namespace from a current kubectl context
    :return: namespace
    In case of any problems - it raises an exception
    """
    return config.list_kube_config_contexts()[1]["context"]["namespace"]


def get_users_samba_password(username: str) -> str:
    """
    Returns samba password of a user with a given username

    :param username: name of a user
    :return: password of a user,
    In case of any problems during gathering of a password it raises KubectlIntError
    If password doesnt exist - it raises ValueError.
    """
    error_message = Texts.GATHERING_PASSWORD_ERROR_MSG
    password = None
    try:
        api = get_k8s_api()

        secret = api.read_namespaced_secret("password", username)

        password = str(base64.b64decode(secret.data["password"]), encoding="utf-8")
    except ApiException as exe:
        if exe.status == 404:
            password = None
        else:
            logger.exception(error_message)
            raise KubernetesError(error_message) from exe
    except Exception as exe:
        logger.exception(error_message)
        raise KubernetesError(error_message) from exe

    if password is None:
        raise ValueError(Texts.LACK_OF_PASSWORD_ERROR_MSG)

    return str.strip(password)


def get_cluster_roles(request_timeout: int = None) -> client.V1ClusterRoleList:
    config.load_kube_config()
    api = client.RbacAuthorizationV1Api(client.ApiClient())
    return api.list_cluster_role(_request_timeout=request_timeout)


def is_current_user_administrator(request_timeout: int = None) -> bool:
    """
    Function checks whether a current user is a k8s administrator

    :param request_timeout: optional timeout for k8s request. Defaults to 120 sec inside k8s api.
    :return: True if a user is a k8s administrator, False otherwise
    In case of any errors - raises an exception
    """
    # regular users shouldn't have access to cluster roles
    try:
        get_cluster_roles(request_timeout=request_timeout)
    except ApiException as exe:
        # 403 - forbidden
        if exe.status == 403:
            return False
        else:
            raise exe

    return True


def sum_cpu_resources_unformatted(cpu_resources: List[str]):
    """ Sum cpu resources given in k8s format and return the sum in the same format. """
    cpu_sum = 0
    for cpu_resource in cpu_resources:
        if not cpu_resource:
            continue
        # If CPU resources are gives as for example 100m, we simply strip last character and sum leftover numbers.
        elif cpu_resource[-1] == "m":
            cpu_sum += int(cpu_resource[:-1])
        # Else we assume that cpu resources are given as float value of normal CPUs instead of miliCPUs.
        else:
            cpu_sum += int(float(cpu_resource) * 1000)

    return cpu_sum


def format_cpu_resources(sum: int):
    return str(sum) + "m"


def sum_cpu_resources(cpu_resources: List[str]):
    return format_cpu_resources(sum_cpu_resources_unformatted(cpu_resources))


def sum_mem_resources_unformatted(mem_resources: List[str]):
    """
    Sum memory resources given in k8s format and return the sum as a number.
    """
    mem_sum = 0

    for mem_resource in mem_resources:
        if not mem_resource:
            continue
        # If last character is "i" then assume that resource is given as for example 1000Ki.
        elif mem_resource[-1] == "i" and mem_resource[-2:] in PREFIX_I_VALUES:
            prefix = mem_resource[-2:]
            mem_sum += int(mem_resource[:-2]) * PREFIX_I_VALUES[prefix]
        # If last character is one of the normal exponent prefixes (with base 10) then assume that resource is given
        # as for example 1000K.
        elif mem_resource[-1] in PREFIX_VALUES:
            prefix = mem_resource[-1]
            mem_sum += int(mem_resource[:-1]) * PREFIX_VALUES[prefix]
        # If there is e contained inside resource string then assume that it is given in exponential format.
        elif "e" in mem_resource:
            mem_sum += int(float(mem_resource))
        else:
            mem_sum += int(mem_resource)

    return mem_sum


def format_mem_resources(sum: int):
    mem_sum_partial_strs = []
    for prefix, value in PREFIX_I_VALUES.items():
        mem_sum_partial = sum // value
        if mem_sum_partial != 0:
            mem_sum_partial_strs.append(str(mem_sum_partial) + prefix + "B")
            sum = sum % value
    if len(mem_sum_partial_strs) == 0:
        return "0KiB"
    else:
        return " ".join(mem_sum_partial_strs)


def sum_mem_resources(mem_resources: List[str]):
    """
    Sum memory resources given in k8s format and return the sum converted to byte units with base 2 - for example KiB.
    """
    mem_sum = sum_mem_resources_unformatted(mem_resources)

    return format_mem_resources(mem_sum)


def get_pod_events(namespace: str, name: str = None):
    try:
        api = get_k8s_api()

        events_list = api.list_namespaced_event(namespace=namespace)

        return [event for event in events_list.items if name is None or event.involved_object.name == name]
    except Exception as exe:
        error_message = Texts.GATHERING_EVENTS_ERROR_MSG
        logger.exception(error_message)
        raise KubernetesError(error_message) from exe


def add_bytes_to_unit(value: str) -> str:
    """
    Method adds 'B' suffix to memory values represented in format like Gi, Mi, etc
    """
    if type(value) == str and value[-2:] in PREFIX_I_VALUES:
            value += "B"
    return value
