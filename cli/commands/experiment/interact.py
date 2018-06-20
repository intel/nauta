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

HELP = "Launches a local browser with Jupyter Notebook. If the script name argument " \
       "is given, then script is put into the opened notebook."
HELP_N = "The name of this Jupyter Notebook session."


@click.command(short_help=HELP, cls=AliasCmd, alias='i')
@click.argument("script_name", default="")
@click.option('-n', '--name', default=None, help=HELP_N)
@common_options()
@pass_state
def interact(state: State, script_name: str, name: str):
    """
    Starts an interactive session with Jupyter Notebook.
    """
    click.echo("Interact command - under development")
