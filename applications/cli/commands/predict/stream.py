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

import json
from sys import exit

import click
import requests

from util.cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_api_key
from platform_resources.runs import get_run
from platform_resources.run_model import RunStatus
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
        inference_instance = get_run(name=name, namespace=namespace)
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
            stream_response = requests.post(stream_url, data=json.dumps(stream_data), verify=False, headers=headers)
        stream_response.raise_for_status()
        click.echo(stream_response.text)
    except Exception as e:
        error_msg = Texts.INFERENCE_OTHER_ERROR_MSG.format(exception=e)
        if hasattr(e, 'response'):
            error_msg += Texts.INFERENCE_ERROR_RESPONSE_MSG.format(response_text=e.response.text)
        handle_error(logger, error_msg, error_msg)
        exit(1)
