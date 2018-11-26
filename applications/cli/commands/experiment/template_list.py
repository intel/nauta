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

import sys

import click
from tabulate import tabulate

from commands.experiment.common import RUN_TEMPLATE_NAME, get_list_of_packs
from cli_state import common_options
from util.aliascmd import AliasCmd
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import ExperimentTemplateListCmdTexts as Texts


log = initialize_logger('commands.template_list')

CHART_YAML_FILENAME = "Chart.yaml"
TEMPL_FOLDER_NAME = "templates"


@click.command("template_list", short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='t',
               options_metavar='[options]')
@common_options()
def template_list():
    list_of_packs = get_list_of_packs()

    if list_of_packs:
        click.echo(tabulate([[row] for row in list_of_packs],
                            headers=[RUN_TEMPLATE_NAME],
                            tablefmt="orgtbl"))
    else:
        handle_error(user_msg=Texts.LACK_OF_PACKS_ERROR_MSG)
        sys.exit(1)
