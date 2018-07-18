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
