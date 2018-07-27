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

import json
import logging

from flask import Flask, Response, request
import requests

import database
from models import InactivityResponse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

redirect_to = 'http://127.0.0.1:{}/'.format('6006')


database.init_db()


@app.route('/', defaults={'url': ''})
@app.route('/<path:url>')
def proxy(url):
    new_url = url
    if request.query_string:
        new_url = new_url + '?' + request.query_string.decode('utf-8')

    headers = dict(request.headers)

    final_url = str(redirect_to + new_url)

    resp = requests.request(request.method,
                            final_url,
                            data=request.get_data(),
                            headers=headers,
                            cookies=request.cookies
                            )

    flask_resp = Response(response=resp.content, content_type=resp.headers['Content-Type'])

    flask_resp.status_code = resp.status_code

    for cookie_key, cookie_value in resp.cookies.items():
        flask_resp.set_cookie(cookie_key, value=cookie_value)

    database.update_timestamp()

    return flask_resp


@app.route('/inactivity')
def inactivity():
    timestamp = database.get_timestamp()
    response = InactivityResponse(last_request_datetime=timestamp)
    return Response(response=json.dumps(response.to_dict()), content_type='application/json')


@app.route('/healthz')
def healthz():
    resp = requests.get(redirect_to)
    flask_response = Response()
    flask_response.status_code = resp.status_code
    return flask_response
