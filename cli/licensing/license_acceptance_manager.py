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

from os import path
import sys

import click

from cli_text_consts import LicenseAcceptanceTexts
from util.config import Config


def save_license_accepted():
    config_dir_path = Config.get_config_path()
    if Config.validate_config_path(config_dir_path):
        open(path.join(config_dir_path, "license_accepted"), mode='a').close()
    else:
        click.echo(LicenseAcceptanceTexts.CANNOT_ACCEPT_LICENSE_MSG.format(dlsctl_config_path=config_dir_path))
        sys.exit(1)


def is_license_already_accepted() -> bool:
    config_dir_path = Config.get_config_path()
    return path.isfile(path.join(config_dir_path, "license_accepted"))


def check_license_acceptance() -> bool:
    if is_license_already_accepted():
        return True

    yes_answered: bool = click.confirm(text=LicenseAcceptanceTexts.LICENSE_ACCEPTANCE_QUESTION_MSG)

    if yes_answered:
        save_license_accepted()
        return True

    return False
