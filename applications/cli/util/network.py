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

import requests
import time


def wait_for_connection(url, retries=10, timeout=1) -> bool:
    while retries:
        try:
            response = requests.get(url)
            return int(response.status_code / 100) == 2
        except requests.exceptions.ConnectionError:
            retries = retries - 1
            time.sleep(timeout)
    return False
