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

log.basicConfig(level=log.DEBUG)

app = Flask(__name__)


def _generate_error_response(error_code: HTTPStatus, message: str) -> (str, HTTPStatus, dict):
    response = {
        'code': error_code,
        'message': message
    }
    return json.dumps(response), error_code, {'Content-Type': 'application/json'}


@app.route('/create/<run_name>', methods=['POST'])
def create(run_name: str):
    tensb_mgr = TensorboardManager.incluster_init()

    current_tensorboard_instance = tensb_mgr.get_by_run_names([run_name])

    if current_tensorboard_instance:
        return json.dumps(current_tensorboard_instance.to_dict()), HTTPStatus.CONFLICT

    tensorboard = tensb_mgr.create(run_name)

    response = tensorboard.to_dict()

    response['DEPRECATED'] = 'This endpoint is deprecated! Use "POST /tensorboard" instead!'

    return json.dumps(response), {'Content-Type': 'application/json'}


@app.route('/tensorboard', methods=['POST'])
def create_v2():
    request_json_body = request.get_json(force=True)

    try:
        run_names = request_json_body['runNames']
    except KeyError:
        return _generate_error_response(HTTPStatus.BAD_REQUEST, "missing required 'runNames' field in request body!")

    if len(run_names) < 1:
        return _generate_error_response(HTTPStatus.BAD_REQUEST, 'at least 1 run name is needed!')

    # TODO: remove when CAN-630 is done
    if len(run_names) > 1:
        return _generate_error_response(HTTPStatus.NOT_IMPLEMENTED, 'many experiments not implemented yet!')

    run_name = run_names[0]

    tensb_mgr = TensorboardManager.incluster_init()

    current_tensorboard_instance = tensb_mgr.get_by_run_names([run_name])

    if current_tensorboard_instance:
        return json.dumps(current_tensorboard_instance.to_dict()), HTTPStatus.CONFLICT

    tensorboard = tensb_mgr.create(run_name)

    return json.dumps(tensorboard.to_dict()), HTTPStatus.ACCEPTED, {'Content-Type': 'application/json'}


@app.route('/tensorboard/<id>', methods=['GET'])
def get_v2(id: str):
    tensb_mgr = TensorboardManager.incluster_init()

    current_tensorboard_instance = tensb_mgr.get_by_id(id)

    if current_tensorboard_instance is None:
        return _generate_error_response(HTTPStatus.NOT_FOUND, 'Tensorboard instance with provided id does not exist.')

    return json.dumps(current_tensorboard_instance.to_dict()), {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
