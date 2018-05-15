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

from collections import namedtuple
from typing import List
import re
import sre_constants

from kubernetes import config, client

import platform_resources.experiment_model as model
from util.exceptions import InvalidRegularExpressionError
from util.logger import initialize_logger


logger = initialize_logger(__name__)

API_GROUP_NAME = 'aipg.intel.com'
EXPERIMENTS_PLURAL = 'experiments'
EXPERIMENTS_VERSION = 'v1'


ExperimentShort = namedtuple('Experiment', ['name', 'parameters_spec', 'creation_timestamp', 'submitter', 'status'])


def list_experiments(namespace: str = None, state: model.ExperimentStatus=None, name_filter: str = None) -> List[ExperimentShort]:
    """
    Return list of experiments.
    :param namespace: If provided, only experiments from this namespace will be returned
    :param state: If provided, only experiments with given state will be returned
    :param name_filter: If provided, only experiments matching name_filter regular expression will be returned
    :return: List of Experiment named tuples
    """
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

    experiment_filters = [lambda experiment_dict: not state or experiment_dict['spec']['state'] == state.value,
                          lambda experiment_dict: not name_regex or name_regex.search(experiment_dict['spec']['name'])]

    experiments = [ExperimentShort(name=experiment_dict['spec']['name'],
                                   parameters_spec=experiment_dict['spec']['parameters-spec'],
                                   creation_timestamp=experiment_dict['metadata']['creationTimestamp'],
                                   submitter=experiment_dict['metadata']['namespace'],
                                   status=experiment_dict['spec']['state'])
                   for experiment_dict in raw_experiments['items']
                   if all(f(experiment_dict) for f in experiment_filters)
                   ]

    return experiments


def add_experiment(exp: model.Experiment, namespace: str) -> model.ExperimentKubernetes:
    """
    Return list of experiments.
    :param exp model to save
    :param namespace where Experiment will be saved
    :return: Kubernetes response object
    """

    config.load_kube_config()
    api = client.CustomObjectsApi(client.ApiClient())

    exp_kubernetes = model.ExperimentKubernetes(exp, client.V1ObjectMeta(name=exp.name, namespace=namespace))
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
