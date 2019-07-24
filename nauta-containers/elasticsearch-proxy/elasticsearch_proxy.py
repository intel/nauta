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

from flask import Flask
from flask import Response
from flask import request

import requests

import base64
from subprocess import check_output


app = Flask(__name__)

ELASTICSEARCH_PORT = 9200
ip = check_output(['hostname', '--all-ip-addresses']).decode("ascii").split('\n')[0].strip()
REDIRECT_TO = f'http://{ip}:{ELASTICSEARCH_PORT}/'
ADMIN_KEY = base64.b64encode(
    open("/var/es-proxy-auth/token").read().encode("ascii")).decode("ascii")


def create_flask_response(original_response):
    flask_response = Response(
        response=original_response.content,
        content_type=original_response.headers['content-type'])

    flask_response.status_code = original_response.status_code

    for cookie_key, cookie_value in original_response.cookies.items():
        flask_response.set_cookie(cookie_key, value=cookie_value)

    return flask_response


def is_gui_search_scroll_request(url, request):
    return request.method == "POST" \
           and (url == "_all/_search" or url == "_all/scroll"
                or url == "_search/scroll")


@app.route('/', methods=['GET', 'POST', 'DELETE', 'PUT', 'HEAD'])
@app.route('/<path:url>', methods=['GET', 'POST', 'DELETE', 'PUT', 'HEAD'])
def redirect(url=""):
    new_url = url
    if request.query_string:
        new_url = new_url + '?' + request.query_string.decode("ascii")

    headers = dict(request.headers)

    if (
        not is_gui_search_scroll_request(url, request)
        and request.method != "GET"
        and (headers.get("ES-Authorization") != f"Basic {ADMIN_KEY}"
             and headers.get("Authorization") != f"Basic {ADMIN_KEY}")
    ):
        return "", 403

    response = requests.request(
        request.method,
        str(REDIRECT_TO + new_url),
        data=request.get_data(),
        headers=headers,
        cookies=request.cookies)

    return create_flask_response(response)
