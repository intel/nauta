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

from enum import Enum
from typing import List, Tuple

from platform_resources.run import Run
from commands.experiment.common import submit_experiment, RunKinds
from util.k8s.k8s_info import get_kubectl_host, get_kubectl_current_context_namespace

INFERENCE_TEMPLATE = 'tf-inference-stream'
INFERENCE_INSTANCE_PREFIX = 'pred'


class InferenceRuntime(Enum):
    TFSERVING = 'tfserving'
    OVMS = 'ovms'


class InferenceVerb(Enum):
    CLASSIFY = 'classify'
    REGRESS = 'regress'
    PREDICT = 'predict'


def start_inference_instance(name: str,
                             model_location: str,
                             model_name: str,
                             template: str,
                             local_model_location: str = None,
                             data_location: str = None,
                             output_location: str = None,
                             env_variables: List[str] = None,
                             tf_record: bool = False,
                             pack_params: List[Tuple[str, str]] = None,
                             requirements: str = None) -> Run:

    if pack_params is None:
        pack_params = []
    else:
        pack_params = list(pack_params)

    pack_params.append(('modelName', model_name))

    if model_location:
        pack_params.append(('modelPath', model_location))
    elif local_model_location:
        pack_params.append(('modelPath', '/app'))
    if data_location:
        pack_params.append(('dataPath', data_location))
    if output_location:
        pack_params.append(('outputPath', output_location))
    if tf_record:
        pack_params.append(('inputFormat', 'tf-record'))

    runs, _, _ = submit_experiment(run_kind=RunKinds.INFERENCE, name=name, template=template, pack_params=pack_params,
                                   script_folder_location=local_model_location, env_variables=env_variables,
                                   requirements_file=requirements)
    return runs[0]


def get_inference_instance_url(inference_instance: Run, model_name: str = None) -> str:
    """
    Get URL to inference instance.
    """
    service_name = inference_instance.name
    model_name = model_name if model_name else inference_instance.metadata['annotations']['modelName']
    k8s_host = get_kubectl_host(replace_https=False)
    k8s_namespace = get_kubectl_current_context_namespace()

    proxy_url = f'{k8s_host}/api/v1/namespaces/{k8s_namespace}/' \
                f'services/{service_name}:rest-port/proxy/v1/models/{model_name}'

    return proxy_url
