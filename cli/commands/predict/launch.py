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

import os
import sys

import click
from tabulate import tabulate

from commands.experiment.common import validate_experiment_name
from commands.predict.common import start_inference_instance, get_inference_instance_url
from platform_resources.experiments import generate_name
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_api_key

HELP = "Starts a new prediction instance that can be used for performing prediction, classification and" \
       " regression tasks on trained model."
HELP_N = "The name of this inference instance."
HELP_M = "Path to saved model that will be used for inference. Model must be located on one of the input or output" \
         " system shares (e.g. /mnt/input/saved_model)."

INFERENCE_TEMPLATE = 'tf-inference-stream'

log = initialize_logger(__name__)


@click.command(short_help=HELP, cls=AliasCmd, alias='l')
@click.option('-n', '--name', default=None, help=HELP_N, callback=validate_experiment_name)
@click.option('-m', '--model-location', required=True, help=HELP_M)
@common_options()
@pass_state
def launch(state: State, name: str, model_location: str):
    """
    Starts a new prediction instance that can be used for performing prediction, classification and
    regression tasks on trained model.
    """
    try:
        model_name = os.path.basename(model_location)
        name = name if name else generate_name(name=model_name)
        inference_instance = start_inference_instance(name=name, model_location=model_location, model_name=model_name)
    except Exception:
        error_message = "Failed to create prediction instance."
        log.exception(error_message)
        sys.exit(error_message)

    click.echo(tabulate({'Name': [inference_instance.name],
                         'Model Location': [model_location],
                         'Status': [inference_instance.status.value]},
                        headers=['Name', 'Model Location', 'Status'],
                        tablefmt="orgtbl"))

    try:
        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance,
                                                            model_name=model_name)
        authorization_header = get_authorization_header()
        click.echo(f'\nPrediction instance URL (append method verb manually, e.g. :predict):'
                   f'\n{inference_instance_url}')
        click.echo(f'\nAuthorize with following header:\n{authorization_header}')
    except Exception:
        error_message = "Failed to obtain prediction instance URL."
        log.exception(error_message)
        sys.exit(error_message)


def get_authorization_header():
    authorization_token = get_api_key()
    return f'Authorization: {authorization_token}'
