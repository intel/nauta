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

import base64
import os
from sys import exit
import time
from typing import Tuple, List


import click
from kubernetes.client import V1Pod
from tabulate import tabulate

from commands.predict.common import start_inference_instance, get_inference_instance_url, INFERENCE_INSTANCE_PREFIX, \
    InferenceRuntime
from commands.experiment.common import validate_experiment_name, validate_pack_params_names
from platform_resources.experiment_utils import generate_name
from util.cli_state import common_options, pass_state, State
from platform_resources.run import RunStatus
from util.aliascmd import AliasCmd
from util.config import TBLT_TABLE_FORMAT
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import PredictLaunchCmdTexts as Texts
from util.k8s.k8s_info import get_secret, get_kubectl_current_context_namespace, get_service_account, \
    get_namespaced_pods


INFERENCE_TEMPLATE_TFSERVING = 'tf-inference-stream'
INFERENCE_TEMPLATE_OVMS = 'ovms-inference-stream'

logger = initialize_logger(__name__)


def validate_local_model_location(local_model_location: str):
    if not os.path.isdir(local_model_location):
        handle_error(
            user_msg=Texts.MODEL_DIR_NOT_FOUND_ERROR_MSG.format(local_model_location=local_model_location)
        )
        exit(2)


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='l', options_metavar='[options]')
@click.option('-n', '--name', default=None, help=Texts.HELP_N, callback=validate_experiment_name)
@click.option('-m', '--model-location', help=Texts.HELP_M)
@click.option("-l", "--local-model-location", type=click.Path(exists=True), help=Texts.HELP_LOCAL_MODEL_LOCATION)
@click.option('-mn', '--model-name', help=Texts.HELP_MODEL_NAME)
@click.option("-p", "--pack-param", type=(str, str), multiple=True, help=Texts.HELP_P,
              callback=validate_pack_params_names)
@click.option("-r", "--requirements", type=click.Path(exists=True, dir_okay=False), required=False, help=Texts.HELP_R)
@click.option('-rt', '--runtime', required=False, type=click.Choice([runtime.value for runtime in InferenceRuntime]),
              default=InferenceRuntime.TFSERVING.value, help=Texts.HELP_RT)
@common_options(admin_command=False)
@pass_state
def launch(state: State, name: str, model_location: str, local_model_location: str, model_name: str,
           pack_param: List[Tuple[str, str]], requirements: str, runtime: InferenceRuntime):
    """
    Starts a new prediction instance that can be used for performing prediction, classification and
    regression tasks on trained model.
    """
    if not model_location and not local_model_location:
        handle_error(
            user_msg=Texts.MISSING_MODEL_LOCATION_ERROR_MSG.format(local_model_location=local_model_location)
        )
        exit(1)

    if local_model_location:
        validate_local_model_location(local_model_location)

    click.echo('Submitting prediction instance.')
    try:
        template = INFERENCE_TEMPLATE_OVMS if InferenceRuntime(runtime) == InferenceRuntime.OVMS else \
            INFERENCE_TEMPLATE_TFSERVING
        model_path = model_location.rstrip('/') if model_location else local_model_location.rstrip('/')
        model_name = model_name if model_name else os.path.basename(model_path)
        name = name if name else generate_name(name=model_name, prefix=INFERENCE_INSTANCE_PREFIX)
        inference_instance = start_inference_instance(name=name, model_location=model_location, model_name=model_name,
                                                      local_model_location=local_model_location, template=template,
                                                      requirements=requirements, pack_params=pack_param)
        if inference_instance.state == RunStatus.FAILED:
            raise RuntimeError('Inference instance submission failed.')
    except Exception:
        handle_error(logger, Texts.INSTANCE_START_ERROR_MSG, Texts.INSTANCE_START_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo(tabulate([[inference_instance.cli_representation.name, model_location,
                          inference_instance.cli_representation.status]],
                        headers=Texts.TABLE_HEADERS,
                        tablefmt=TBLT_TABLE_FORMAT))

    try:
        namespace = get_kubectl_current_context_namespace()
        authorization_header = get_authorization_header(service_account_name=name, namespace=namespace)
        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance,
                                                            model_name=model_name)
        click.echo(Texts.INSTANCE_INFO_MSG.format(inference_instance_url=inference_instance_url,
                                                  authorization_header=authorization_header))
    except Exception:
        handle_error(logger, Texts.INSTANCE_URL_ERROR_MSG, Texts.INSTANCE_URL_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    # wait till pod is ready - no more than 40 seconds
    for i in range(40):
        pods = get_namespaced_pods(label_selector=f'runName={name}', namespace=namespace)
        if pods:
            for pod in pods:
                if not check_pod_readiness(pod):
                    break
            else:
                break
            time.sleep(1)
    else:
        handle_error(logger, Texts.PREDICTION_INSTANCE_NOT_READY, Texts.PREDICTION_INSTANCE_NOT_READY,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)


def get_authorization_header(service_account_name: str, namespace: str):
    service_account = get_service_account(service_account_name=service_account_name, namespace=namespace)
    secret_name = service_account.secrets[0].name
    authorization_token = get_secret(secret_name=secret_name, namespace=namespace).data['token']
    authorization_token = base64.b64decode(authorization_token).decode('utf-8')
    return f'Authorization: Bearer {authorization_token}'


def check_pod_readiness(pod: V1Pod):
    container_statuses_list = pod.status.container_statuses
    if container_statuses_list:
        for status in container_statuses_list:
            if not status.ready:
                break
        else:
            return True
    return False
