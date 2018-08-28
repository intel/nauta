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
from typing import Union

from platform_resources.run_model import Run
from commands.experiment.common import submit_experiment, RunSubmission, RunKinds
from util.k8s.k8s_info import get_kubectl_host, get_kubectl_current_context_namespace

INFERENCE_TEMPLATE = 'tf-inference-stream'


class InferenceVerb(Enum):
    CLASSIFY = 'classify'
    REGRESS = 'regress'
    PREDICT = 'predict'


def start_inference_instance(name: str,
                             model_location: str,
                             model_name: str,
                             template: str = INFERENCE_TEMPLATE,
                             data_location: str = None,
                             output_location: str = None) -> RunSubmission:

    pack_params = [('modelPath', model_location), ('modelName', model_name)]

    if data_location:
        pack_params.append(('dataPath', data_location))
    if output_location:
        pack_params.append(('outputPath', output_location))

    runs, _ = submit_experiment(run_kind=RunKinds.JUPYTER, name=name, template=template, pack_params=pack_params)
    return runs[0]


def get_inference_instance_url(inference_instance: Union[Run, RunSubmission], model_name: str = None) -> str:
    """
    Get URL to inference instance. If RunDescription is passed as inference_instance, model_name must be also provided.
    If Run is passed as inference_instance, model name is automatically obtained from Run metadata.
    """
    service_name = inference_instance.name
    model_name = model_name if model_name else inference_instance.metadata['labels']['modelName']
    k8s_host = get_kubectl_host(replace_https=False)
    k8s_namespace = get_kubectl_current_context_namespace()

    proxy_url = f'{k8s_host}/api/v1/namespaces/{k8s_namespace}/' \
                f'services/{service_name}/proxy/v1/models/{model_name}'

    return proxy_url
