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

import click
import requests

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_api_key
from platform_resources.runs import get_run
from platform_resources.run_model import RunStatus
from commands.predict.common import get_inference_instance_url, InferenceVerb
from util.system import handle_error
from cli_text_consts import PREDICT_STREAM_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)


@click.command(short_help=TEXTS["help"], cls=AliasCmd, alias='s')
@click.option('-n', '--name', required=True, help=TEXTS["help_n"])
@click.option('-d', '--data', required=True, type=click.Path(exists=True), help=TEXTS["help_d"])
@click.option('-m', '--method-verb', default=InferenceVerb.PREDICT.value,
              type=click.Choice([verb.value for verb in InferenceVerb]), help=TEXTS["help_m"])
@common_options()
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
            handle_error(user_msg=TEXTS["instance_not_exists_error_msg"].format(name=name))
        if not inference_instance.state == RunStatus.RUNNING:
            handle_error(user_msg=TEXTS["instance_not_running_error_msg"]
                         .format(name=name, running_code=RunStatus.RUNNING.value))

        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance)
        stream_url = f'{inference_instance_url}:{method_verb.value}'
    except Exception:
        handle_error(logger, TEXTS["instance_get_fail_error_msg"].format(name=name),
                     TEXTS["instance_get_fail_error_msg"].format(name=name),
                     add_verbosity_msg=state.verbosity == 0)

    try:
        with open(data, 'r', encoding='utf-8') as data_file:
            stream_data = json.load(data_file)
    except (json.JSONDecodeError, IOError):
        handle_error(logger, TEXTS["json_load_error_msg"].format(data=data),
                     TEXTS["json_load_error_msg"].format(data=data))

    try:
        api_key = get_api_key()
        headers = {'Authorization': api_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        stream_response = requests.post(stream_url, data=json.dumps(stream_data), verify=False, headers=headers)
        stream_response.raise_for_status()
        click.echo(stream_response.text)
    except Exception as e:
        error_msg = TEXTS["inference_other_error_msg"].format(exception=e)
        if hasattr(e, 'response'):
            error_msg += TEXTS["inferenece_error_response_msg"].format(response_text=e.response.text)
        handle_error(logger, error_msg, error_msg)
