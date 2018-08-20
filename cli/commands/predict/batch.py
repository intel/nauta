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
from commands.predict.common import start_inference_instance
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from platform_resources.experiments import generate_name

HELP = "Uses specified dataset to perform inference. Results stored in output file"
HELP_DATA = "location of a folder with data that will be used to perform the batch inference. Value should points " \
            "out the location from one of the system's shares."
HELP_MODEL_LOCATION = "Path to saved model that will be used for inference. Model must be located on one of the " \
                      "input or output system shares (e.g. /mnt/input/saved_model)."
HELP_MODEL_NAME = "Name of a model passed as a servable name. By default it is the name of directory in model's " \
                  "location."
HELP_NAME = "name of a predict session"
HELP_OUTPUT = "location of a folder where outputs from inferences will be stored. Value should points out the " \
              "location from one of the system's shares."

BATCH_INFERENCE_TEMPLATE = 'tf-inference-batch'

log = initialize_logger(__name__)


# noinspection PyUnusedLocal
@click.command(short_help=HELP, cls=AliasCmd, alias='b')
@click.option('-n', '--name', help=HELP_NAME, callback=validate_experiment_name)
@click.option('-m', '--model-location', required=True, help=HELP_MODEL_LOCATION)
@click.option('-d', '--data', required=True, help=HELP_DATA)
@click.option('-o', '--output', help=HELP_OUTPUT)
@click.option('-mn', '--model-name', help=HELP_MODEL_NAME)
@common_options()
@pass_state
def batch(state: State, name: str, model_location: str, data: str, output: str, model_name: str):
    """
    Starts a new batch instance that will perform prediction on provided data.
    """
    # noinspection PyBroadException
    try:
        model_name = model_name if model_name else os.path.basename(model_location)
        name = name if name else generate_name(name=model_name)
        inference_instance = start_inference_instance(name=name, model_location=model_location, model_name=model_name,
                                                      template=BATCH_INFERENCE_TEMPLATE, data_location=data,
                                                      output_location=output)
    except Exception:
        error_message = "Failed to create batch prediction instance."
        log.exception(error_message)
        sys.exit(error_message)

    click.echo(tabulate({'Name': [inference_instance.name],
                         'Model Location': [model_location],
                         'Status': [inference_instance.status.value]},
                        headers=['Name', 'Model Location', 'Status'],
                        tablefmt="orgtbl"))
