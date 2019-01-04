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

from typing import List

from tensorboard.tensorboard import Tensorboard
from tensorboard.models import Run, TensorboardStatus


class TensorboardCreationRequestBody:
    def __init__(self, run_names: List[Run]):
        self.run_names = run_names

    @classmethod
    def from_dict(cls, body):
        runs_from_json = body['runNames']
        runs = []
        for json_run in runs_from_json:
            name = json_run['name']
            owner = json_run['owner']
            new_run = Run(name=name, owner=owner)
            runs.append(new_run)

        return cls(run_names=runs)


class TensorboardResponse:
    def __init__(self, id: str, status: TensorboardStatus, url: str, invalid_runs: List[Run] = None):
        self.id = id
        self.status = status
        self.url = url
        self.invalid_runs = invalid_runs

    def to_dict(self):
        tb_dict = {
            'id': self.id,
            'status': self.status.value,
            'url': self.url
        }

        if self.invalid_runs:
            runs = []
            for run in self.invalid_runs:
                runs.append(run.to_dict())

            tb_dict['invalidRuns'] = runs

        return tb_dict

    @classmethod
    def from_tensorboard(cls, tb: Tensorboard):
        return cls(id=tb.id, status=tb.status, url=tb.url)


class TensorboardResponsePreconditionFailed:
    def __init__(self, code: int, invalid_runs: List[Run]):
        self.code = code
        self.invalid_runs = invalid_runs

    def to_dict(self):
        initial = {
            'code': self.code
        }

        invalid_runs_dict = []

        for run in self.invalid_runs:
            invalid_runs_dict.append(run.to_dict())

        initial['invalidRuns'] = invalid_runs_dict

        return initial
