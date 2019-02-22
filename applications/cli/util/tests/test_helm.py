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

import util.helm
from util.helm import install_helm_chart


def test_install_helm_chart(mocker):
    mocker.patch('os.environ.copy', return_value={'PATH': ''})
    mocker.patch('util.helm.execute_system_command', return_value=("", 0, ""))

    install_helm_chart('/home/user/fake_chart')

    assert util.helm.execute_system_command.call_count == 1


def test_install_helm_chart_error(mocker):
    mocker.patch('os.environ.copy', return_value={'PATH': ''})
    mocker.patch('util.helm.execute_system_command', return_value=("", 1, ""))

    with pytest.raises(RuntimeError):
        install_helm_chart('/home/user/fake_chart')

    assert util.helm.execute_system_command.call_count == 1
