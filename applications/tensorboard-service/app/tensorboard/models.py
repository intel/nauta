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
from typing import Dict


class TensorboardStatus(Enum):
    CREATING = 'CREATING'
    RUNNING = 'RUNNING'


class Tensorboard:
    def __init__(self, id: str, status: TensorboardStatus = TensorboardStatus.CREATING, url: str = ''):
        self.id = id
        self.status = status
        self.url = url

    def to_dict(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'status': self.status.value,
            'url': self.url
        }


class Run:
    def __init__(self, name: str, owner: str):
        self.name = name
        self.owner = owner

    def to_dict(self):
        return {
            'name': self.name,
            'owner': self.owner
        }
