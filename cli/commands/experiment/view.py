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


HELP = "Displays basic details of experiment with a given name."
HELP_T = "If given - exposes a tensorboard's instance with exepriment's data."


@click.command(help=HELP, cls=AliasCmd, alias='v')
@click.argument("experiment_name")
@click.option('-tb', '--tensorboard', default=None, help=HELP_T, is_flag=True)
@common_options
@pass_state
def view(state: State, experiment_name: str, tensorboard: bool):
    """
    Displays details of an experiment.
    """
    click.echo("View command - under development")
