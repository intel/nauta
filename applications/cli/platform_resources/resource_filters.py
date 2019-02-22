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

from enum import Enum
from typing import Pattern, List


def filter_by_name_regex(resource_object_dict: dict, name_regex: Pattern = None, spec_location: bool = True):
    if spec_location:
        rod = resource_object_dict['spec']['name']
    else:
        rod = resource_object_dict['metadata']['name']

    return name_regex.search(rod) if name_regex else True


def filter_by_state(resource_object_dict: dict, state: Enum = None):
    return resource_object_dict['spec']['state'] == state.value if state else True


def filter_by_excl_state(resource_object_dict: dict, state: Enum = None):
    return resource_object_dict['spec']['state'] != state.value if state else True


def filter_by_experiment_name(resource_object_dict: dict, exp_name: List[str] = None):
    return resource_object_dict['spec']['experiment-name'] in exp_name if exp_name else True


