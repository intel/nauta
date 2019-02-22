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

from http import HTTPStatus
import json
import logging as log

from flask import Flask, request

from tensorboard.tensorboard import TensorboardManager
from api.models import TensorboardCreationRequestBody, TensorboardResponse, TensorboardResponsePreconditionFailed

log.basicConfig(level=log.DEBUG)

app = Flask(__name__)

# TODO: change to decorator
CONTENT_TYPE_SLUG = {'Content-Type': 'application/json'}


def _generate_error_response(error_code: HTTPStatus, message: str) -> (str, HTTPStatus, dict):
    response = {
        'code': error_code,
        'message': message
    }
    return json.dumps(response), error_code, CONTENT_TYPE_SLUG


@app.route('/tensorboard', methods=['POST'])
def create():
    request_json_body = request.get_json(force=True)

    try:
        run_names = request_json_body['runNames']
    except (KeyError, TypeError):
        return _generate_error_response(HTTPStatus.BAD_REQUEST, "missing required 'runNames' field in request body!")

    if len(run_names) < 1:
        return _generate_error_response(HTTPStatus.BAD_REQUEST, 'at least 1 run name is needed!')

    try:
        request_body = TensorboardCreationRequestBody.from_dict(request_json_body)
    except (KeyError, TypeError):
        return _generate_error_response(HTTPStatus.BAD_REQUEST, 'incorrect request body!')

    tensb_mgr = TensorboardManager.incluster_init()

    valid_runs, invalid_runs = tensb_mgr.validate_runs(request_body.run_names)

    if not valid_runs:
        response = TensorboardResponsePreconditionFailed(code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
                                                         invalid_runs=invalid_runs)

        return json.dumps(response.to_dict()), HTTPStatus.UNPROCESSABLE_ENTITY, CONTENT_TYPE_SLUG

    current_tensorboard_instance = tensb_mgr.get_by_runs(valid_runs)

    if current_tensorboard_instance:
        response = TensorboardResponse.from_tensorboard(current_tensorboard_instance)

        if invalid_runs:
            response.invalid_runs = invalid_runs

        return json.dumps(response.to_dict()), HTTPStatus.CONFLICT, CONTENT_TYPE_SLUG

    tensorboard = tensb_mgr.create(valid_runs)

    response = TensorboardResponse.from_tensorboard(tensorboard)

    if invalid_runs:
        response.invalid_runs = invalid_runs

    return json.dumps(response.to_dict()), HTTPStatus.ACCEPTED, CONTENT_TYPE_SLUG


@app.route('/tensorboard/<id>', methods=['GET'])
def get(id: str):
    tensb_mgr = TensorboardManager.incluster_init()

    current_tensorboard_instance = tensb_mgr.get_by_id(id)

    if current_tensorboard_instance is None:
        return _generate_error_response(HTTPStatus.NOT_FOUND, 'Tensorboard instance with provided id does not exist.')

    return json.dumps(current_tensorboard_instance.to_dict()), CONTENT_TYPE_SLUG
