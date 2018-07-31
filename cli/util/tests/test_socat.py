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
