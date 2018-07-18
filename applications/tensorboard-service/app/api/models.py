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
