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
from typing import List
import re
import sre_constants
import time
from pathlib import Path

from kubernetes import config, client
from kubernetes.client.rest import ApiException

import platform_resources.experiment_model as model
from platform_resources.platform_resource_model import KubernetesObject
from platform_resources.resource_filters import filter_by_name_regex, filter_by_state
from platform_resources.custom_object_meta_model import validate_kubernetes_name
from util.exceptions import InvalidRegularExpressionError
from util.logger import initialize_logger


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aipg.intel.com'
EXPERIMENTS_PLURAL = 'experiments'
EXPERIMENTS_VERSION = 'v1'

def list_experiments(namespace: str = None,
                     state: model.ExperimentStatus=None,
                     name_filter: str = None) -> List[model.Experiment]:
    """
    Return list of experiments.
    :param namespace: If provided, only experiments from this namespace will be returned
    :param state: If provided, only experiments with given state will be returned
    :param name_filter: If provided, only experiments matching name_filter regular expression will be returned
    :return: List of Experiment objects
    """
    logger.debug('Listing experiments.')

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    if namespace:
        raw_experiments = api.list_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                            plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION)
    else:
        raw_experiments = api.list_cluster_custom_object(group=API_GROUP_NAME, plural=EXPERIMENTS_PLURAL,
                                                         version=EXPERIMENTS_VERSION)

    try:
        name_regex = re.compile(name_filter) if name_filter else None
    except sre_constants.error as e:
        error_msg = f'Failed to compile regular expresssion: {name_filter}'
        logger.exception(error_msg)
        raise InvalidRegularExpressionError(error_msg) from e

    experiment_filters = [partial(filter_by_name_regex, name_regex=name_regex),
                          partial(filter_by_state, state=state)]

    experiments = [model.Experiment.from_k8s_response_dict(experiment_dict)
                   for experiment_dict in raw_experiments['items']
                   if all(f(experiment_dict) for f in experiment_filters)]

    return experiments


def add_experiment(exp: model.Experiment, namespace: str) -> KubernetesObject:
    """
    Return list of experiments.
    :param exp model to save
    :param namespace where Experiment will be saved
    :return: Kubernetes response object
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())

    exp_kubernetes = KubernetesObject(exp, client.V1ObjectMeta(name=exp.name, namespace=namespace),
                                            kind="Experiment", apiVersion=f"{API_GROUP_NAME}/{EXPERIMENTS_VERSION}")
    schema = model.ExperimentKubernetesSchema()
    body, err = schema.dump(exp_kubernetes)
    if err:
        raise RuntimeError(f'preparing dump of ExperimentKubernetes request object error - {err}')

    raw_exp = api.create_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace, body = body,
                                                  plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION)

    response, err = schema.load(raw_exp)
    if err:
        raise RuntimeError(f'preparing load of ExperimentKubernetes response object error - {err}')

    return response


def generate_experiment_name(script_name: str, namespace: str, name: str = None, name_prefix: str = "exp") -> str:
    # TODO: CAN-310
    if script_name:
        script_name = Path(script_name).name
    if name:
        # tf-operator requires that {user}-{tfjob's name} is no longer than 63 chars, so we need to limit name passed
        # by user
        limited_name = name[:30]

        validate_kubernetes_name(limited_name)
        experiments = list_experiments(namespace=namespace, name_filter=f'^{limited_name}$')
        if experiments and len(experiments) > 0:
            return f'{limited_name}-{len(experiments)}'
        return limited_name
    else:
        # tf-operator requires that {user}-{tfjob's name} is no longer than 63 chars, so we need to limit script name,
        # so user cannot pass script name with any number of chars
        formatter = re.compile(r'[^a-z0-9-]')
        formatted_name = f"{name_prefix}"

        if script_name:
            normalized_script_name = script_name.lower().replace('_', '-').replace('.', '-')[:10]
            formatted_name = f"{formatted_name}-{normalized_script_name}"
            formatted_name = formatter.sub('', formatted_name)
        experiments = list_experiments(namespace=namespace, name_filter=formatted_name)
        result = f'{formatted_name}-{time.strftime("%y-%m-%d-%H-%M-%S", time.localtime())}'
        if experiments and len(experiments) > 0:
            return f'{result}-{len(experiments)}'
        return result


def update_experiment(experiment: model.Experiment, namespace: str) -> KubernetesObject:
    """
    Updates an Experiment object given as a parameter.
    :param experiment model to update
    :param namespace where Experiment will be updated
    :return: in case of any problems during update it throws an exception
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())

    run_kubernetes = KubernetesObject(experiment, client.V1ObjectMeta(name=experiment.name, namespace=namespace),
                                            kind="Experiment", apiVersion=f"{API_GROUP_NAME}/{EXPERIMENTS_VERSION}")
    schema = model.ExperimentKubernetesSchema()
    body, err = schema.dump(run_kubernetes)
    if err:
        raise RuntimeError(f'preparing dump of ExperimentKubernetes request object error - {err}')

    try:
        raw_exp = api.patch_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                     body = body, plural=EXPERIMENTS_PLURAL,
                                                     version=EXPERIMENTS_VERSION, name=experiment.name)
        logger.debug(f'Experiment patch response : {raw_exp}')
    except ApiException as exe:
        err_message = "Error during patching an Experiment"
        logger.exception(err_message)
        raise RuntimeError(err_message) from exe
