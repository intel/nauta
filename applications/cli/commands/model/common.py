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

from collections import namedtuple
from enum import Enum

from typing import List
import yaml

from util.config import Config
from util.logger import initialize_logger

MODEL_HEADERS = ['Operation', 'Start date', 'End date', 'Owner', 'State']
STEP_HEADERS = ['Name', 'Start date', 'End date', 'State']

EXPORT_LIST_HEADERS = ['Name']
PROCESS_LIST_HEADERS = ['Name']

PROCESS_WORKFLOWS_LOCATION = 'workflows/processes'
EXPORT_WORKFLOWS_LOCATION = 'workflows/exports'

workflow_description = namedtuple('Description', ['name'])

logger = initialize_logger(__name__)


class PodPhase(Enum):
    Pending = 'Pending'
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'
    Unknown = 'Unknown'


def get_list_of_workflows(location: str) -> List[workflow_description]:
    path = os.path.join(Config().config_path, location)

    list_of_workflows = []
    for name in os.listdir(path):
        description = format_workflow_description(os.path.join(path, name))
        list_of_workflows.append(description)

    return list_of_workflows


def format_workflow_description(filename: str) -> workflow_description:
    with open(filename, mode='r', encoding='utf-8') as workflow_content_file:
        workflow_content = yaml.safe_load(workflow_content_file) or {}

        name = workflow_content.get('metadata', {}).get('generateName')

        return workflow_description(name=name)
