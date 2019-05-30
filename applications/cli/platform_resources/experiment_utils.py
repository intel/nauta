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

import re
from pathlib import Path
from random import randrange
from typing import List, Dict

import time

from cli_text_consts import PlatformResourcesExperimentsTexts as Texts
from platform_resources.experiment import Experiment, ExperimentKubernetesSchema
from platform_resources.platform_resource import KubernetesObject
from platform_resources.run import RunKinds, Run
from util.exceptions import SubmitExperimentError
from util.k8s.pods import list_pods

"""
Utility functions for Experiments
"""

def list_k8s_experiments_by_label(namespace: str = None, label_selector: str = "") -> List[KubernetesObject]:
    """
    Return list of Kubernetes Experiments filtered [optionally] by labels
    :param namespace: If provided, only experiments from this namespace will be returned
    :param str label_selector: A selector to restrict the list of returned objects by their labels. Defaults to everything.
    :return: List of Experiment objects
    """
    raw_experiments = Experiment.list_raw_experiments(namespace, label_selector)
    schema = ExperimentKubernetesSchema()
    body, err = schema.load(raw_experiments['items'], many=True)
    if err:
        raise RuntimeError(Texts.K8S_RESPONSE_LOAD_ERROR_MSG.format(err=err))
    return body


def generate_exp_name_and_labels(script_name: str, namespace: str, name: str = None,
                                 run_kind: RunKinds = RunKinds.TRAINING) -> (str, Dict[str, str]):
    if script_name:
        script_name = Path(script_name).name

    if name:
        # CASE 1: If user pass name as param, then use it. If experiment with this name exists - return error
        experiment = Experiment.get(namespace=namespace, name=name)
        experiment_runs = experiment.get_runs() if experiment else []
        if experiment and experiment_runs:
            raise SubmitExperimentError(Texts.EXPERIMENT_ALREADY_EXISTS_ERROR_MSG.format(name=name))
        # subcase when experiment has no associated runs.
        if experiment and not experiment_runs:
            raise SubmitExperimentError(Texts.EXPERIMENT_INVALID_STATE_MSG.format(name=name))
        # if there are still artifacts from previous experiment with the same name
        if list_pods(namespace=namespace, label_selector=f'runName={name}'):
            raise SubmitExperimentError(Texts.EXPERIMENT_PREV_EXP_STILL_TERMINATING)
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

        experiments = Experiment.list(namespace=namespace, name_filter=result)
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
    return f'{formatted_name}-{str(randrange(1,999)).zfill(3)}-' \
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
    runs_of_exp_list = Run.list(namespace=namespace, exp_name_filter=names_of_experiments_with_the_same_origin)

    counter = 1
    if runs_of_exp_list:
        counter = len(runs_of_exp_list) + 1

    calculated_name = f"{name_origin}-{counter}"
    return calculated_name, prepare_label(script_name, calculated_name, name_origin, run_kind=run_kind)