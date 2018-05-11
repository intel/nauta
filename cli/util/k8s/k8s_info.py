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

from enum import Enum
from kubernetes import config, client
from kubernetes.client import configuration


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


def get_pod_status(pod_name: str, namespace: str) -> PodStatus:
    config.load_kube_config()
    api = client.CoreV1Api(client.ApiClient())
    return PodStatus(api.read_namespaced_pod(name=pod_name, namespace=namespace).status.phase.upper())


def get_app_services(app_name: str) -> list:
    config.load_kube_config()
    api = client.CoreV1Api(client.ApiClient())
    return api.list_service_for_all_namespaces(label_selector='dls4e_app_name={}'.format(app_name)).items


def get_app_namespace(app_name: str) -> str:
    namespace = ""

    app_services = get_app_services(app_name)

    if app_services:
        namespace = app_services[0].metadata.namespace

    return namespace
