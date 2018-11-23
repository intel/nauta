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

import click

from commands.predict import launch, list, cancel, stream, batch
from util.logger import initialize_logger
from util.aliascmd import AliasGroup
from cli_text_consts import PredictCmdTexts as Texts


logger = initialize_logger(__name__)


@click.group(short_help=Texts.HELP, cls=AliasGroup, alias='p', help=Texts.HELP,
             subcommand_metavar="COMMAND [options] [args]...")
def predict():
    pass


predict.add_command(cancel.cancel)
predict.add_command(launch.launch)
predict.add_command(list.list_inference_instances)
predict.add_command(stream.stream)
predict.add_command(batch.batch)
