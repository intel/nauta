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

from docker.errors import NotFound
import pytest

from util import socat


@pytest.fixture
def socat_mocked(mocker):
    mocker.patch.object(socat, 'client')
    mocker.patch.object(socat, 'sleep')

    return socat


def test_start(mocker, socat_mocked):
    mocker.patch.object(socat_mocked, '_ensure_socat_running')
    mocker.patch.object(socat_mocked, 'load_socat_image')

    socat_mocked.start('whatever')

    # noinspection PyProtectedMember
    assert socat_mocked._ensure_socat_running.call_count == 1
    assert socat_mocked.client.containers.run.call_count == 1


def test_ensure_socat_running(mocker, socat_mocked):
    mocker.patch.object(socat_mocked.client.containers, 'get').return_value = mocker.MagicMock(status='running')

    # noinspection PyProtectedMember
    socat_mocked._ensure_socat_running()

    # noinspection PyUnresolvedReferences
    assert socat_mocked.sleep.call_count == 0


def test_ensure_socat_running_some_wait(mocker, socat_mocked):
    mocker.patch.object(socat_mocked.client.containers, 'get').side_effect = [NotFound('not found'),
                                                                              NotFound('not found'),
                                                                              mocker.MagicMock(status='creating'),
                                                                              mocker.MagicMock(status='creating'),
                                                                              mocker.MagicMock(status='creating'),
                                                                              mocker.MagicMock(status='running')]

    # noinspection PyProtectedMember
    socat_mocked._ensure_socat_running()

    # noinspection PyUnresolvedReferences
    assert socat_mocked.sleep.call_count == 5


def test_ensure_socat_running_never_running(mocker, socat_mocked):
    mocker.patch.object(socat_mocked.client.containers, 'get').return_value = mocker.MagicMock(status='creating')

    with pytest.raises(RuntimeError):
        # noinspection PyProtectedMember
        socat_mocked._ensure_socat_running()
