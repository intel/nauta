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

from datetime import datetime
import json
import logging as log
from typing import Optional

import dateutil.parser
import requests
import requests.exceptions


def try_get_last_request_datetime(proxy_address: str) -> Optional[datetime]:
    # sometimes proxy times out with the response and that's okay - it might be too busy with getting the last request
    # timestamp. try again shortly - it should return proper response.
    try:
        proxy_response = requests.get(f'http://{proxy_address}/inactivity', timeout=5)
    except requests.exceptions.ConnectionError:
        log.exception('connection to proxy failed')
        return None

    proxy_resonse_body = proxy_response.content.decode('utf-8')

    proxy_response_dict = json.loads(proxy_resonse_body)

    last_request_datetime_str = proxy_response_dict['lastRequestDatetime']

    last_request_datetime: datetime = dateutil.parser.parse(last_request_datetime_str)

    return last_request_datetime
