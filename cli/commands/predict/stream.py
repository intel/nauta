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
import sys

import click
import requests

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_api_key
from platform_resources.runs import get_run
from platform_resources.run_model import RunStatus
from commands.predict.common import get_inference_instance_url, InferenceVerb

HELP = "Perform stream prediction task on deployed prediction instance."
HELP_N = "Name of prediction session."
HELP_D = "Path to JSON data file that will be streamed to prediction instance. " \
         "Data must be formatted such that it is compatible with the SignatureDef specified within the model " \
         "deployed in selected prediction instance."
HELP_M = "Method verb that will be used when performing inference. Predict verb is used by default."

log = initialize_logger(__name__)


@click.command(short_help=HELP, cls=AliasCmd, alias='s')
@click.option('-n', '--name', required=True, help=HELP_N)
@click.option('-d', '--data', required=True, type=click.Path(exists=True), help=HELP_D)
@click.option('-m', '--method-verb', default=InferenceVerb.PREDICT.value,
              type=click.Choice([verb.value for verb in InferenceVerb]), help=HELP_M)
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
            click.echo(f'Prediction instance {name} does not exist.')
            sys.exit(1)
        if not inference_instance.state == RunStatus.RUNNING:
            click.echo(f'Prediction instance {name} is not in {RunStatus.RUNNING.value} state.')
            sys.exit(1)

        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance)
        stream_url = f'{inference_instance_url}:{method_verb.value}'
    except Exception:
        error_msg = f'Failed to get prediction instance {name} URL.'
        log.exception(error_msg)
        sys.exit(error_msg)

    try:
        with open(data, 'r', encoding='utf-8') as data_file:
            stream_data = json.load(data_file)
    except (json.JSONDecodeError, IOError):
        error_msg = f'Failed to load {data} data file. Make sure that provided file exists and' \
                    f' is in a valid JSON format.'
        log.exception(error_msg)
        sys.exit(error_msg)

    try:
        api_key = get_api_key()
        headers = {'Authorization': api_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        stream_response = requests.post(stream_url, data=json.dumps(stream_data), verify=False, headers=headers)
        stream_response.raise_for_status()
        click.echo(stream_response.text)
    except Exception as e:
        error_msg = f'Failed to perform inference. Reason: {e}'
        if hasattr(e, 'response'):
            error_msg += f'\n Response: {e.response.text}'
        log.exception(error_msg)
        sys.exit(error_msg)
