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

import pytest
from unittest.mock import call

from draft import cmd


@pytest.fixture
def draft_mock(mocker):
    exe_mock = mocker.patch.object(cmd, 'execute_system_command')
    exe_mock.return_value = ('some return', 0)

    return cmd


# noinspection PyShadowingNames
def test_create(draft_mock):
    draft_mock.create()

    assert draft_mock.execute_system_command.call_count == 1
    assert draft_mock.execute_system_command.call_args == call(['draft', 'create'])


# noinspection PyShadowingNames
def test_up(draft_mock):
    draft_mock.up()

    assert draft_mock.execute_system_command.call_count == 1
    assert draft_mock.execute_system_command.call_args == call(['draft', 'up'])
