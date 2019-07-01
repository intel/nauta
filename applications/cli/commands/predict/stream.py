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

import json
from sys import exit

import click
import requests

from util.cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_api_key
from platform_resources.run import RunStatus, Run
from commands.predict.common import get_inference_instance_url, InferenceVerb
from util.spinner import spinner
from util.system import handle_error
from cli_text_consts import PredictStreamCmdTexts as Texts

logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, cls=AliasCmd, alias='s', options_metavar='[options]')
@click.option('-n', '--name', required=True, help=Texts.HELP_N)
@click.option('-d', '--data', required=True, type=click.Path(exists=True), help=Texts.HELP_D)
@click.option('-m', '--method-verb', default=InferenceVerb.PREDICT.value,
              type=click.Choice([verb.value for verb in InferenceVerb]), help=Texts.HELP_M)
@common_options(admin_command=False)
@pass_state
def stream(state: State, name: str, data: str, method_verb: InferenceVerb):
    """
    Perform stream inference task on launched prediction instance.
    """
    method_verb = InferenceVerb(method_verb)
    try:
        namespace = get_kubectl_current_context_namespace()

        # TODO: check if kind field of inference instance Run is correct
        inference_instance = Run.get(name=name, namespace=namespace)
        if not inference_instance:
            handle_error(user_msg=Texts.INSTANCE_NOT_EXISTS_ERROR_MSG.format(name=name))
            exit(1)
        if not inference_instance.state == RunStatus.RUNNING:
            handle_error(user_msg=Texts.INSTANCE_NOT_RUNNING_ERROR_MSG
                         .format(name=name, running_code=RunStatus.RUNNING.value))
            exit(1)

        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance)
        stream_url = f'{inference_instance_url}:{method_verb.value}'
    except Exception:
        handle_error(logger, Texts.INSTANCE_GET_FAIL_ERROR_MSG.format(name=name),
                     Texts.INSTANCE_GET_FAIL_ERROR_MSG.format(name=name),
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        with open(data, 'r', encoding='utf-8') as data_file:
            stream_data = json.load(data_file)
    except (json.JSONDecodeError, IOError):
        handle_error(logger, Texts.JSON_LOAD_ERROR_MSG.format(data=data),
                     Texts.JSON_LOAD_ERROR_MSG.format(data=data))
        exit(1)

    try:
        api_key = get_api_key()
        headers = {'Authorization': api_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        with spinner(text=Texts.WAITING_FOR_RESPONSE_MSG):
            stream_response = requests.post(stream_url, data=json.dumps(stream_data),  # nosec - request to k8s cluster
                                            verify=False, headers=headers)
        stream_response.raise_for_status()
        click.echo(stream_response.text)
    except Exception as e:
        error_msg = Texts.INFERENCE_OTHER_ERROR_MSG.format(exception=e)
        if hasattr(e, 'response'):
            error_msg += Texts.INFERENCE_ERROR_RESPONSE_MSG.format(response_text=e.response.text)  # type: ignore
        handle_error(logger, error_msg, error_msg)
        exit(1)
