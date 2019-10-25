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

import subprocess
import time

import pytest
from kopf.testing import KopfRunner

from nauta_resources.platform_resource import CustomResourceApiClient


@pytest.fixture(scope='function')
def unmock_k8s_api_client():
    CustomResourceApiClient.k8s_custom_object_api = None


def test_create_delete_run(unmock_k8s_api_client):
    with KopfRunner(['run', 'nauta_operator.py'], timeout=5) as runner:
        subprocess.run(['kubectl', 'apply', '-f', 'example_runs/test_run.yaml'], check=True)
        time.sleep(2)
        subprocess.run(['kubectl', 'delete', '-f', 'example_runs/test_run.yaml'], check=True)
        time.sleep(2)

    assert runner.exit_code == 0
    assert runner.exception is None
    assert 'Run test-run created.' in runner.stdout
    assert 'Run test-run deleted.' in runner.stdout
