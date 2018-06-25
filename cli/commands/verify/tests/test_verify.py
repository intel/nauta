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

from click.testing import CliRunner

from commands.verify import verify
from util.exceptions import KubectlConnectionError


def test_verify_with_kubectl_connection_error(mocker):
    mocker.patch("cli_state.verify_cli_config_path")
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_connection_mock.side_effect = KubectlConnectionError
    check_dependency_mock = mocker.patch.object(verify, "check_dependency")

    runner = CliRunner()
    runner.invoke(verify.verify, [])

    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    assert check_dependency_mock.call_count == 0, "dependency was checked"


def test_verify_with_kubectl_connection_success(mocker):
    mocker.patch("cli_state.verify_cli_config_path")
    check_connection_mock = mocker.patch.object(verify, "check_connection_to_cluster")
    check_dependency_mock = mocker.patch.object(verify, "check_dependency")

    runner = CliRunner()
    runner.invoke(verify.verify, [])

    assert check_connection_mock.call_count == 1, "connection wasn't checked"
    assert check_dependency_mock.call_count != 0, "dependency was checked"
