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
import urllib3

import click

from commands import submit
from commands import verify
from commands import logs
from commands import list
from commands import view
from commands import cancel
from commands import version
from commands import interact
from commands import predict
from commands import launch
from util.config import Config, Fields
from commands import template_list


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
DEFAULT_LANG = "en_US.UTF-8"


@click.group(context_settings=CONTEXT_SETTINGS)
def entry_point():
    Config.set(Fields.CONFIG_PATH, verify.validate_config_path())


entry_point.add_command(submit.submit)
entry_point.add_command(verify.verify)
entry_point.add_command(launch.launch)
entry_point.add_command(logs.logs)
entry_point.add_command(template_list.template_list)
entry_point.add_command(list.list)
entry_point.add_command(view.view)
entry_point.add_command(cancel.cancel)
entry_point.add_command(version.version)
entry_point.add_command(interact.interact)
entry_point.add_command(predict.predict)

if __name__ == '__main__':
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        entry_point()
    except RuntimeError:
        os.environ["LC_ALL"] = DEFAULT_LANG
        os.environ["LANG"] = DEFAULT_LANG
        entry_point()
