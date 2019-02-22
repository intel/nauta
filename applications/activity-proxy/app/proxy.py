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
