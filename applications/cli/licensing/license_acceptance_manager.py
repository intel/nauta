#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        click.echo(LicenseAcceptanceTexts.CANNOT_ACCEPT_LICENSE_MSG.format(nctl_config_path=config_dir_path))
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
