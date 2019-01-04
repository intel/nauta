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

import os
from typing import List, Tuple


# list of files/folders created by helm/draft
draft_files = ['.draftignore', 'dockerignore', 'Dockerfile', 'draft.toml']


def prepare_script_paramaters(script_parameters: Tuple[str, ...], script_location: str) -> List[str]:
    """
    Prepares a list of PARAMETERS based on arguments passed to a command.

    :param script_parameters: string with arguments passed to a command
    :param script_location: location of a script
    :return: list with arguments
    """
    args = [script_location]

    if script_parameters:
        for param in script_parameters:
            if "&" in param or "|" in param:
                param = f'"{param}"'
            if "\\" in param:
                # Each backslash has to be quadrupled because it has to be escaped and it goes through 2 template
                # systems.
                param = param.replace("\\", "\\\\\\\\")
            args.append(param)

    return args
