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

from enum import Enum
from typing import Pattern, List

from platform_resources.run_model import RunStatus


def filter_by_name_regex(resource_object_dict: dict, name_regex: Pattern = None, spec_location: bool = True):
    if spec_location:
        rod = resource_object_dict['spec']['name']
    else:
        rod = resource_object_dict['metadata']['name']

    return name_regex.search(rod) if name_regex else True


def filter_by_state(resource_object_dict: dict, state: Enum = None):
    return resource_object_dict['spec']['state'] == state.value if state else True


def filter_run_by_state(resource_object_dict: dict, state: Enum = None):
    if not state:
        return True

    current_state = resource_object_dict['spec'].get('state')

    if current_state:
        return current_state == state.value
    else:
        if state == RunStatus.CREATING:
            return True
        else:
            return False


def filter_by_excl_state(resource_object_dict: dict, state: Enum = None):
    return resource_object_dict['spec']['state'] != state.value if state else True


def filter_run_by_excl_state(resource_object_dict: dict, state: Enum = None):
    if not state:
        return True

    return not filter_run_by_state(resource_object_dict, state)


def filter_by_experiment_name(resource_object_dict: dict, exp_name: str = None):
    return resource_object_dict['spec']['experiment-name'] == exp_name if exp_name else True


def filter_by_run_kinds(resource_object_dict: dict, run_kinds: List[Enum] = None):
    return any([resource_object_dict['metadata']['labels']['runKind'] == run_kind.value for run_kind in run_kinds]) \
        if run_kinds else True
