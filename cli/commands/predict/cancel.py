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

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
import commands.experiment.cancel
from util.logger import initialize_logger
from cli_text_consts import PREDICT_CANCEL_CMD_TEXTS as TEXTS
from commands.experiment.common import RunKinds

logger = initialize_logger(__name__)


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='c')
@click.argument("name", required=False)
@click.option('-m', '--match', default=None, help=TEXTS["help_m"])
@click.option('-p', '--purge', default=None, help=TEXTS["help_p"], is_flag=True)
@common_options()
@pass_state
@click.pass_context
def cancel(context, state: State, name: str, match: str, purge: bool):
    """
    Cancels chosen prediction instances based on a name provided as a parameter.
    """
    commands.experiment.cancel.experiment_name = TEXTS["experiment_name"]
    commands.experiment.cancel.experiment_name_plural = TEXTS["experiment_name_plural"]
    context.forward(commands.experiment.cancel.cancel, listed_runs_kinds=[RunKinds.INFERENCE])
