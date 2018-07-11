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
import re
import sre_constants
from typing import Dict, List, Optional

from kubernetes import config, client
from kubernetes.client.rest import ApiException

from platform_resources.platform_resource_model import KubernetesObject
from platform_resources.run_model import Run, RunStatus, RunKubernetesSchema
from platform_resources.resource_filters import filter_by_name_regex, filter_run_by_excl_state, \
    filter_by_experiment_name, filter_run_by_state
from util.logger import initialize_logger
from util.exceptions import InvalidRegularExpressionError


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aggregator.aipg.intel.com'
RUN_PLURAL = 'runs'
RUN_VERSION = 'v1'


def get_run(name: str, namespace: str = None) -> Optional[Run]:
    """
    Return Run of given name. If Run is not found, function returns None.
    :param namespace: If provided, only experiments from this namespace will be returned
    :return: Experiment object or None
    """
    logger.debug(f'Getting run {name}.')

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    try:
        if namespace:
            raw_run = api.get_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                              plural=RUN_PLURAL, version=RUN_VERSION,
                                                              name=name)
        else:
            raw_run = api.get_cluster_custom_object(group=API_GROUP_NAME, plural=RUN_PLURAL,
                                                           version=RUN_VERSION, name=name)
    except ApiException as e:
        logger.exception(f'Failed to find run {name}.')
        if e.status == 404:
            raw_run = None
        else:
            raise

    return Run.from_k8s_response_dict(raw_run) if raw_run else None


def list_runs(namespace: str = None, state: RunStatus = None, name_filter: str = None, exp_name_filter: str = None,
              excl_state: RunStatus = None) -> List[Run]:
    """
    Return list of experiment runs.
    :param namespace: If provided, only runs from this namespace will be returned
    :param state: If provided, only runs with given state will be returned
    :param name_filter: If provided, only runs matching name_filter regular expression will be returned
    :param exp_name_filter: If provided, list of runs is filtered by experiment name
    :param excl_state: If provided, only runs with a state other than given will be returned
    :return: List of Run objects
    In case of problems during getting a list of runs - throws an error
    """
    logger.debug('Listing runs.')
    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())
    if namespace:
        raw_runs = api.list_namespaced_custom_object(group=API_GROUP_NAME, namespace=namespace,
                                                            plural=RUN_PLURAL, version=RUN_VERSION)
    else:
        raw_runs = api.list_cluster_custom_object(group=API_GROUP_NAME, plural=RUN_PLURAL, version=RUN_VERSION)

    try:
        name_regex = re.compile(name_filter) if name_filter else None
    except sre_constants.error as e:
        error_msg = f'Failed to compile regular expresssion: {name_filter}'
        logger.exception(error_msg)
        raise InvalidRegularExpressionError(error_msg) from e

    run_filters = [partial(filter_by_name_regex, name_regex=name_regex, spec_location=False),
                   partial(filter_run_by_state, state=state),
                   partial(filter_run_by_excl_state, state=excl_state),
                   partial(filter_by_experiment_name, exp_name=exp_name_filter)]

    runs = [Run.from_k8s_response_dict(run_dict)
            for run_dict in raw_runs['items']
            if all(f(run_dict) for f in run_filters)]

    return runs


def update_run(run: Run, namespace: str) -> (KubernetesObject, Run):
    """
    Updates a Run object given as a parameter.
    :param run model to update
    :param namespace where Run will be updated
    :return: in case of any problems during update it throws an exception
    """
    run_kubernetes = KubernetesObject(run, client.V1ObjectMeta(name=run.name, namespace=namespace),
                                            kind="Run", apiVersion=f"{API_GROUP_NAME}/{RUN_VERSION}")
    schema = RunKubernetesSchema()
    body, err = schema.dump(run_kubernetes)
    if err:
        raise RuntimeError(f'preparing dump of RunKubernetes request object error - {err}')
    return _update(run.name, namespace, body)


def patch_run(name: str, namespace: str, metrics: Dict[str,str]) -> (KubernetesObject, Run):
    """
    Patch a Run object for a given data
    :param name run name to update
    :param namespace where Run will be updated
    :param metrics dict to be merged into Run object
    :return: in case of any problems during update it throws an exception
    """
    body = {
        "spec": {
            "metrics": metrics
        }
    }
    return _update(name, namespace, body)


def _update(name: str, namespace: str, body: object) -> (KubernetesObject, Run):
    """
    Patch a Run object for a given data
    :param name run name to update
    :param namespace where Run will be updated
    :param body: patch object to apply
    :return: in case of any problems during update it throws an exception
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())

    try:
        raw_run = api.patch_namespaced_custom_object(group='aggregator.aipg.intel.com', namespace=namespace, body=body,
                                                     plural=RUN_PLURAL, version=RUN_VERSION, name=name)
        schema = RunKubernetesSchema()
        run, err = schema.load(raw_run)
        if err:
            raise RuntimeError(f'preparing load of RunKubernetes update response object error - {err}')
        logger.debug(f"Run patch response : {raw_run}")
        return run, Run.from_k8s_response_dict(raw_run)
    except ApiException as exe:
        err_message = "Error during patching a Run"
        logger.exception(err_message)
        raise RuntimeError(err_message) from exe
