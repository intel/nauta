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
from typing import Dict, List, Optional
import re
import sre_constants
import time
from pathlib import Path
import random

from kubernetes import config, client
from kubernetes.client.rest import ApiException

import platform_resources.experiment_model as model
from platform_resources.run_model import RunKinds
from platform_resources.platform_resource_model import KubernetesObject
from platform_resources.resource_filters import filter_by_name_regex, filter_by_state, filter_by_run_kinds
from util.exceptions import InvalidRegularExpressionError, SubmitExperimentError
from util.logger import initialize_logger
from cli_text_consts import PLATFORM_RESOURCES_EXPERIMENTS_TEXTS as TEXTS
from platform_resources.runs import list_runs


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aipg.intel.com'
EXPERIMENTS_PLURAL = 'experiments'
EXPERIMENTS_VERSION = 'v1'


def get_experiment(name: str, namespace: str = None) -> Optional[model.Experiment]:
    """
    Return Experiment of given name. If Experiment is not found, function returns None.
    :param namespace: If provided, only experiments from this namespace will be returned
    :return: Experiment object or None
    """
    logger.debug(f'Getting experiment {name}.')

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    try:
        if namespace:
            raw_experiment = api.get_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                              plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION,
                                                              name=name)
        else:
            raw_experiment = api.get_cluster_custom_object(group=API_GROUP_NAME, plural=EXPERIMENTS_PLURAL,
                                                           version=EXPERIMENTS_VERSION, name=name)
    except ApiException as e:
        logger.exception(f"Failed to find experiment {name}.")
        if e.status == 404:
            raw_experiment = None
        else:
            raise

    return model.Experiment.from_k8s_response_dict(raw_experiment) if raw_experiment else None


def list_experiments(namespace: str = None,
                     state: model.ExperimentStatus = None,
                     run_kinds_filter : List[RunKinds] = None,
                     name_filter: str = None) -> List[model.Experiment]:
    """
    Return list of experiments.
    :param namespace: If provided, only experiments from this namespace will be returned
    :param state: If provided, only experiments with given state will be returned
    :param name_filter: If provided, only experiments matching name_filter regular expression will be returned
    :param run_kinds_filter: If provided, only experiments with a kind that matches to any of the run kinds from given
        filtering list will be returned
    :return: List of Experiment objects
    """
    logger.debug('Listing experiments.')
    raw_experiments = list_raw_experiments(namespace)
    try:
        name_regex = re.compile(name_filter) if name_filter else None
    except sre_constants.error as e:
        error_msg = TEXTS["regex_compilation_fail_msg"].format(name_filter=name_filter)
        logger.exception(error_msg)
        raise InvalidRegularExpressionError(error_msg) from e

    experiment_filters = [partial(filter_by_name_regex, name_regex=name_regex),
                          partial(filter_by_state, state=state),
                          partial(filter_by_run_kinds, run_kinds=run_kinds_filter)]

    experiments = [model.Experiment.from_k8s_response_dict(experiment_dict)
                   for experiment_dict in raw_experiments['items']
                   if all(f(experiment_dict) for f in experiment_filters)]

    return experiments


def list_k8s_experiments_by_label(namespace: str = None, label_selector: str = "") -> List[KubernetesObject]:
    """
    Return list of Kubernetes Experiments filtered [optionally] by labels
    :param namespace: If provided, only experiments from this namespace will be returned
    :param str label_selector: A selector to restrict the list of returned objects by their labels. Defaults to everything.
    :return: List of Experiment objects
    """
    raw_experiments = list_raw_experiments(namespace, label_selector)
    schema = model.ExperimentKubernetesSchema()
    body, err = schema.load(raw_experiments['items'], many=True)
    if err:
        raise RuntimeError(TEXTS["k8s_response_load_error_msg"].format(err=err))
    return body


def list_raw_experiments(namespace: str = None, label_selector: str = "") -> object:
    """
    Return raw list of experiments.
    :param namespace: If provided, only experiments from this namespace will be returned
    :param str label_selector: A selector to restrict the list of returned objects by their labels. Defaults to everything.
    :return: object
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    if namespace:
        raw_experiments = api.list_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                            plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION,
                                                            label_selector=label_selector)
    else:
        raw_experiments = api.list_cluster_custom_object(group=API_GROUP_NAME, plural=EXPERIMENTS_PLURAL,
                                                         version=EXPERIMENTS_VERSION, label_selector=label_selector)
    return raw_experiments


def add_experiment(exp: model.Experiment, namespace: str, labels: Dict[str, str] = None) -> KubernetesObject:
    """
    Add a new Experiment resource object to the platform
    :param labels: additional labels
    :param exp model to save
    :param namespace where Experiment will be saved
    :return: Kubernetes response object
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())

    # exclude labels with None values - labels won't be correctly added otherwise
    labels = {key: value for key, value in labels.items() if value} if labels else None

    exp_kubernetes = KubernetesObject(exp, client.V1ObjectMeta(name=exp.name, namespace=namespace, labels=labels),
                                      kind="Experiment", apiVersion=f"{API_GROUP_NAME}/{EXPERIMENTS_VERSION}")
    schema = model.ExperimentKubernetesSchema()
    body, err = schema.dump(exp_kubernetes)
    if err:
        raise RuntimeError(TEXTS["k8s_dump_preparation_error_msg"].format(err=err))

    raw_exp = api.create_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace, body=body,
                                                  plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION)

    response, err = schema.load(raw_exp)
    if err:
        raise RuntimeError(TEXTS["k8s_response_load_error_msg"].format(err=err))

    return response


