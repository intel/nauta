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
from typing import List, Tuple


# list of files/folders created by helm/draft
draft_files = ['.draftignore', 'dockerignore', 'Dockerfile', 'draft.toml']


def prepare_script_paramaters(script_parameters: Tuple[str, ...], script_location: str,
                              script_name_as_a_first_element: bool=True) -> List[str]:
    """
    Prepares a list of PARAMETERS based on arguments passed to a command.

    :param script_parameters: string with arguments passed to a command
    :param script_location: location of a script
    :param script_name_as_a_first_element: if True - name of a script is a first element of
                    an array returned by the function
    :return: list with arguments
    """
    if "/" in script_location:
        script_filename = script_location.split("/")[-1]
    else:
        script_filename = script_location

    args = []

    if script_name_as_a_first_element:
        args.append(script_filename)

    if script_parameters:
        args.extend(list(script_parameters))

    return args
