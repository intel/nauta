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
from typing import Tuple, List

import click
from tabulate import tabulate

from commands.experiment.common import validate_experiment_name, validate_pack_params_names
from commands.predict.common import start_inference_instance, INFERENCE_INSTANCE_PREFIX
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from platform_resources.experiments import generate_name
from util.system import handle_error
from cli_text_consts import PredictBatchCmdTexts as Texts


BATCH_INFERENCE_TEMPLATE = 'tf-inference-batch'

logger = initialize_logger(__name__)


def validate_local_model_location(local_model_location: str):
    if not os.path.isdir(local_model_location):
        handle_error(
            user_msg=Texts.MODEL_DIR_NOT_FOUND_ERROR_MSG.format(local_model_location=local_model_location)
        )
        exit(2)


# noinspection PyUnusedLocal

@click.command(short_help=Texts.HELP, cls=AliasCmd, alias='b', options_metavar='[options]')
@click.option('-n', '--name', help=Texts.HELP_NAME, callback=validate_experiment_name)
@click.option('-m', '--model-location', help=Texts.HELP_MODEL_LOCATION)
@click.option("-l", "--local-model-location", type=click.Path(), help=Texts.HELP_LOCAL_MODEL_LOCATION)
@click.option('-d', '--data', required=True, help=Texts.HELP_DATA)
@click.option('-o', '--output', help=Texts.HELP_OUTPUT)
@click.option('-mn', '--model-name', help=Texts.HELP_MODEL_NAME)
@click.option('-tr', '--tf-record', help=Texts.HELP_TF_RECORD,  is_flag=True)
@click.option("-p", "--pack_param", type=(str, str), multiple=True, help=Texts.HELP_P,
              callback=validate_pack_params_names)
@click.option("-r", "--requirements", type=click.Path(exists=True, dir_okay=False), required=False,
              help=Texts.HELP_REQUIREMENTS)
@common_options()
@pass_state
def batch(state: State, name: str, model_location: str, local_model_location: str, data: str, output: str,
          model_name: str, tf_record: bool, pack_param: List[Tuple[str, str]], requirements: str):
    """
    Starts a new batch instance that will perform prediction on provided data.
    """
    if not model_location and not local_model_location:
        handle_error(
            user_msg=Texts.MISSING_MODEL_LOCATION_ERROR_MSG.format(local_model_location=local_model_location)
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
                                                      output_location=output,
                                                      tf_record=tf_record,
                                                      pack_params=pack_param,
                                                      requirements=requirements)
    except Exception:
        handle_error(logger, Texts.OTHER_INSTANCE_CREATION_ERROR_MSG, Texts.OTHER_INSTANCE_CREATION_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    click.echo(tabulate({Texts.TABLE_NAME_HEADER: [inference_instance.cli_representation.name],
                         Texts.TABLE_MODEL_LOCATION_HEADER: [model_location],
                         Texts.TABLE_STATUS_HEADER: [inference_instance.cli_representation.status]},
                        headers=Texts.TABLE_HEADERS,
                        tablefmt="orgtbl"))