def generate_exp_name_and_labels(script_name: str, namespace: str, name: str = None,
                                 run_kind: RunKinds = RunKinds.TRAINING) -> (str, Dict[str, str]):
    if script_name:
        script_name = Path(script_name).name

    if name:
        # CASE 1: If user pass name as param, then use it. If experiment with this name exists - return error
        experiment = get_experiment(namespace=namespace, name=name)
        experiment_runs = experiment.get_runs() if experiment else []
        if experiment and experiment_runs:
            raise SubmitExperimentError(TEXTS["experiment_already_exists_error_msg"].format(name=name))
        # subcase when experiment has no associated runs.
        if experiment and not experiment_runs:
            raise SubmitExperimentError(TEXTS["experiment_invalid_state_msg"].format(name=name))
        return name, prepare_label(script_name, name, name, run_kind=run_kind)
    else:
        # CASE 2: If user submit exp without name, but there is already exp with the same script name, then:
        # --> use existing exp name and add post-fix with next index
        generated_name, labels = generate_name_for_existing_exps(script_name, namespace, run_kind=run_kind)
        if generated_name:
            return generated_name, labels

        # CASE 3: If user submit exp without name and there is no existing exps with matching script name,then:
        # --> generate new name

        result = generate_name(script_name)

        experiments = list_experiments(namespace=namespace, name_filter=result)
        if experiments and len(experiments) > 0:
            result = f'{result}-{len(experiments)}'
            return result, prepare_label(script_name, result, run_kind=run_kind)
        return result, prepare_label(script_name, result, run_kind=run_kind)


def generate_name(name: str, prefix='exp') -> str:
    # tf-operator requires that {user}-{tfjob's name} is no longer than 63 chars, so we need to limit script name,
    # so user cannot pass script name with any number of chars
    name = name if re.match('^[a-z]+', name) else f'{prefix}-{name}'
    formatter = re.compile(r'[^a-z0-9-]')
    normalized_script_name = name.lower().replace('_', '-').replace('.', '-')[:10]
    formatted_name = formatter.sub('', normalized_script_name)
    return f'{formatted_name}-{str(random.randrange(1,999)).zfill(3)}-' \
           f'{time.strftime("%y-%m-%d-%H-%M-%S", time.localtime())}'


def prepare_label(script_name, calculated_name: str, name: str=None,
                  run_kind: RunKinds = RunKinds.TRAINING) -> Dict[str, str]:
    labels = {
        "script_name": script_name,
        "calculated_name": calculated_name,
        "runKind": run_kind.value
    }
    if name:
        labels['name_origin'] = name
    return labels


def generate_name_for_existing_exps(script_name: str, namespace: str,
                                    run_kind: RunKinds = RunKinds.TRAINING) -> (str or None, Dict[str, str]):
    exp_list = list_k8s_experiments_by_label(namespace=namespace,
                                             label_selector=f"script_name={script_name},name_origin")
    if not exp_list or len(exp_list) == 0:
        return None, {}

    # 1. Find newest experiment name
    newest_exp = None
    for exp in exp_list:
        if not newest_exp:
            newest_exp = exp
        elif exp.metadata.creation_timestamp > newest_exp.metadata.creation_timestamp:
            newest_exp = exp
    name_origin = newest_exp.metadata.labels['name_origin']

    names_of_experiments_with_the_same_origin = []
    for exp in exp_list:
        if exp.metadata.labels['name_origin'] == name_origin:
            names_of_experiments_with_the_same_origin.append(exp.metadata.name)

    # 2. Count experiments(runs) matching the same origin name of an experiment
    runs_of_exp_list = list_runs(namespace=namespace, exp_name_filter=names_of_experiments_with_the_same_origin)

    counter = 1
    if runs_of_exp_list:
        counter = len(runs_of_exp_list) + 1

    calculated_name = f"{name_origin}-{counter}"
    return calculated_name, prepare_label(script_name, calculated_name, name_origin, run_kind=run_kind)


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
        raise RuntimeError(TEXTS["k8s_dump_preparation_error_msg"].format(err=err))

    try:
        raw_exp = api.patch_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                     body=body, plural=EXPERIMENTS_PLURAL,
                                                     version=EXPERIMENTS_VERSION, name=experiment.name)
        logger.debug(f'Experiment patch response : {raw_exp}')
    except ApiException as exe:
        err_message = TEXTS["experiment_update_error_msg"]
        logger.exception(err_message)
        raise RuntimeError(err_message) from exe


def delete_experiment(experiment: model.Experiment, namespace: str):
    logger.debug(f'Deleting experiment {experiment.name}.')

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    try:
        api.delete_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                            plural=EXPERIMENTS_PLURAL, version=EXPERIMENTS_VERSION,
                                            name=experiment.name, body={})
    except ApiException:
        logger.exception(f"Failed to delete experiment {experiment.name}.")
        raise
