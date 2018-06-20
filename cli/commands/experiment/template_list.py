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

from util.aliascmd import AliasCmd
from draft.cmd import DRAFT_HOME_FOLDER
from util.config import Config
from util.logger import initialize_logger

log = initialize_logger('commands.template_list')

HELP = "Returns a list of available templates that can be used to submit training jobs."

CHART_YAML_FILENAME = "Chart.yaml"
TEMPL_FOLDER_NAME = "templates"


@click.command(short_help=HELP, cls=AliasCmd, alias='t')
def template_list():
    path = os.path.join(Config().config_path, DRAFT_HOME_FOLDER, "packs")

    list_of_packs = []
    for (dirpath, dirnames, filenames) in os.walk(path):

        if CHART_YAML_FILENAME in filenames and TEMPL_FOLDER_NAME in dirnames:
            pack_name = os.path.split(os.path.split(dirpath)[0])[1]
            list_of_packs.append(pack_name)

    if list_of_packs:
        click.echo(tabulate([[row] for row in list_of_packs],
                            headers=["Template name"],
                            tablefmt="orgtbl"))
    else:
        click.echo("Lack of installed packs.")
        sys.exit(1)
