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

from http import HTTPStatus
from enum import Enum
from typing import Dict, List, Optional

import json
import requests

from cli_text_consts import TensorboardClientTexts as Texts


class TensorboardServiceAPIException(Exception):
    def __init__(self, error_code: int, message: str):
        super().__init__(message)

        self.error_code = error_code


class TensorboardStatus(Enum):
    CREATING = 'CREATING'
    RUNNING = 'RUNNING'


class Tensorboard:
    def __init__(self, id: str, status: TensorboardStatus, url: str, invalid_runs: List[str]):
        self.id = id
        self.status = status
        self.url = url
        self.invalid_runs = invalid_runs

    @classmethod
    def from_dict(cls, tensorboard_dict: Dict[str, str]):
        id = tensorboard_dict['id']
        status = TensorboardStatus(tensorboard_dict['status'].upper())
        url = tensorboard_dict['url']
        invalid_runs = tensorboard_dict.get('invalidRuns')
        return cls(id, status, url, invalid_runs)


class TensorboardRun:
    def __init__(self, name: str, owner: str):
        self.name = name
        self.owner = owner

    def to_dict(self) -> Dict[str, str]:
        return {
            'name': self.name,
            'owner': self.owner
        }


class TensorboardCreationRequest:
    def __init__(self, tr_list: List[TensorboardRun]):
        self.runs = tr_list

    def to_dict(self) -> dict:
        result = {
            'runNames': []
        }
        for run in self.runs:
            result['runNames'].append(run.to_dict())
        return result


class TensorboardServiceAPIErrorResponse:
    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message

    @classmethod
    def from_dict(cls, error_dict: Dict):
        code = error_dict['code']
        message = error_dict['message']
        return cls(error_code=code, message=message)


class TensorboardServiceClient:
    def __init__(self, address: str):
        self.address = address

    def get_tensorboard(self, tensorboard_id: str) -> Optional[Tensorboard]:
        response = requests.get(self.address + "/tensorboard/" + tensorboard_id)
        if response.status_code == HTTPStatus.OK:
            response_body = json.loads(response.content.decode('utf-8'))

            tensorboard = Tensorboard.from_dict(tensorboard_dict=response_body)

            return tensorboard
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return None
        else:
            response_body = json.loads(response.content.decode('utf-8'))

            error = TensorboardServiceAPIErrorResponse.from_dict(response_body)

            raise TensorboardServiceAPIException(error_code=error.error_code, message=error.message)

    def create_tensorboard(self, runs: List[TensorboardRun]) -> Tensorboard:
        request = TensorboardCreationRequest(runs)

        response = requests.post(self.address + '/tensorboard', json=request.to_dict())
        if response.status_code in (HTTPStatus.ACCEPTED, HTTPStatus.CONFLICT):
            response_body = json.loads(response.content.decode('utf-8'))
            tensorboard = Tensorboard.from_dict(tensorboard_dict=response_body)
            return tensorboard
        elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            response_body = json.loads(response.content.decode('utf-8'))
            if response_body.get('invalidRuns'):
                list_of_invalid_runs = ', '.join([f'{item.get("owner")}/{item.get("name")}'
                                                  for item in response_body.get('invalidRuns')])
                err_message = Texts.INVALID_RUNS_ERROR_MSG.format(invalid_runs_list=list_of_invalid_runs)
            else:
                err_message = Texts.RUNS_NOT_EXIST_ERROR_MSG
            raise TensorboardServiceAPIException(error_code=response.status_code, message=err_message)
        else:
            response_body = json.loads(response.content.decode('utf-8'))
            error = TensorboardServiceAPIErrorResponse.from_dict(response_body)
            raise TensorboardServiceAPIException(error_code=error.error_code, message=error.message)


def build_tensorboard_run_list(exp_list: List[str], current_namespace: str) -> List[TensorboardRun]:
    ret_list = []

    for item in exp_list:
        split_experiment = item.split("/", 1)

        if len(split_experiment) == 1:
            ret_list.append(TensorboardRun(name=split_experiment[0], owner=current_namespace))
        else:
            ret_list.append(TensorboardRun(name=split_experiment[1], owner=split_experiment[0]))

    return ret_list
