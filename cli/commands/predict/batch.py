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
from sys import exit

import click
from tabulate import tabulate

from commands.experiment.common import validate_experiment_name
from commands.predict.common import start_inference_instance, INFERENCE_INSTANCE_PREFIX
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from platform_resources.experiments import generate_name
from util.system import handle_error
from cli_text_consts import PREDICT_BATCH_CMD_TEXTS as TEXTS


BATCH_INFERENCE_TEMPLATE = 'tf-inference-batch'

logger = initialize_logger(__name__)


def validate_local_model_location(local_model_location: str):
    if not os.path.isdir(local_model_location):
        handle_error(
            user_msg=TEXTS["model_dir_not_found_error_msg"].format(local_model_location=local_model_location)
        )
        exit(2)


# noinspection PyUnusedLocal
@click.command(short_help=TEXTS["help"], cls=AliasCmd, alias='b')
@click.option('-n', '--name', help=TEXTS["help_name"], callback=validate_experiment_name)
@click.option('-m', '--model-location', help=TEXTS["help_model_location"])
@click.option("-l", "--local_model_location", type=click.Path(), help=TEXTS["help_local_model_location"])
@click.option('-d', '--data', required=True, help=TEXTS["help_data"])
@click.option('-o', '--output', help=TEXTS["help_output"])
@click.option('-mn', '--model-name', help=TEXTS["help_model_name"])
@common_options()
@pass_state
def batch(state: State, name: str, model_location: str, local_model_location: str, data: str, output: str,
          model_name: str):
    """
    Starts a new batch instance that will perform prediction on provided data.
    """
    if not model_location and not local_model_location:
        handle_error(
            user_msg=TEXTS["missing_model_location_error_msg"].format(local_model_location=local_model_location)
        )
        exit(1)

    if local_model_location:
        validate_local_model_location(local_model_location)

    # noinspection PyBroadException
    try:
        model_name = model_name if model_name else os.path.basename(model_location)
        name = name if name else generate_name(name=model_name, prefix=INFERENCE_INSTANCE_PREFIX)
        inference_instance = start_inference_instance(name=name, model_location=model_location,
                                                      local_model_location=local_model_location, model_name=model_name,
                                                      template=BATCH_INFERENCE_TEMPLATE, data_location=data,
                                                      output_location=output)
    except Exception:
        handle_error(logger, TEXTS["other_instance_creation_error_msg"], TEXTS["other_instance_creation_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo(tabulate({TEXTS["table_name_header"]: [inference_instance.cli_representation.name],
                         TEXTS["table_model_location_header"]: [model_location],
                         TEXTS["table_status_header"]: [inference_instance.cli_representation.status]},
                        headers=TEXTS["table_headers"],
                        tablefmt="orgtbl"))
