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
