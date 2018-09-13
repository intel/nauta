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

import base64
import os
from sys import exit

import click
from tabulate import tabulate

from commands.predict.common import start_inference_instance, get_inference_instance_url, INFERENCE_INSTANCE_PREFIX
from commands.experiment.common import validate_experiment_name
from platform_resources.experiments import generate_name
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import PREDICT_LAUNCH_CMD_TEXTS as TEXTS
from util.k8s.k8s_info import get_secret, get_kubectl_current_context_namespace, get_service_account


INFERENCE_TEMPLATE = 'tf-inference-stream'

logger = initialize_logger(__name__)


def validate_local_model_location(local_model_location: str):
    if not os.path.isdir(local_model_location):
        handle_error(
            user_msg=TEXTS["model_dir_not_found_error_msg"].format(local_model_location=local_model_location)
        )
        exit(2)


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='l')
@click.option('-n', '--name', default=None, help=TEXTS["help_n"], callback=validate_experiment_name)
@click.option('-m', '--model-location', help=TEXTS["help_m"])
@click.option("-l", "--local_model_location", type=click.Path(), help=TEXTS["help_local_model_location"])
@common_options()
@pass_state
def launch(state: State, name: str, model_location: str, local_model_location: str):
    """
    Starts a new prediction instance that can be used for performing prediction, classification and
    regression tasks on trained model.
    """
    if not model_location and not local_model_location:
        handle_error(
            user_msg=TEXTS["missing_model_location_error_msg"].format(local_model_location=local_model_location)
        )
        exit(1)

    if local_model_location:
        validate_local_model_location(local_model_location)

    click.echo('Submitting prediction instance.')
    try:
        model_name = os.path.basename(model_location)
        name = name if name else generate_name(name=model_name, prefix=INFERENCE_INSTANCE_PREFIX)
        inference_instance = start_inference_instance(name=name, model_location=model_location, model_name=model_name,
                                                      local_model_location=local_model_location)
    except Exception:
        handle_error(logger, TEXTS["instance_start_error_msg"], TEXTS["instance_start_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo(tabulate([[inference_instance.cli_representation.name, model_location,
                          inference_instance.cli_representation.status]],
                        headers=TEXTS["table_headers"],
                        tablefmt="orgtbl"))

    try:
        namespace = get_kubectl_current_context_namespace()
        authorization_header = get_authorization_header(service_account_name=name, namespace=namespace)
        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance,
                                                            model_name=model_name)
        click.echo(TEXTS["instance_info_msg"].format(inference_instance_url=inference_instance_url,
                                                     authorization_header=authorization_header))
    except Exception:
        handle_error(logger, TEXTS["instance_url_error_msg"], TEXTS["instance_url_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)


def get_authorization_header(service_account_name: str, namespace: str):
    service_account = get_service_account(service_account_name=service_account_name, namespace=namespace)
    secret_name = service_account.secrets[0].name
    authorization_token = get_secret(secret_name=secret_name, namespace=namespace).data['token']
    authorization_token = base64.b64decode(authorization_token).decode('utf-8')
    return f'Authorization: Bearer {authorization_token}'
