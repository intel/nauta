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

import click
from tabulate import tabulate


from commands.predict.common import start_inference_instance, get_inference_instance_url
from commands.experiment.common import validate_experiment_name
from platform_resources.experiments import generate_name
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.k8s.k8s_info import get_api_key
from util.system import handle_error
from cli_text_consts import PREDICT_LAUNCH_CMD_TEXTS as TEXTS


INFERENCE_TEMPLATE = 'tf-inference-stream'

logger = initialize_logger(__name__)


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='l')
@click.option('-n', '--name', default=None, help=TEXTS["help_n"], callback=validate_experiment_name)
@click.option('-m', '--model-location', required=True, help=TEXTS["help_m"])
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
        handle_error(logger, TEXTS["instance_start_error_msg"], TEXTS["instance_start_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)

    click.echo(tabulate([[inference_instance.cli_representation.name, model_location,
                          inference_instance.cli_representation.status]],
                        headers=TEXTS["table_headers"],
                        tablefmt="orgtbl"))

    try:
        inference_instance_url = get_inference_instance_url(inference_instance=inference_instance,
                                                            model_name=model_name)
        authorization_header = get_authorization_header()
        click.echo(TEXTS["instance_info_msg"].format(inference_instance_url=inference_instance_url,
                                                     authorization_header=authorization_header))
    except Exception:
        handle_error(logger, TEXTS["instance_url_error_msg"], TEXTS["instance_url_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)


def get_authorization_header():
    authorization_token = get_api_key()
    return f'Authorization: {authorization_token}'
