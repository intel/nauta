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

from commands.experiment import list, cancel, logs, view, template_list, submit, interact
from util.logger import initialize_logger
from util.aliascmd import AliasGroup

logger = initialize_logger(__name__)

HELP = "Command for training and managing training jobs"


@click.group(short_help=HELP, cls=AliasGroup, alias='exp')
def experiment():
    pass


experiment.add_command(cancel.cancel)
experiment.add_command(submit.submit)
experiment.add_command(list.list_experiments)
experiment.add_command(logs.logs)
experiment.add_command(interact.interact)
experiment.add_command(view.view)
experiment.add_command(template_list.template_list)
